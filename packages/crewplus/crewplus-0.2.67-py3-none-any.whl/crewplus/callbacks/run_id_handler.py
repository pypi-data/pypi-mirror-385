# File: crewplus/callbacks/run_id_handler.py

from typing import Any, Dict
from uuid import UUID
import logging

# Langfuse imports with graceful fallback
from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
from .async_langfuse_handler import AsyncLangfuseCallbackHandler
from langfuse import get_client
LANGFUSE_AVAILABLE = True

# --- Custom Callback Handlers to capture the run_id ---

class RunIdCallbackHandler(LangfuseCallbackHandler):
    """
    A custom synchronous callback handler that captures the Langchain run_id
    and adds it to the Langfuse trace metadata. It also stores the mapping
    between the run_id and the generated trace_id.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_trace_map = {}
        # Use a named logger for better context
        self.logger = logging.getLogger(__name__)
        self.logger.info("RunIdCallbackHandler initialized.")

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        self.logger.debug(f"on_chain_start triggered for run_id: {run_id}")
        # First, let the base handler do its work, which includes creating the trace
        run = super().on_chain_start(serialized, inputs, run_id, **kwargs)
        self.logger.debug(f"Base handler's on_chain_start completed. Current trace_id: {self.last_trace_id}")

        try:
            # The base handler sets `self.last_trace_id` when a trace is created
            if self.last_trace_id:
                self.run_trace_map[str(run_id)] = self.last_trace_id
                self.logger.info(f"Mapping run_id '{run_id}' to trace_id '{self.last_trace_id}'.")

                # Then, update the created trace with the run_id as metadata
                langfuse_client = get_client()
                langfuse_client.update_current_trace(
                    metadata={"langchain_run_id": str(run_id)}
                )
                self.logger.info(f"Successfully updated trace '{self.last_trace_id}' with metadata for run_id '{run_id}'.")
            else:
                self.logger.warning(f"Could not find 'last_trace_id' for run_id '{run_id}'. Metadata will not be updated.")

        except Exception as e:
            self.logger.error(f"Failed to process run_id '{run_id}' in RunIdCallbackHandler: {e}", exc_info=True)

        return run

class AsyncRunIdCallbackHandler(AsyncLangfuseCallbackHandler):
    """
    A custom asynchronous callback handler that captures the Langchain run_id
    and adds it to the Langfuse trace metadata.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_trace_map = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("AsyncRunIdCallbackHandler initialized.")

    async def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        self.logger.debug(f"Async on_chain_start triggered for run_id: {run_id}")
        # First, let the base handler do its work
        run = await super().on_chain_start(serialized, inputs, run_id, **kwargs)
        self.logger.debug(f"Async base handler's on_chain_start completed. Current trace_id: {self.last_trace_id}")
        
        try:
            if self.last_trace_id:
                self.run_trace_map[str(run_id)] = self.last_trace_id
                self.logger.info(f"Async: Mapping run_id '{run_id}' to trace_id '{self.last_trace_id}'.")

                langfuse_client = get_client()
                langfuse_client.update_current_trace(
                    metadata={"langchain_run_id": str(run_id)}
                )
                self.logger.info(f"Async: Successfully updated trace '{self.last_trace_id}' with metadata for run_id '{run_id}'.")
            else:
                self.logger.warning(f"Async: Could not find 'last_trace_id' for run_id '{run_id}'. Metadata will not be updated.")

        except Exception as e:
            self.logger.error(f"Async: Failed to process run_id '{run_id}' in AsyncRunIdCallbackHandler: {e}", exc_info=True)

        return run
