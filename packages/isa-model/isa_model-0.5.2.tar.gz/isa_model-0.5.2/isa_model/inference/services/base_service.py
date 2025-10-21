from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, AsyncGenerator, TypeVar, Optional
from ...core.models.model_manager import ModelManager
from ...core.config.config_manager import ConfigManager
from ...core.types import Provider, ServiceType

T = TypeVar('T')  # Generic type for responses

class BaseService(ABC):
    """Base class for all AI services - now uses centralized managers"""
    
    def __init__(self,
                 provider_name: str,
                 model_name: str,
                 model_manager: Optional[ModelManager] = None,
                 config_manager: Optional[ConfigManager] = None):
        self.provider_name = provider_name
        self.model_name = model_name
        self.model_manager = model_manager or ModelManager()
        self.config_manager = config_manager or ConfigManager()

        # Store user_id for billing (will be set by invoke kwargs)
        self._current_user_id: Optional[str] = None

        # Validate provider is configured
        if not self.config_manager.is_provider_enabled(provider_name):
            raise ValueError(f"Provider {provider_name} is not configured or enabled")
    
    def get_api_key(self) -> str:
        """Get API key for the provider"""
        api_key = self.config_manager.get_provider_api_key(self.provider_name)
        if not api_key:
            raise ValueError(f"No API key configured for provider {self.provider_name}")
        return api_key
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider configuration"""
        config = self.config_manager.get_provider_config(self.provider_name)
        if not config:
            return {}
        
        return {
            "api_key": config.api_key,
            "api_base_url": config.api_base_url,
            "organization": config.organization,
            "rate_limit_rpm": config.rate_limit_rpm,
            "rate_limit_tpm": config.rate_limit_tpm,
        }
        
    async def _publish_billing_event(
        self,
        user_id: str,  # REQUIRED: User ID from gateway authentication
        service_type: Union[str, ServiceType],
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Publish usage event to centralized billing system via NATS.

        This replaces local billing calculation with event-driven architecture.
        The billing_service will handle cost calculation and wallet deduction.

        Args:
            user_id: User ID from gateway authentication
            service_type: Type of service (text, vision, audio, etc.)
            operation: Operation performed (chat, generate, etc.)
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            input_units: Input units for non-token services
            output_units: Output units for non-token services
            metadata: Additional metadata
        """
        try:
            from decimal import Decimal
            import logging
            logger = logging.getLogger(__name__)

            # DEBUG: Log that we're entering this method
            logger.info(f"_publish_billing_event called for user={user_id}, model={self.model_name}")

            # Calculate total usage based on service type
            if input_tokens is not None and output_tokens is not None:
                # Token-based services (text, vision)
                usage_amount = Decimal(input_tokens + output_tokens)
                unit_type = "token"
            elif input_units is not None:
                # Unit-based services (audio characters, image count, etc.)
                usage_amount = Decimal(input_units)
                unit_type = "request"  # or determine from service_type
            else:
                logger.warning(f"No usage metrics provided for {user_id}")
                return

            # Prepare usage details
            usage_details = {
                "provider": self.provider_name,
                "model": self.model_name,
                "operation": operation,
                "service_type": service_type if isinstance(service_type, str) else service_type.value,
            }

            # Add token breakdown if available
            if input_tokens is not None:
                usage_details["input_tokens"] = input_tokens
            if output_tokens is not None:
                usage_details["output_tokens"] = output_tokens
            if input_units is not None:
                usage_details["input_units"] = float(input_units)
            if output_units is not None:
                usage_details["output_units"] = float(output_units)
            if metadata:
                usage_details.update(metadata)

            # Import and publish event (lazy import to avoid circular dependency)
            try:
                # Import from isA_common shared library
                from isa_common.events import publish_usage_event
                from isa_common.consul_client import ConsulRegistry
                import os

                # Try Consul discovery first for NATS service
                consul = None
                nats_host = None
                nats_port = None

                try:
                    consul_host = os.getenv('CONSUL_HOST', 'localhost')
                    consul_port = int(os.getenv('CONSUL_PORT', '8500'))
                    consul = ConsulRegistry(consul_host=consul_host, consul_port=consul_port)

                    # Try to discover NATS via Consul
                    nats_url = consul.get_nats_url()
                    if '://' in nats_url:
                        nats_url = nats_url.split('://', 1)[1]
                    nats_host, port_str = nats_url.rsplit(':', 1)
                    nats_port = int(port_str)
                    logger.info(f"Discovered NATS via Consul: {nats_host}:{nats_port}")
                except Exception as consul_err:
                    logger.debug(f"Consul discovery failed: {consul_err}, using environment variables")
                    # Fallback to environment variables or defaults
                    nats_host = os.getenv('NATS_HOST', 'localhost')
                    nats_port = int(os.getenv('NATS_PORT', '50056'))

                success = await publish_usage_event(
                    user_id=user_id,
                    product_id=self.model_name,  # Model name is the product ID
                    usage_amount=usage_amount,
                    unit_type=unit_type,
                    usage_details=usage_details,
                    nats_host=nats_host,
                    nats_port=nats_port
                )

                if success:
                    logger.info(
                        f"Published billing event: user={user_id}, "
                        f"model={self.model_name}, usage={usage_amount} {unit_type}"
                    )
                else:
                    logger.warning(f"Failed to publish billing event for user {user_id}")

            except ImportError as ie:
                logger.error(
                    f"Cannot import billing events module: {ie}. "
                    f"Make sure isa_common package is installed."
                )
            except Exception as pe:
                logger.error(f"Error publishing billing event: {pe}", exc_info=True)

        except Exception as e:
            # Don't let billing event publishing break the service
            import logging
            logging.getLogger(__name__).warning(
                f"Failed to publish billing event: {e}",
                exc_info=True
            )
        
    def __await__(self):
        """Make the service awaitable"""
        yield
        return self

class BaseEmbeddingService(BaseService):
    """Base class for embedding services"""
    
    @abstractmethod
    async def create_text_embedding(self, text: str) -> List[float]:
        """Create embedding for single text"""
        pass
    
    @abstractmethod
    async def create_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        pass
    
    @abstractmethod
    async def create_chunks(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """Create text chunks with embeddings"""
        pass
    
    @abstractmethod
    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute similarity between two embeddings"""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources"""
        pass

class BaseRerankService(BaseService):
    """Base class for reranking services"""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """Rerank documents based on query relevance"""
        pass
    
    @abstractmethod
    async def rerank_texts(
        self,
        query: str,
        texts: List[str]
    ) -> List[Dict]:
        """Rerank raw texts based on query relevance"""
        pass
