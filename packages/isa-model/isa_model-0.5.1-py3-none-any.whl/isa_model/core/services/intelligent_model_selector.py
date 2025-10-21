#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Intelligent Model Selector - Embedding-based model selection
Uses embedding similarity matching against model descriptions and metadata
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

from ..database.supabase_client import get_supabase_client, get_supabase_table
from ...inference.ai_factory import AIFactory


class IntelligentModelSelector:
    """
    Intelligent model selector using embedding similarity
    
    Features:
    - Reads models from database registry
    - Uses unified Supabase client
    - Uses existing embedding service for similarity matching
    - Has default models for each service type
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.supabase_client = None
        self.embedding_service = None
        self.nlp = None  # spaCy NLP model
        self.models_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Default models for each service type (updated to GPT-5-nano for best cost/performance)
        self.default_models = {
            "vision": {"model_id": "gpt-5-mini", "provider": "openai"},
            "audio": {"model_id": "whisper-1", "provider": "openai"},
            "text": {"model_id": "gpt-5-nano", "provider": "openai"},  # Primary: 50% cheaper than gpt-4.1-nano
            "image": {"model_id": "black-forest-labs/flux-schnell", "provider": "replicate"},
            "embedding": {"model_id": "text-embedding-3-small", "provider": "openai"},
            "omni": {"model_id": "gpt-5", "provider": "openai"}
        }
        
        # Rate limit fallback: same models with different providers
        self.rate_limit_fallbacks = {
            "text": {"model_id": "gpt-5-nano", "provider": "yyds"},  # Same model, yyds provider
            "vision": {"model_id": "gpt-5-mini", "provider": "yyds"},
            "omni": {"model_id": "gpt-5", "provider": "yyds"}
        }
        
        # Entity-based model mappings
        self.entity_model_mappings = {
            # Domain-specific mappings
            "medical": {"preferred_models": ["microsoft/BioGPT", "medalpaca/medalpaca-7b"]},
            "legal": {"preferred_models": ["saul-7b", "legal-bert"]},
            "financial": {"preferred_models": ["ProsusAI/finbert", "financialbert"]},
            "scientific": {"preferred_models": ["microsoft/DialoGPT-medium", "allenai/scibert"]},
            "code": {"preferred_models": ["microsoft/CodeBERT", "codeparrot/codeparrot"]},
            
            # Task-specific mappings
            "translation": {"preferred_models": ["facebook/m2m100", "google/mt5"]},
            "summarization": {"preferred_models": ["facebook/bart-large", "google/pegasus"]},
            "question_answering": {"preferred_models": ["deepset/roberta-base-squad2", "distilbert-base-uncased-distilled-squad"]},
            "sentiment": {"preferred_models": ["cardiffnlp/twitter-roberta-base-sentiment", "nlptown/bert-base-multilingual-uncased-sentiment"]},
            
            # Language-specific mappings
            "chinese": {"preferred_models": ["THUDM/chatglm2-6b", "baichuan-inc/Baichuan2-7B-Chat"]},
            "japanese": {"preferred_models": ["rinna/japanese-gpt2-medium", "sonoisa/sentence-bert-base-ja-mean-tokens"]},
            "multilingual": {"preferred_models": ["facebook/mbart-large-50", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]}
        }
        
        logger.info("Intelligent Model Selector initialized")
    
    async def initialize(self):
        """Initialize the model selector"""
        try:
            # Initialize Supabase client
            self.supabase_client = get_supabase_client()
            logger.info("Supabase client initialized")
            
            # Initialize embedding service
            await self._init_embedding_service()
            
            # Initialize spaCy NLP
            await self._init_spacy_nlp()
            
            # Load models from database
            await self._load_models_from_database()
            
            logger.info("Model selector fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize model selector: {e}")
            # Continue with fallback mode
    
    async def _init_embedding_service(self):
        """Initialize embedding service for text similarity"""
        try:
            factory = AIFactory.get_instance()
            self.embedding_service = factory.get_embed("text-embedding-3-small", "openai")
            logger.info("Embedding service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}")
    
    async def _init_spacy_nlp(self):
        """Initialize spaCy NLP model for entity extraction"""
        try:
            import spacy
            
            # Try to load the English model
            models_to_try = ["en_core_web_sm", "en_core_web_md", "en_core_web_lg"]
            
            for model_name in models_to_try:
                try:
                    self.nlp = spacy.load(model_name)
                    logger.info(f"spaCy model '{model_name}' loaded successfully")
                    break
                except OSError:
                    logger.warning(f"spaCy model '{model_name}' not found")
                    continue
            
            if not self.nlp:
                # Try to download the smallest model automatically
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python", "-m", "spacy", "download", "en_core_web_sm"],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minutes timeout
                    )
                    
                    if result.returncode == 0:
                        self.nlp = spacy.load("en_core_web_sm")
                        logger.info("spaCy en_core_web_sm downloaded and loaded successfully")
                    else:
                        logger.warning(f"Failed to download spaCy model: {result.stderr}")
                        
                except Exception as download_error:
                    logger.warning(f"Failed to download spaCy model: {download_error}")
            
            # If still no model, create a blank model with NER
            if not self.nlp:
                logger.warning("No spaCy model available, creating blank model with NER")
                self.nlp = spacy.blank("en")
                # Add basic NER component
                try:
                    self.nlp.add_pipe("ner")
                except:
                    pass  # NER might not be available in blank model
                    
        except ImportError:
            # spaCy not available, will use regex fallback
            self.nlp = None
        except Exception as e:
            # Failed to init spaCy, will use regex fallback
            self.nlp = None
    
    def extract_entities_and_keywords(self, text: str) -> Dict[str, Any]:
        """Extract entities and keywords from text using spaCy and heuristics"""
        try:
            entities_info = {
                "domains": set(),
                "tasks": set(),
                "languages": set(),
                "technical_terms": set(),
                "named_entities": {},
                "keywords": set()
            }
            
            # Use spaCy if available
            if self.nlp:
                try:
                    doc = self.nlp(text)
                    
                    # Extract named entities
                    for ent in doc.ents:
                        label = ent.label_
                        if label not in entities_info["named_entities"]:
                            entities_info["named_entities"][label] = []
                        entities_info["named_entities"][label].append(ent.text)
                    
                    # Extract noun phrases as potential keywords
                    for chunk in doc.noun_chunks:
                        entities_info["keywords"].add(chunk.text.lower())
                        
                except Exception as e:
                    logger.warning(f"spaCy processing failed: {e}")
            
            # Heuristic-based extraction
            text_lower = text.lower()
            
            # Domain detection
            domain_keywords = {
                "medical": ["medical", "health", "doctor", "patient", "diagnosis", "treatment", "clinical", "healthcare", "hospital", "medicine", "drug"],
                "legal": ["legal", "law", "court", "lawyer", "attorney", "contract", "litigation", "compliance", "regulation", "statute"],
                "financial": ["financial", "finance", "banking", "investment", "trading", "market", "stock", "currency", "economic", "accounting"],
                "scientific": ["scientific", "research", "study", "experiment", "analysis", "data", "hypothesis", "theory", "academic", "journal"],
                "code": ["code", "programming", "software", "development", "algorithm", "function", "variable", "debug", "compile", "syntax"],
                "educational": ["education", "learning", "teaching", "student", "school", "university", "course", "lesson", "curriculum"]
            }
            
            # Task detection
            task_keywords = {
                "translation": ["translate", "translation", "language", "multilingual", "convert"],
                "summarization": ["summarize", "summary", "summarization", "abstract", "brief", "condense"],
                "question_answering": ["question", "answer", "qa", "ask", "respond", "query"],
                "sentiment": ["sentiment", "emotion", "feeling", "opinion", "positive", "negative", "mood"],
                "classification": ["classify", "classification", "category", "categorize", "label", "predict"],
                "generation": ["generate", "creation", "create", "produce", "write", "compose"]
            }
            
            # Language detection
            language_keywords = {
                "chinese": ["chinese", "mandarin", "cantonese", "zh", "中文", "汉语"],
                "japanese": ["japanese", "日本語", "ja", "nihongo"],
                "spanish": ["spanish", "español", "es", "castellano"],
                "french": ["french", "français", "fr", "francais"],
                "german": ["german", "deutsch", "de", "german"],
                "multilingual": ["multilingual", "multiple languages", "multi-language", "cross-lingual"]
            }
            
            # Extract domains
            for domain, keywords in domain_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    entities_info["domains"].add(domain)
            
            # Extract tasks
            for task, keywords in task_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    entities_info["tasks"].add(task)
            
            # Extract languages
            for lang, keywords in language_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    entities_info["languages"].add(lang)
            
            # Extract technical terms and model names
            import re
            
            # Add specific model name patterns
            model_patterns = [
                r'\bgpt-[0-9]+\.?[0-9]*-?\w*\b',  # GPT models (gpt-4, gpt-5-nano, etc)
                r'\bclaude-[0-9]+\.?[0-9]*-?\w*\b',  # Claude models
                r'\bllama-?\d*-?\w*\b',  # Llama models
                r'\bgemini-?\w*\b',  # Gemini models  
                r'\bmistral-?\w*\b',  # Mistral models
            ]
            
            for pattern in model_patterns:
                matches = re.findall(pattern, text_lower)
                entities_info["technical_terms"].update(matches)
                entities_info["keywords"].update(matches)
            
            # General technical patterns
            tech_patterns = [
                r'\b\w*bert\w*\b',  # BERT variants
                r'\b\w*gpt\w*\b',   # GPT variants  
                r'\b\w*llm\w*\b',   # LLM variants
                r'\b\w*ai\w*\b',    # AI-related
                r'\b\w*ml\w*\b',    # ML-related
                r'\b\w*neural\w*\b', # Neural networks
            ]
            
            for pattern in tech_patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    if len(match) > 2:  # Filter out too short matches
                        entities_info["technical_terms"].add(match)
            
            # Convert sets to lists for JSON serialization
            return {
                key: list(value) if isinstance(value, set) else value 
                for key, value in entities_info.items()
            }
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {
                "domains": [],
                "tasks": [],
                "languages": [],
                "technical_terms": [],
                "named_entities": {},
                "keywords": []
            }
    
    async def _load_models_from_database(self):
        """Load models from database registry"""
        try:
            # Get all models from database
            result = get_supabase_table('models').select('*').execute()
            models = result.data
            
            logger.info(f"Found {len(models)} models in database registry")
            
            # Process each model
            for model in models:
                model_id = model['model_id']
                
                # Parse metadata if it's a string (from JSONB)
                metadata_raw = model.get('metadata', '{}')
                if isinstance(metadata_raw, str):
                    try:
                        metadata = json.loads(metadata_raw)
                    except json.JSONDecodeError:
                        metadata = {}
                else:
                    metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
                
                # Store model metadata
                self.models_metadata[model_id] = {
                    "provider": model['provider'],
                    "model_type": model['model_type'],
                    "metadata": metadata
                }
            
            # Check embeddings status
            embeddings_result = get_supabase_table('model_embeddings').select('model_id').execute()
            existing_embeddings = {row['model_id'] for row in embeddings_result.data}
            
            logger.info(f"Found {len(existing_embeddings)} model embeddings")
            logger.info(f"Loaded {len(self.models_metadata)} models for similarity matching")
            
            # Warn if models don't have embeddings
            missing_embeddings = set(self.models_metadata.keys()) - existing_embeddings
            if missing_embeddings:
                logger.warning(f"Models without embeddings: {list(missing_embeddings)}")
                logger.warning("Embeddings are generated during startup. Consider restarting the service.")
            
        except Exception as e:
            logger.error(f"Failed to load models from database: {e}")
    
    
    async def select_model(
        self,
        request: str,
        service_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select best model using entity extraction and similarity matching
        
        Args:
            request: User's request/query
            service_type: Type of service needed
            context: Additional context
            
        Returns:
            Selection result with model info and reasoning
        """
        try:
            # Extract entities and keywords from the request
            entities_info = self.extract_entities_and_keywords(request)
            logger.debug(f"Extracted entities: {entities_info}")
            
            # Try entity-based selection first
            entity_based_result = await self._select_model_by_entities(entities_info, service_type, request)
            if entity_based_result and entity_based_result.get("success"):
                return entity_based_result
            
            # Fallback to similarity-based selection
            similarity_result = await self._select_model_by_similarity(request, service_type, entities_info)
            if similarity_result and similarity_result.get("success"):
                return similarity_result
            
            # Final fallback to default
            return self._get_default_selection(service_type, "No suitable models found after entity and similarity matching")
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return self._get_default_selection(service_type, f"Selection error: {e}")
    
    async def _select_model_by_entities(
        self, 
        entities_info: Dict[str, Any], 
        service_type: str, 
        request: str
    ) -> Optional[Dict[str, Any]]:
        """Select model based on extracted entities"""
        try:
            reasoning_parts = []
            candidate_models = []
            
            # Check for domain-specific models
            for domain in entities_info.get("domains", []):
                if domain in self.entity_model_mappings:
                    models = self.entity_model_mappings[domain]["preferred_models"]
                    candidate_models.extend(models)
                    reasoning_parts.append(f"domain: {domain}")
            
            # Check for task-specific models
            for task in entities_info.get("tasks", []):
                if task in self.entity_model_mappings:
                    models = self.entity_model_mappings[task]["preferred_models"]
                    candidate_models.extend(models)
                    reasoning_parts.append(f"task: {task}")
            
            # Check for language-specific models
            for lang in entities_info.get("languages", []):
                if lang in self.entity_model_mappings:
                    models = self.entity_model_mappings[lang]["preferred_models"]
                    candidate_models.extend(models)
                    reasoning_parts.append(f"language: {lang}")
            
            if not candidate_models:
                return None
            
            # Remove duplicates while preserving order
            unique_candidates = list(dict.fromkeys(candidate_models))
            
            # Check which models are actually available in our database
            available_models = []
            for model_id in unique_candidates:
                if model_id in self.models_metadata:
                    model_info = self.models_metadata[model_id]
                    model_type = model_info.get('model_type')
                    
                    # Filter by service type compatibility
                    if model_type == service_type or model_type == 'omni':
                        available_models.append({
                            "model_id": model_id,
                            "provider": model_info.get('provider', 'unknown'),
                            "model_type": model_type,
                            "entity_match_score": 1.0  # High score for entity matches
                        })
            
            if not available_models:
                logger.debug(f"No entity-based models available for {unique_candidates}")
                return None
            
            # Return the first available model (highest priority)
            selected_model = available_models[0]
            
            return {
                "success": True,
                "selected_model": {
                    "model_id": selected_model["model_id"],
                    "provider": selected_model["provider"]
                },
                "selection_reason": f"Entity-based match ({', '.join(reasoning_parts)})",
                "alternatives": available_models[1:3],
                "entity_match_score": selected_model["entity_match_score"],
                "entities_detected": entities_info,
                "method": "entity_based"
            }
            
        except Exception as e:
            logger.error(f"Entity-based model selection failed: {e}")
            return None
    
    async def _select_model_by_similarity(
        self, 
        request: str, 
        service_type: str, 
        entities_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Select model using embedding similarity (enhanced with entity info)"""
        try:
            if not self.embedding_service:
                return None
            
            request_embedding = await self.embedding_service.create_text_embedding(request)
            
            # Find similar models using Supabase
            candidates = await self._find_similar_models_supabase(request_embedding, service_type)
            
            if not candidates:
                return None
            
            # Boost scores for models that match extracted entities
            enhanced_candidates = []
            for candidate in candidates:
                model_id = candidate["model_id"]
                base_score = candidate["similarity"]
                
                # Apply entity-based boosting
                entity_boost = 0.0
                
                # Boost based on domain match
                for domain in entities_info.get("domains", []):
                    if domain in model_id.lower() or any(domain in desc.lower() for desc in [candidate.get("description", "")]):
                        entity_boost += 0.1
                
                # Boost based on task match
                for task in entities_info.get("tasks", []):
                    if task in model_id.lower() or any(task in desc.lower() for desc in [candidate.get("description", "")]):
                        entity_boost += 0.1
                
                # Apply boost
                enhanced_score = min(base_score + entity_boost, 1.0)
                
                enhanced_candidate = candidate.copy()
                enhanced_candidate["similarity"] = enhanced_score
                enhanced_candidate["entity_boost"] = entity_boost
                enhanced_candidates.append(enhanced_candidate)
            
            # Re-sort by enhanced similarity
            enhanced_candidates.sort(key=lambda x: x["similarity"], reverse=True)
            
            best_match = enhanced_candidates[0]
            
            return {
                "success": True,
                "selected_model": {
                    "model_id": best_match["model_id"],
                    "provider": best_match["provider"]
                },
                "selection_reason": f"Enhanced similarity match (base: {best_match['similarity']:.3f}, entity boost: {best_match.get('entity_boost', 0):.3f})",
                "alternatives": enhanced_candidates[1:3],
                "similarity_score": best_match["similarity"],
                "entities_detected": entities_info,
                "method": "enhanced_similarity"
            }
            
        except Exception as e:
            logger.error(f"Similarity-based model selection failed: {e}")
            return None
    
    async def _find_similar_models_supabase(
        self, 
        request_embedding: List[float], 
        service_type: str
    ) -> List[Dict[str, Any]]:
        """Find similar models using Supabase and embedding service similarity"""
        try:
            # Get all model embeddings from database
            embeddings_result = get_supabase_table('model_embeddings').select('*').execute()
            model_embeddings = embeddings_result.data
            
            if not model_embeddings:
                logger.warning("No model embeddings found in database")
                return []
            
            # Calculate similarity for each model
            candidates = []
            for model_embed in model_embeddings:
                model_id = model_embed['model_id']
                model_embedding = model_embed['embedding']
                
                # Get model metadata
                model_metadata = self.models_metadata.get(model_id, {})
                model_type = model_metadata.get('model_type')
                
                # Filter by service type (including omni models)
                if model_type not in [service_type, 'omni']:
                    continue
                
                # Calculate similarity using embedding service
                try:
                    similarity_result = await self.embedding_service.invoke(
                        input_data="",  # Not used for similarity task
                        task="similarity",
                        embedding1=request_embedding,
                        embedding2=model_embedding
                    )
                    similarity = similarity_result['similarity']
                    
                    candidates.append({
                        "model_id": model_id,
                        "provider": model_embed['provider'],
                        "model_type": model_type,
                        "similarity": similarity,
                        "description": model_embed.get('description', '')
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to calculate similarity for {model_id}: {e}")
                    continue
            
            # Sort by similarity score
            candidates.sort(key=lambda x: x["similarity"], reverse=True)
            return candidates[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Supabase similarity search failed: {e}")
            return []
    
    def _get_default_selection(self, service_type: str, reason: str) -> Dict[str, Any]:
        """Get default model selection"""
        default = self.default_models.get(service_type, self.default_models["vision"])
        
        return {
            "success": True,
            "selected_model": default,
            "selection_reason": f"Default selection ({reason})",
            "alternatives": [],
            "similarity_score": 0.0
        }
    
    def get_rate_limit_fallback(self, service_type: str, original_provider: str = "openai") -> Dict[str, Any]:
        """
        Get fallback model when hitting rate limits
        
        Args:
            service_type: Type of service (text, vision, etc.)
            original_provider: The provider that hit rate limit
            
        Returns:
            Fallback model selection result
        """
        if original_provider == "openai" and service_type in self.rate_limit_fallbacks:
            fallback = self.rate_limit_fallbacks[service_type]
            
            return {
                "success": True,
                "selected_model": fallback,
                "selection_reason": f"Rate limit fallback from {original_provider} to {fallback['provider']}",
                "alternatives": [],
                "is_fallback": True,
                "original_provider": original_provider
            }
        
        # If no specific fallback, return default
        return self._get_default_selection(service_type, f"No fallback available for {original_provider}")
    
    async def get_available_models(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            if service_type:
                # Filter by service type
                query = get_supabase_table('models').select('*').or_(f'model_type.eq.{service_type},model_type.eq.omni')
            else:
                # Get all models
                query = get_supabase_table('models').select('*')
            
            result = query.order('model_id').execute()
            return result.data
                
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    async def close(self):
        """Clean up resources"""
        if self.embedding_service:
            await self.embedding_service.close()
            logger.info("Embedding service closed")


# Singleton instance
_selector_instance = None

async def get_model_selector(config: Optional[Dict[str, Any]] = None) -> IntelligentModelSelector:
    """Get singleton model selector instance"""
    global _selector_instance
    
    if _selector_instance is None:
        _selector_instance = IntelligentModelSelector(config)
        await _selector_instance.initialize()
    
    return _selector_instance