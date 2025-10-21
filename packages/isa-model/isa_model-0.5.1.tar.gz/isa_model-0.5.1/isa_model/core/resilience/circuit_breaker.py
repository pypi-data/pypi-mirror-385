"""
Circuit Breaker Implementation for External Service Calls

Provides resilience patterns including:
- Circuit breaker for external API calls
- Retry with exponential backoff
- Timeout handling
- Health monitoring
"""

import asyncio
import time
import logging
import functools
from typing import Dict, Any, Optional, Callable, Union, List
from enum import Enum
from dataclasses import dataclass, field
from circuitbreaker import circuit
import structlog

logger = structlog.get_logger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker triggered, blocking calls
    HALF_OPEN = "half_open"  # Testing if service is recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: int = 30          # Seconds before trying to recover
    expected_exception: type = Exception  # Exception type that triggers circuit breaker
    success_threshold: int = 3          # Successful calls needed to close circuit
    timeout: float = 30.0               # Request timeout in seconds

@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: List[Dict[str, Any]] = field(default_factory=list)

class EnhancedCircuitBreaker:
    """Enhanced circuit breaker with monitoring and configuration"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.stats = CircuitBreakerStats()
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        
        # Create underlying circuit breaker
        self._circuit = circuit(
            failure_threshold=config.failure_threshold,
            recovery_timeout=config.recovery_timeout,
            expected_exception=config.expected_exception
        )
        
        logger.info("Circuit breaker initialized", name=name, config=config)
    
    def __call__(self, func: Callable):
        """Decorator to wrap functions with circuit breaker"""
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        
        # Apply the circuit breaker decorator
        wrapped_func = self._circuit(wrapper)
        return wrapped_func
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        start_time = time.time()
        
        try:
            # Record call attempt
            self.stats.total_calls += 1
            
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_state_change < self.config.recovery_timeout:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker '{self.name}' is open"
                    )
                else:
                    # Try to move to half-open state
                    self._change_state(CircuitState.HALF_OPEN)
            
            # Execute the function with timeout
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=self.config.timeout
                    )
                else:
                    result = func(*args, **kwargs)
                
                # Record success
                self._record_success()
                
                return result
                
            except asyncio.TimeoutError:
                self._record_failure()
                raise CircuitBreakerTimeoutException(
                    f"Timeout after {self.config.timeout}s for '{self.name}'"
                )
            except self.config.expected_exception as e:
                self._record_failure()
                raise
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Circuit breaker call failed",
                name=self.name,
                error=str(e),
                duration=duration,
                state=self.state.value
            )
            raise
    
    def _record_success(self):
        """Record successful call"""
        self.stats.successful_calls += 1
        self.stats.consecutive_successes += 1
        self.stats.consecutive_failures = 0
        self.stats.last_success_time = time.time()
        
        # If we're in half-open state and have enough successes, close the circuit
        if (self.state == CircuitState.HALF_OPEN and 
            self.stats.consecutive_successes >= self.config.success_threshold):
            self._change_state(CircuitState.CLOSED)
        
        logger.debug(
            "Circuit breaker success",
            name=self.name,
            consecutive_successes=self.stats.consecutive_successes,
            state=self.state.value
        )
    
    def _record_failure(self):
        """Record failed call"""
        self.stats.failed_calls += 1
        self.stats.consecutive_failures += 1
        self.stats.consecutive_successes = 0
        self.stats.last_failure_time = time.time()
        
        # Check if we should open the circuit
        if (self.state == CircuitState.CLOSED and 
            self.stats.consecutive_failures >= self.config.failure_threshold):
            self._change_state(CircuitState.OPEN)
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state reopens the circuit
            self._change_state(CircuitState.OPEN)
        
        logger.warning(
            "Circuit breaker failure",
            name=self.name,
            consecutive_failures=self.stats.consecutive_failures,
            state=self.state.value
        )
    
    def _change_state(self, new_state: CircuitState):
        """Change circuit breaker state"""
        old_state = self.state
        self.state = new_state
        self.last_state_change = time.time()
        
        # Record state change
        state_change = {
            "from_state": old_state.value,
            "to_state": new_state.value,
            "timestamp": self.last_state_change,
            "total_calls": self.stats.total_calls,
            "consecutive_failures": self.stats.consecutive_failures
        }
        self.stats.state_changes.append(state_change)
        
        logger.warning(
            "Circuit breaker state changed",
            name=self.name,
            from_state=old_state.value,
            to_state=new_state.value,
            consecutive_failures=self.stats.consecutive_failures
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.stats.total_calls,
            "successful_calls": self.stats.successful_calls,
            "failed_calls": self.stats.failed_calls,
            "success_rate": (
                self.stats.successful_calls / self.stats.total_calls 
                if self.stats.total_calls > 0 else 0
            ),
            "consecutive_failures": self.stats.consecutive_failures,
            "consecutive_successes": self.stats.consecutive_successes,
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time,
            "last_state_change": self.last_state_change,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "timeout": self.config.timeout
            }
        }
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self.last_state_change = time.time()
        
        logger.info("Circuit breaker reset", name=self.name)

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreakerTimeoutException(Exception):
    """Exception raised when call times out"""
    pass

# Global circuit breaker registry
_circuit_breakers: Dict[str, EnhancedCircuitBreaker] = {}

def get_circuit_breaker(
    name: str, 
    config: Optional[CircuitBreakerConfig] = None
) -> EnhancedCircuitBreaker:
    """Get or create a circuit breaker"""
    if name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig()
        _circuit_breakers[name] = EnhancedCircuitBreaker(name, config)
    
    return _circuit_breakers[name]

def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
    timeout: float = 30.0,
    expected_exception: type = Exception
):
    """Decorator for applying circuit breaker to functions"""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        timeout=timeout,
        expected_exception=expected_exception
    )
    
    breaker = get_circuit_breaker(name, config)
    return breaker

# Predefined circuit breakers for common services
def openai_circuit_breaker():
    """Circuit breaker for OpenAI API calls"""
    return circuit_breaker(
        name="openai",
        failure_threshold=3,
        recovery_timeout=60,
        timeout=120.0  # OpenAI can be slow
    )

def replicate_circuit_breaker():
    """Circuit breaker for Replicate API calls"""
    return circuit_breaker(
        name="replicate",
        failure_threshold=3,
        recovery_timeout=45,
        timeout=300.0  # Replicate can be very slow for image generation
    )

def database_circuit_breaker():
    """Circuit breaker for database calls"""
    return circuit_breaker(
        name="database",
        failure_threshold=5,
        recovery_timeout=20,
        timeout=10.0
    )

def redis_circuit_breaker():
    """Circuit breaker for Redis calls"""
    return circuit_breaker(
        name="redis",
        failure_threshold=3,
        recovery_timeout=15,
        timeout=5.0
    )

# Health check for all circuit breakers
async def check_circuit_breakers_health() -> Dict[str, Any]:
    """Check health of all circuit breakers"""
    health_status = {
        "circuit_breakers": {},
        "total_breakers": len(_circuit_breakers),
        "open_breakers": 0,
        "status": "healthy"
    }
    
    for name, breaker in _circuit_breakers.items():
        stats = breaker.get_stats()
        health_status["circuit_breakers"][name] = stats
        
        if stats["state"] == "open":
            health_status["open_breakers"] += 1
    
    # Overall health status
    if health_status["open_breakers"] > 0:
        health_status["status"] = "degraded"
    
    return health_status

# Utility functions for retry with exponential backoff
async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Retry function with exponential backoff"""
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
        except exceptions as e:
            if attempt == max_retries:
                logger.error(
                    "All retry attempts failed",
                    attempts=attempt + 1,
                    error=str(e)
                )
                raise
            
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            
            logger.warning(
                "Retry attempt failed, backing off",
                attempt=attempt + 1,
                max_retries=max_retries,
                delay=delay,
                error=str(e)
            )
            
            await asyncio.sleep(delay)