import os
from typing import Dict, Any, Optional

from langchain_community.chat_models.openai import ChatOpenAI as ChatOpenAIBase
from pydantic import BaseModel, Field, model_validator
from langchain.utils import get_from_dict_or_env
from langchain_community.utils.openai import is_openai_v1

from .client import CrucibleOpenAI
from .async_client import CrucibleAsyncOpenAI
from langchain.schema.runnable import RunnableLambda


class ChatOpenAI(ChatOpenAIBase):
    """
    LangChain ChatOpenAI wrapper for Crucible.
    
    Provides seamless integration with LangChain while automatically
    logging requests and responses to Crucible warehouse.
    """
    
    crucible_kwargs: Dict[str, Any] = Field(
        default_factory=lambda: {"verify_ssl": False}
    )

    def __init__(self, **kwargs):
        """Initialize the ChatOpenAI with Crucible client."""
        # Extract Crucible configuration before calling super()
        crucible_kwargs = kwargs.pop('crucible_kwargs', {})
        
        # Call parent constructor
        super().__init__(**kwargs)
        
        # Create Crucible client if configuration provided
        self._crucible_client = None
        if crucible_kwargs:
            crucible_api_key = crucible_kwargs.get('api_key') or os.getenv('CRUCIBLE_API_KEY')
            crucible_domain = crucible_kwargs.get('domain') or os.getenv('CRUCIBLE_DOMAIN', 'warehouse.usecrucible.ai')
            
            if crucible_api_key:
                # Create Crucible client
                self._crucible_client = CrucibleOpenAI(
                    api_key=crucible_api_key,
                    domain=crucible_domain
                )
                
                # Replace the client with Crucible's wrapped client
                self.client = self._crucible_client.chat.completions
                
                # Store metadata for injection
                self._crucible_metadata = {}

    def bind_metadata(self, **kwargs):
        """Bind metadata to the LLM for use in chains."""
        # Store metadata for use in chains
        if not hasattr(self, "_crucible_metadata"):
            self._crucible_metadata = {}
        
        self._crucible_metadata.update(kwargs)
        
        # Return a wrapper that injects metadata
        def metadata_injector(input_data):
            return self.invoke(input_data, crucible_metadata=self._crucible_metadata)
        
        return RunnableLambda(metadata_injector)

    def with_metadata(self, **kwargs) -> "ChatOpenAI":
        """
        Add metadata to be sent with Crucible requests.
        
        Args:
            **kwargs: Metadata key-value pairs
            
        Returns:
            ChatOpenAI instance with metadata
        """
        # Store metadata for use in invoke/ainvoke methods
        if not hasattr(self, "_crucible_metadata"):
            self._crucible_metadata = {}
        
        self._crucible_metadata.update(kwargs)
        
        return self

    def invoke(self, input, config=None, **kwargs):
        """
        Invoke the model with input and optional metadata.
        
        Args:
            input: Input to the model
            config: Optional configuration
            **kwargs: Additional arguments
            
        Returns:
            Model response
        """
        # Extract metadata if provided
        crucible_metadata = kwargs.pop("crucible_metadata", {})
        
        # Merge with stored metadata
        if hasattr(self, "_crucible_metadata"):
            crucible_metadata.update(self._crucible_metadata)
        
        # Store metadata for _generate method
        if crucible_metadata:
            self._current_metadata = crucible_metadata
        
        # Remove any Crucible-specific kwargs that shouldn't be passed to OpenAI
        kwargs.pop("_crucible_client", None)
        
        return super().invoke(input, config=config, **kwargs)

    async def ainvoke(self, input, config=None, **kwargs):
        """
        Async invoke the model with input and optional metadata.
        
        Args:
            input: Input to the model
            config: Optional configuration
            **kwargs: Additional arguments
            
        Returns:
            Model response
        """
        # Extract metadata if provided
        crucible_metadata = kwargs.pop("crucible_metadata", {})
        
        # Merge with stored metadata
        if hasattr(self, "_crucible_metadata"):
            crucible_metadata.update(self._crucible_metadata)
        
        # Store metadata for _generate method
        if crucible_metadata:
            self._current_metadata = crucible_metadata
        
        # Remove any Crucible-specific kwargs that shouldn't be passed to OpenAI
        kwargs.pop("_crucible_client", None)
        
        return await super().ainvoke(input, config=config, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Override _generate to inject Crucible metadata."""
        # Get current metadata from invoke method
        crucible_metadata = getattr(self, "_current_metadata", {})
        
        # Add metadata to kwargs if present
        if crucible_metadata:
            kwargs["crucible_metadata"] = crucible_metadata
        
        # Clear current metadata after use
        if hasattr(self, "_current_metadata"):
            delattr(self, "_current_metadata")
        
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    def close(self) -> None:
        """Close the Crucible client and flush logs."""
        if hasattr(self, "_crucible_client"):
            self._crucible_client.close()

    def flush_logs(self) -> None:
        """Force flush of pending logs."""
        if hasattr(self, "_crucible_client"):
            self._crucible_client.flush_logs()

    def get_logging_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        if hasattr(self, "_crucible_client"):
            return self._crucible_client.get_logging_stats()
        return {}

    def is_healthy(self) -> bool:
        """Check if client is healthy."""
        if hasattr(self, "_crucible_client"):
            return self._crucible_client.is_healthy()
        return True

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass
