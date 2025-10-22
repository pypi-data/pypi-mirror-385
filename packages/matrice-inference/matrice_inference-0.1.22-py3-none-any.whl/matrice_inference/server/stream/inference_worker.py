import asyncio
import base64
import logging
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

class InferenceWorker:
    """Handles inference processing with clean resource management and error handling."""

    def __init__(
        self,
        worker_id: int,
        inference_queue: queue.PriorityQueue,
        postproc_queue: queue.PriorityQueue,
        inference_executor: ThreadPoolExecutor,
        message_timeout: float,
        inference_timeout: float,
        inference_interface: Optional[Any] = None
    ):
        self.worker_id = worker_id
        self.inference_queue = inference_queue
        self.postproc_queue = postproc_queue
        self.inference_executor = inference_executor
        self.message_timeout = message_timeout
        self.inference_timeout = inference_timeout
        self.inference_interface = inference_interface
        self.running = False
        self.logger = logging.getLogger(f"{__name__}.inference.{worker_id}")
    
    def start(self) -> threading.Thread:
        """Start the inference worker in a separate thread."""
        self.running = True
        thread = threading.Thread(
            target=self._run,
            name=f"InferenceWorker-{self.worker_id}",
            daemon=False
        )
        thread.start()
        return thread
    
    def stop(self):
        """Stop the inference worker."""
        self.running = False
    
    def _run(self) -> None:
        """Main inference dispatcher loop with proper error handling."""
        self.logger.info(f"Started inference worker {self.worker_id}")

        try:
            while self.running:
                task = self._get_task_from_queue()
                if task:
                    self._process_inference_task(*task)
        except Exception as e:
            self.logger.error(f"Fatal error in inference worker: {e}")
        finally:
            self.logger.info(f"Inference worker {self.worker_id} stopped")

    def _get_task_from_queue(self) -> Optional[tuple]:
        """Get task from inference queue with timeout handling."""
        try:
            return self.inference_queue.get(timeout=self.message_timeout)
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Error getting task from queue: {e}")
            return None
    
    def _process_inference_task(self, priority: int, timestamp: float, task_data: Dict[str, Any]) -> None:
        """Process a single inference task with proper error handling."""
        try:
            if not self._validate_task_data(task_data):
                return

            start_time = time.time()
            result = self._execute_inference(task_data)
            processing_time = time.time() - start_time

            if result["success"]:
                postproc_task = self._create_postprocessing_task(
                    task_data, result, processing_time
                )
                self.postproc_queue.put((priority, time.time(), postproc_task))
            else:
                self.logger.error(f"Inference failed: {result['error']}")

        except Exception as e:
            self.logger.error(f"Inference task error: {e}")

    def _validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate that task data contains required fields."""
        required_fields = ["message", "input_stream", "stream_key", "camera_config"]
        for field in required_fields:
            if field not in task_data:
                self.logger.error(f"Missing required field '{field}' in task data")
                return False
        return True

    def _execute_inference(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute inference task in thread pool."""
        future = self.inference_executor.submit(self._run_inference, task_data)
        return future.result(timeout=self.inference_timeout)

    def _create_postprocessing_task(
        self, task_data: Dict[str, Any], result: Dict[str, Any], processing_time: float
    ) -> Dict[str, Any]:
        """Create post-processing task from inference result."""
        return {
            "original_message": task_data["message"],
            "model_result": result["model_result"],
            "metadata": result["metadata"],
            "processing_time": processing_time,
            "input_stream": task_data["input_stream"],
            "stream_key": task_data["stream_key"],
            "camera_config": task_data["camera_config"]
        }

    def _run_inference(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference in thread pool with proper error handling and cleanup."""
        try:
            # Extract task data - handle camera streamer format
            input_stream_data = task_data.get("input_stream", {})
            stream_key = task_data.get("stream_key")
            stream_info = input_stream_data.get("stream_info", {})
            camera_info = input_stream_data.get("camera_info", {})
            extra_params = task_data.get("extra_params", {})
            
            # Ensure extra_params is a dictionary
            if not isinstance(extra_params, dict):
                logging.warning(f"extra_params is not a dict in inference worker, converting from {type(extra_params)}: {extra_params}")
                if isinstance(extra_params, list):
                    # Convert list to dict if possible
                    if len(extra_params) == 0:
                        extra_params = {}
                    elif all(isinstance(item, dict) for item in extra_params):
                        # Merge all dictionaries in the list
                        merged_params = {}
                        for item in extra_params:
                            merged_params.update(item)
                        extra_params = merged_params
                    else:
                        extra_params = {}
                else:
                    extra_params = {}
            
            if not self.inference_interface:
                raise ValueError("Inference interface not initialized")

            inference_params = self._extract_inference_params(task_data)
            loop = self._get_or_create_event_loop()

            model_result, metadata = loop.run_until_complete(
                self.inference_interface.inference(**inference_params)
            )

            return self._create_success_result(model_result, metadata)

        except Exception as e:
            self.logger.error(f"Inference execution error: {e}", exc_info=True)
            return self._create_error_result(str(e))

    def _extract_inference_params(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate inference parameters from task data."""
        input_stream_data = task_data.get("input_stream", {})
        # Prefer decoded bytes if provided by upstream stages
        input_bytes = task_data.get("decoded_input_bytes")
        if not isinstance(input_bytes, (bytes, bytearray)):
            content = input_stream_data.get("content")
            if isinstance(content, str) and content:
                try:
                    input_bytes = base64.b64decode(content)
                except Exception as e:
                    self.logger.warning(f"Failed to decode base64 content for inference: {e}")
                    input_bytes = None
            elif isinstance(content, (bytes, bytearray)):
                input_bytes = content
            else:
                input_bytes = None

        extra_params = self._normalize_extra_params(task_data.get("extra_params", {}))

        return {
            "input": input_bytes,
            "extra_params": extra_params,
            "apply_post_processing": False,
            "stream_key": task_data.get("stream_key"),
            "stream_info": input_stream_data.get("stream_info", {}),
            "camera_info": input_stream_data.get("camera_info", {})
        }

    def _decode_input_content(self, content: Any) -> Any:
        """Decode base64 content if it's a string."""
        if content and isinstance(content, str):
            try:
                return base64.b64decode(content)
            except Exception as e:
                self.logger.warning(f"Failed to decode base64 input: {e}")
        return content

    def _normalize_extra_params(self, extra_params: Any) -> Dict[str, Any]:
        """Normalize extra_params to ensure it's a dictionary."""
        if isinstance(extra_params, dict):
            return extra_params
        elif isinstance(extra_params, list):
            return self._merge_list_params(extra_params)
        else:
            self.logger.warning(f"Invalid extra_params type {type(extra_params)}, using empty dict")
            return {}

    def _merge_list_params(self, params_list: list) -> Dict[str, Any]:
        """Merge list of dictionaries into single dictionary."""
        if not params_list:
            return {}

        if all(isinstance(item, dict) for item in params_list):
            merged = {}
            for item in params_list:
                merged.update(item)
            return merged

        return {}

    def _get_or_create_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get existing event loop or create a new one for this thread."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _create_success_result(self, model_result: Any, metadata: Any) -> Dict[str, Any]:
        """Create successful inference result."""
        return {
            "model_result": model_result,
            "metadata": metadata,
            "success": True,
            "error": None
        }

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error inference result."""
        return {
            "model_result": None,
            "metadata": None,
            "success": False,
            "error": error_message
        }

