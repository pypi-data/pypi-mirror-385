# File: crewplus/services/tracing_manager.py

from typing import Any, Optional, List, Protocol
import os
import logging

# Langfuse imports with graceful fallback. This allows the application to run
# even if the langfuse library is not installed.
try:
    from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
    from ..callbacks.async_langfuse_handler import AsyncLangfuseCallbackHandler
    # Import the new custom handlers
    from ..callbacks.run_id_handler import RunIdCallbackHandler, AsyncRunIdCallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    LangfuseCallbackHandler = None
    AsyncLangfuseCallbackHandler = None
    # Define dummy classes for the custom handlers to prevent errors if langfuse is not installed
    class RunIdCallbackHandler: pass
    class AsyncRunIdCallbackHandler: pass

class TracingContext(Protocol):
    """
    A protocol that defines a formal contract for a model to be "traceable."

    This protocol ensures that any class using the TracingManager provides the
    necessary attributes and methods for the manager to function correctly. By
    using a Protocol, we leverage Python's static analysis tools (like mypy)
    to enforce this contract, preventing runtime errors and making the system
    more robust and self-documenting.

    It allows the TracingManager to be completely decoupled from any specific
    model implementation, promoting clean, compositional design.

    A class that implements this protocol must provide:
    - A `logger` attribute for logging.
    - An `enable_tracing` attribute to control tracing.
    - A `get_model_identifier` method to describe itself for logging purposes.
    """
    logger: logging.Logger
    enable_tracing: Optional[bool]
    
    def get_model_identifier(self) -> str:
        """
        Return a string that uniquely identifies the model instance for logging.
        
        Example:
            "GeminiChatModel (model='gemini-1.5-flash')"
            
        Note:
            The '...' (Ellipsis) is the standard way in a Protocol to indicate
            that this method must be implemented by any class that conforms to
            this protocol, but has no implementation in the protocol itself.
        """
        ...

class TracingManager:
    """
    Manages the initialization and injection of tracing handlers for chat models.
    
    This class uses a composition-based approach, taking a context object that
    fulfills the TracingContext protocol. This design is highly extensible,
    allowing new tracing providers (e.g., Helicone, OpenTelemetry) to be added
    with minimal, isolated changes.
    """
    
    def __init__(self, context: TracingContext):
        """
        Args:
            context: An object (typically a chat model instance) that conforms
                     to the TracingContext protocol.
        """
        self.context = context
        self._sync_handlers: List[Any] = []
        self._async_handlers: List[Any] = []
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """
        Initializes all supported tracing handlers. This is the central point
        for adding new observability tools.
        """
        self._sync_handlers = []
        self._async_handlers = []
        self._initialize_langfuse()
        # To add a new handler (e.g., Helicone), you would add a call to
        # self._initialize_helicone() here.
    
    def _initialize_langfuse(self):
        """Initializes the Langfuse handler if it's available and enabled."""
        if not LANGFUSE_AVAILABLE:
            if self.context.enable_tracing is True:
                self.context.logger.warning("Langfuse is not installed; tracing will be disabled. Install with: pip install langfuse")
            return
        
        # Determine if Langfuse should be enabled via an explicit flag or
        # by detecting its environment variables.
        enable_langfuse = self.context.enable_tracing
        if enable_langfuse is None: # Auto-detect if not explicitly set
            langfuse_env_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
            enable_langfuse = any(os.getenv(var) for var in langfuse_env_vars)
        
        if enable_langfuse:
            try:
                # Create and add both the standard and the run_id-capturing handlers.
                # The standard handler creates the trace, and the custom one updates it.
                self._sync_handlers.append(LangfuseCallbackHandler())
                self._sync_handlers.append(RunIdCallbackHandler())

                if AsyncLangfuseCallbackHandler:
                    self._async_handlers.append(AsyncLangfuseCallbackHandler())
                    self._async_handlers.append(AsyncRunIdCallbackHandler())
                
                self.context.logger.info(f"Langfuse tracing enabled for {self.context.get_model_identifier()}")
            except Exception as e:
                self.context.logger.warning(f"Failed to initialize Langfuse: {e}")
    
    def _add_callbacks_to_config(self, config: Optional[dict], handlers: List[Any]) -> dict:
        """A generic helper to add a list of handlers to a config object."""
        if config is None:
            config = {}
        
        if not handlers or config.get("metadata", {}).get("tracing_disabled"):
            return config
        
        callbacks = config.get("callbacks")
        
        if hasattr(callbacks, 'add_handler') and hasattr(callbacks, 'handlers'):
            for handler in handlers:
                if not any(isinstance(cb, type(handler)) for cb in callbacks.handlers):
                    callbacks.add_handler(handler, inherit=True)
            return config
        
        current_callbacks = callbacks or []
        new_callbacks = list(current_callbacks)
        
        for handler in handlers:
            if not any(isinstance(cb, type(handler)) for cb in new_callbacks):
                new_callbacks.append(handler)
        
        if len(new_callbacks) > len(current_callbacks):
            # Create a new dictionary with the updated callbacks list.
            # This is a safe operation that overwrites the existing 'callbacks'
            # key and avoids mutating the original config object.
            return {**config, "callbacks": new_callbacks}
        
        return config

    def add_sync_callbacks_to_config(self, config: Optional[dict]) -> dict:
        """Adds synchronous tracing handlers to the request configuration."""
        return self._add_callbacks_to_config(config, self._sync_handlers)

    def add_async_callbacks_to_config(self, config: Optional[dict]) -> dict:
        """Adds asynchronous tracing handlers to the request configuration."""
        return self._add_callbacks_to_config(config, self._async_handlers)
