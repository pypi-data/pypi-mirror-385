#!/usr/bin/env python3
"""
Complete embedding service test with all functionality
"""

import asyncio
import sys
import os
import json

# Add the isa_model to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_complete_embedding_service():
    """Test all embedding service functionality"""
    print("🚀 Testing Complete ISA Model Embedding Service...")
    print("=" * 60)
    
    try:
        from isa_model.client import ISAModelClient
        client = ISAModelClient()
        
        print("✅ ISA client imported successfully")
        
        # Test 1: Basic embedding
        print("\n📌 Test 1: Basic Embedding")
        try:
            result = await client.invoke(
                input_data="Hello world",
                task="embed",
                service_type="embedding"
            )
            
            if result.get('success'):
                embedding = result['result']
                print(f"✅ Basic embedding: {len(embedding)} dimensions")
                print(f"   First 5 values: {embedding[:5]}")
                print(f"   Model used: {result.get('metadata', {}).get('model_used', 'unknown')}")
                print(f"   Cost: ${result.get('metadata', {}).get('billing', {}).get('cost_usd', 0)}")
            else:
                print(f"❌ Basic embedding failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Basic embedding exception: {e}")
        
        # Test 2: Batch embedding  
        print("\n📌 Test 2: Batch Embedding")
        try:
            result = await client.invoke(
                input_data=["Machine learning", "Deep learning", "Natural language processing"],
                task="embed_batch",
                service_type="embedding"
            )
            
            if result.get('success'):
                embeddings = result['result']
                print(f"✅ Batch embedding: {len(embeddings)} embeddings")
                print(f"   Each with {len(embeddings[0])} dimensions")
                print(f"   Total cost: ${result.get('metadata', {}).get('billing', {}).get('cost_usd', 0)}")
            else:
                print(f"❌ Batch embedding failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Batch embedding exception: {e}")
        
        # Test 3: Text-based similarity search
        print("\n📌 Test 3: Text-based Similarity Search") 
        try:
            result = await client.invoke(
                input_data="artificial intelligence",
                task="similarity",
                service_type="embedding",
                candidates=["machine learning algorithms", "cooking recipes", "deep learning networks", "computer science"]
            )
            
            if result.get('success'):
                similar_docs = result['result']['similar_documents']
                print(f"✅ Similarity search: {len(similar_docs)} results")
                for doc in similar_docs:
                    print(f"   {doc['similarity']:.3f}: {doc['text']}")
            else:
                print(f"❌ Similarity search failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Similarity search exception: {e}")
        
        # Test 4: Text chunking with embeddings
        print("\n📌 Test 4: Text Chunking with Embeddings")
        try:
            long_text = """
            Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models 
            that enable computers to learn and make decisions without being explicitly programmed. Deep learning, 
            a specialized branch of machine learning, uses artificial neural networks with multiple layers to model 
            and understand complex patterns in data. Natural language processing (NLP) is another important field 
            that enables computers to understand, interpret, and generate human language in a valuable way. 
            Computer vision allows machines to interpret and make decisions based on visual data from the world around them.
            """
            
            result = await client.invoke(
                input_data=long_text.strip(),
                task="chunk",
                service_type="embedding",
                chunk_size=20,
                overlap=5,
                metadata={"source": "test_document", "type": "educational"}
            )
            
            if result.get('success'):
                chunks = result['result']
                print(f"✅ Text chunking: {len(chunks)} chunks created")
                for i, chunk in enumerate(chunks):
                    words_in_chunk = len(chunk['text'].split())
                    print(f"   Chunk {i+1}: {words_in_chunk} words, embedding dim: {len(chunk['embedding'])}")
                    print(f"     Text: \"{chunk['text'][:60]}...\"")
                    print(f"     Range: words {chunk['start_index']}-{chunk['end_index']}")
                    print(f"     Metadata: {chunk['metadata']}")
            else:
                print(f"❌ Text chunking failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Text chunking exception: {e}")
        
        # Test 5: Document reranking (ISA service)
        print("\n📌 Test 5: Document Reranking (ISA Jina Reranker v2)")
        try:
            result = await client.invoke(
                input_data="artificial intelligence and machine learning",
                task="rerank",
                service_type="embedding",
                documents=[
                    "Machine learning is a subset of artificial intelligence that uses algorithms to learn from data",
                    "Cooking delicious pasta requires proper timing and quality ingredients", 
                    "Deep learning neural networks can process complex patterns in large datasets",
                    "The weather forecast predicts rain for tomorrow afternoon",
                    "Natural language processing enables computers to understand human language"
                ],
                top_k=3,
                return_documents=True
            )
            
            if result.get('success'):
                rerank_results = result['result']['results']
                print(f"✅ Document reranking: {len(rerank_results)} results")
                for i, item in enumerate(rerank_results):
                    score = item.get('relevance_score', item.get('score', 0))
                    doc = item.get('document', item.get('text', ''))
                    print(f"   {i+1}. Score: {score:.3f} - {doc[:60]}...")
                
                # Show performance metrics
                if 'processing_time' in result['result']:
                    print(f"   Processing time: {result['result']['processing_time']:.3f}s")
                if 'billing' in result['result']:
                    print(f"   Cost: ${result['result']['billing'].get('estimated_cost_usd', 0):.6f}")
            else:
                print(f"❌ Document reranking failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Document reranking exception: {e}")
        
        # Test 6: Advanced similarity with threshold
        print("\n📌 Test 6: Advanced Similarity with Threshold")
        try:
            result = await client.invoke(
                input_data="machine learning algorithms",
                task="similarity",
                service_type="embedding",
                candidates=[
                    "artificial neural networks and deep learning",
                    "baking chocolate chip cookies recipe",
                    "supervised learning classification models", 
                    "gardening tips for spring season",
                    "unsupervised clustering techniques"
                ],
                top_k=3,
                threshold=0.3
            )
            
            if result.get('success'):
                similar_docs = result['result']['similar_documents']
                print(f"✅ Advanced similarity (threshold=0.3): {len(similar_docs)} results")
                for doc in similar_docs:
                    print(f"   {doc['similarity']:.3f}: {doc['text']}")
                print(f"   Total candidates: {result['result']['total_candidates']}")
                print(f"   Returned (above threshold): {result['result']['returned_count']}")
            else:
                print(f"❌ Advanced similarity failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Advanced similarity exception: {e}")
        
        # Test 7: Model parameter testing
        print("\n📌 Test 7: Custom Model Parameters")
        try:
            result = await client.invoke(
                input_data="Testing with custom model parameters",
                task="embed",
                service_type="embedding",
                model="text-embedding-3-small",
                provider="openai"
            )
            
            if result.get('success'):
                embedding = result['result']
                print(f"✅ Custom model embedding: {len(embedding)} dimensions")
                print(f"   Model: {result.get('metadata', {}).get('model_used', 'unknown')}")
                print(f"   Provider: {result.get('metadata', {}).get('provider', 'unknown')}")
            else:
                print(f"❌ Custom model test failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Custom model test exception: {e}")
            
    except ImportError as e:
        print(f"❌ Failed to import ISA client: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Embedding Service Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_complete_embedding_service())