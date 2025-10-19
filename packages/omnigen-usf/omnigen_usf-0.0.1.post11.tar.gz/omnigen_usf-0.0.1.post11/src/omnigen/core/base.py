"""Base classes and protocols for OmniGen."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
from omnigen.core.types import Message, Conversation


class BaseLLMProvider(ABC):
    """Base interface for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.client = None
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate chat completion.
        
        Args:
            messages: List of messages
            model: Model name (optional, uses config default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass
    
    def _prepare_messages(self, messages: List[Message]) -> List[Dict]:
        """
        Convert messages to provider-specific format.
        
        Args:
            messages: List of Message objects
            
        Returns:
            Provider-specific message format
        """
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]


class BaseGenerator(ABC):
    """Base interface for data generators."""
    
    @abstractmethod
    def generate(self, *args, **kwargs) -> Any:
        """Generate data."""
        pass
    
    @abstractmethod
    def generate_batch(self, *args, **kwargs) -> List[Any]:
        """Generate batch of data."""
        pass


class BaseDataLoader(ABC):
    """Base interface for data loaders."""
    
    @abstractmethod
    def load(self) -> Iterator[str]:
        """
        Load and yield base messages.
        
        Yields:
            Base message strings
        """
        pass
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate data format.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid
        """
        pass
    
    def __iter__(self):
        """Make loader iterable."""
        return self.load()


class BaseWriter(ABC):
    """Base interface for output writers."""
    
    @abstractmethod
    def write(self, conversation: Conversation) -> None:
        """
        Write single conversation.
        
        Args:
            conversation: Conversation to write
        """
        pass
    
    @abstractmethod
    def finalize(self) -> None:
        """Finalize output (flush buffers, close files, etc.)."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.finalize()