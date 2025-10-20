# File: crewplus/callbacks/run_id_handler.py

from typing import Any, Dict, List
from uuid import UUID
import logging

# Langfuse imports with graceful fallback
from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
from .async_langfuse_handler import AsyncLangfuseCallbackHandler
from langfuse import get_client
from langchain_core.messages import BaseMessage
#from langchain_core.outputs import LLMResult
LANGFUSE_AVAILABLE = True

# --- Custom Callback Handlers to capture the run_id ---

class RunIdCallbackHandler(LangfuseCallbackHandler):
    """
    A custom handler that injects the LangChain run_id into the metadata
    before the Langfuse observation is created.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_trace_map = {}
        # Use a named logger for better context
        self.logger = logging.getLogger(__name__)
        self.logger.info("RunIdCallbackHandler initialized.")

    def _inject_run_id_to_metadata(self, run_id: UUID, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to safely add the run_id to the metadata in kwargs."""
        metadata = kwargs.get("metadata") or {}
        metadata["langchain_run_id"] = str(run_id)
        kwargs["metadata"] = metadata
        return kwargs

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        self.logger.debug(f"[on_chain_start] Intercepted run_id: {run_id}")
        kwargs = self._inject_run_id_to_metadata(run_id, kwargs)
        
        # Call the base handler with the modified kwargs
        result = super().on_chain_start(serialized, inputs, run_id=run_id, **kwargs)
        
        # We still map the trace_id for easy retrieval in tests
        if self.last_trace_id:
            self.run_trace_map[str(run_id)] = self.last_trace_id
            self.logger.info(f"[on_chain_start] Mapped run_id '{run_id}' to trace_id '{self.last_trace_id}'.")
            
        return result

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        self.logger.debug(f"[on_chat_model_start] Intercepted run_id: {run_id}")
        
        # Only inject the run_id if this is the root of the trace
        if parent_run_id is None:
            kwargs = self._inject_run_id_to_metadata(run_id, kwargs)

        # Call the base handler with potentially modified kwargs
        result = super().on_chat_model_start(serialized, messages, run_id=run_id, parent_run_id=parent_run_id, **kwargs)

        if parent_run_id is None and self.last_trace_id:
            self.run_trace_map[str(run_id)] = self.last_trace_id
            self.logger.info(f"[on_chat_model_start] Mapped root run_id '{run_id}' to trace_id '{self.last_trace_id}'.")

        return result

# You would similarly update the AsyncRunIdCallbackHandler if you use it
class AsyncRunIdCallbackHandler(AsyncLangfuseCallbackHandler):
    """
    An async custom handler that injects the LangChain run_id into the metadata
    before the Langfuse observation is created.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_trace_map = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("AsyncRunIdCallbackHandler initialized.")

    def _inject_run_id_to_metadata(self, run_id: UUID, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to safely add the run_id to the metadata in kwargs."""
        metadata = kwargs.get("metadata") or {}
        metadata["langchain_run_id"] = str(run_id)
        kwargs["metadata"] = metadata
        return kwargs

    async def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        self.logger.debug(f"Async [on_chain_start] Intercepted run_id: {run_id}")
        kwargs = self._inject_run_id_to_metadata(run_id, kwargs)
        result = await super().on_chain_start(serialized, inputs, run_id=run_id, **kwargs)
        if self.last_trace_id:
            self.run_trace_map[str(run_id)] = self.last_trace_id
        return result

    async def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        self.logger.debug(f"Async [on_chat_model_start] Intercepted run_id: {run_id}")
        if parent_run_id is None:
            kwargs = self._inject_run_id_to_metadata(run_id, kwargs)
        result = await super().on_chat_model_start(serialized, messages, run_id=run_id, parent_run_id=parent_run_id, **kwargs)
        
        if parent_run_id is None and self.last_trace_id:
            self.run_trace_map[str(run_id)] = self.last_trace_id
        return result
