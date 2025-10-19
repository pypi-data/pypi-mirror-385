"""
Enhanced rate limiter with enforcement.

Provides thread-safe rate limiting with token bucket algorithm
and per-provider rate management.
"""

import time
import threading
from collections import deque
from typing import Optional, Dict
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class RateLimiter:
    """
    Thread-safe rate limiter with enforcement.
    
    Features:
    - Enforces RPM limits with blocking
    - Token bucket algorithm
    - Per-provider rate limiting
    - Comprehensive error handling
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
        provider_name: str = "default"
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (default: rpm)
            provider_name: Provider identifier
        """
        try:
            self.rpm = max(1, requests_per_minute)  # Minimum 1 RPM
            self.burst_size = burst_size or requests_per_minute
            self.provider_name = provider_name
            
            # Token bucket
            self.tokens = float(self.burst_size)
            self.last_refill = time.time()
            
            # Request tracking
            self.request_times = deque()
            self.lock = threading.Lock()
            
            # Stats
            self.total_requests = 0
            self.blocked_count = 0
            
            logger.debug(f"RateLimiter initialized for {provider_name}: {self.rpm} RPM")
        except Exception as e:
            logger.error(f"Failed to initialize RateLimiter: {e}", exc_info=True)
            # Set safe defaults
            self.rpm = 60
            self.burst_size = 60
            self.provider_name = "default"
            self.tokens = 60.0
            self.last_refill = time.time()
            self.request_times = deque()
            self.lock = threading.Lock()
            self.total_requests = 0
            self.blocked_count = 0
    
    def acquire(self, timeout: Optional[float] = 60) -> bool:
        """
        Acquire permission to make a request (BLOCKING).
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if acquired, False if timeout
        """
        try:
            start_time = time.time()
            
            while True:
                try:
                    with self.lock:
                        self._refill_tokens()
                        
                        # Check if we have tokens
                        if self.tokens >= 1.0:
                            self.tokens -= 1.0
                            self.total_requests += 1
                            return True
                except Exception as e:
                    logger.error(f"Error checking tokens: {e}", exc_info=True)
                    # On error, allow request but log
                    return True
                
                # Check timeout
                try:
                    if timeout and (time.time() - start_time) >= timeout:
                        logger.warning(f"Rate limit timeout after {timeout}s for {self.provider_name}")
                        self.blocked_count += 1
                        return False
                except Exception as e:
                    logger.error(f"Error checking timeout: {e}", exc_info=True)
                    return False
                
                # Wait before retry
                try:
                    wait_time = self._calculate_wait_time()
                    time.sleep(wait_time)
                except Exception as e:
                    logger.error(f"Error during wait: {e}", exc_info=True)
                    time.sleep(1.0)  # Default wait
                    
        except Exception as e:
            logger.error(f"Critical error in acquire: {e}", exc_info=True)
            # On critical error, allow request
            return True
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        try:
            now = time.time()
            elapsed = now - self.last_refill
            
            # Calculate tokens to add (rpm / 60 = tokens per second)
            tokens_per_second = self.rpm / 60.0
            tokens_to_add = elapsed * tokens_per_second
            
            if tokens_to_add >= 1:
                self.tokens = min(float(self.burst_size), self.tokens + tokens_to_add)
                self.last_refill = now
        except Exception as e:
            logger.error(f"Error refilling tokens: {e}", exc_info=True)
            # Reset to safe state
            try:
                self.tokens = float(self.burst_size)
                self.last_refill = time.time()
            except:
                pass
    
    def _calculate_wait_time(self) -> float:
        """Calculate optimal wait time."""
        try:
            with self.lock:
                # If no tokens, calculate time until next token
                tokens_per_second = self.rpm / 60.0
                time_per_token = 1.0 / tokens_per_second
                
                # Add small random jitter to prevent thundering herd
                import random
                jitter = random.uniform(0, time_per_token * 0.1)
                
                return time_per_token + jitter
        except Exception as e:
            logger.error(f"Error calculating wait time: {e}", exc_info=True)
            return 1.0  # Default 1 second wait
    
    def record_request(self):
        """Record a successful request."""
        try:
            with self.lock:
                self.request_times.append(time.time())
                self._cleanup_old_requests()
        except Exception as e:
            logger.error(f"Error recording request: {e}", exc_info=True)
    
    def get_current_rpm(self) -> int:
        """Get current requests per minute."""
        try:
            with self.lock:
                self._cleanup_old_requests()
                return len(self.request_times)
        except Exception as e:
            logger.error(f"Error getting current RPM: {e}", exc_info=True)
            return 0
    
    def get_rpm(self) -> int:
        """
        Get current requests per minute (alias for get_current_rpm).
        
        Returns:
            Current RPM count
        """
        return self.get_current_rpm()
    
    def _cleanup_old_requests(self):
        """Remove requests older than 1 minute."""
        try:
            cutoff = time.time() - 60
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()
        except Exception as e:
            logger.error(f"Error cleaning up requests: {e}", exc_info=True)
            # Clear all on error
            try:
                self.request_times.clear()
            except:
                pass
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        try:
            with self.lock:
                current_rpm = self.get_current_rpm()
                utilization = (current_rpm / self.rpm * 100) if self.rpm > 0 else 0
                
                return {
                    'provider': self.provider_name,
                    'rpm_limit': self.rpm,
                    'current_rpm': current_rpm,
                    'tokens_available': int(self.tokens),
                    'total_requests': self.total_requests,
                    'blocked_count': self.blocked_count,
                    'utilization': utilization
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'provider': self.provider_name,
                'error': str(e)
            }


class ProviderRateLimitManager:
    """
    Manage rate limiters for multiple providers.
    
    Each provider gets its own rate limiter with specific limits.
    Thread-safe with comprehensive error handling.
    """
    
    def __init__(self):
        """Initialize rate limit manager."""
        try:
            self.limiters: Dict[str, RateLimiter] = {}
            self.lock = threading.Lock()
            
            # Default limits per provider
            self.default_limits = {
                'openai': 60,          # 60 RPM for tier 1
                'anthropic': 50,       # 50 RPM default
                'ultrasafe': 100,      # 100 RPM
                'openrouter': 200      # 200 RPM
            }
            
            logger.info("ProviderRateLimitManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ProviderRateLimitManager: {e}", exc_info=True)
            self.limiters = {}
            self.lock = threading.Lock()
            self.default_limits = {}
    
    def get_limiter(self, provider_name: str, custom_rpm: Optional[int] = None) -> RateLimiter:
        """Get or create rate limiter for provider."""
        try:
            with self.lock:
                if provider_name not in self.limiters:
                    rpm = custom_rpm or self.default_limits.get(provider_name, 60)
                    self.limiters[provider_name] = RateLimiter(
                        requests_per_minute=rpm,
                        provider_name=provider_name
                    )
                return self.limiters[provider_name]
        except Exception as e:
            logger.error(f"Error getting limiter for {provider_name}: {e}", exc_info=True)
            # Return a default limiter
            try:
                return RateLimiter(requests_per_minute=60, provider_name=provider_name)
            except:
                # Last resort - create minimal limiter
                limiter = object.__new__(RateLimiter)
                limiter.rpm = 60
                limiter.provider_name = provider_name
                return limiter
    
    def acquire(self, provider_name: str, timeout: float = 60) -> bool:
        """Acquire permission for provider."""
        try:
            limiter = self.get_limiter(provider_name)
            return limiter.acquire(timeout=timeout)
        except Exception as e:
            logger.error(f"Error acquiring rate limit for {provider_name}: {e}", exc_info=True)
            # On error, allow request
            return True
    
    def record_request(self, provider_name: str):
        """Record successful request."""
        try:
            limiter = self.get_limiter(provider_name)
            limiter.record_request()
        except Exception as e:
            logger.error(f"Error recording request for {provider_name}: {e}", exc_info=True)
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Get stats for all providers."""
        try:
            with self.lock:
                return {
                    name: limiter.get_stats()
                    for name, limiter in self.limiters.items()
                }
        except Exception as e:
            logger.error(f"Error getting all stats: {e}", exc_info=True)
            return {}