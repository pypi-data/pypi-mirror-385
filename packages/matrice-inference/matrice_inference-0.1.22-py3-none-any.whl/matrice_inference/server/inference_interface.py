from matrice_inference.server.model.model_manager_wrapper import ModelManagerWrapper
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime, timezone
import logging
import time
from matrice_analytics.post_processing.post_processor import PostProcessor

class InferenceInterface:
    """Interface for proxying requests to model servers with optional post-processing."""

    def __init__(
        self,
        model_manager: ModelManagerWrapper,
        post_processor: Optional[PostProcessor] = None,
    ):
        """
        Initialize the inference interface.

        Args:
            model_manager: Model manager for model inference
            post_processor: Post processor for post-processing
        """
        self.logger = logging.getLogger(__name__)
        self.model_manager = model_manager
        self.post_processor = post_processor
        self.latest_inference_time = datetime.now(timezone.utc)

    def get_latest_inference_time(self) -> datetime:
        """Get the latest inference time."""
        return self.latest_inference_time
    
    async def inference(
        self,
        input: Any,
        extra_params: Optional[Dict[str, Any]] = None,
        apply_post_processing: bool = False,
        post_processing_config: Optional[Union[Dict[str, Any], str]] = None,
        stream_key: Optional[str] = None,
        stream_info: Optional[Dict[str, Any]] = None,
        camera_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, Optional[Dict[str, Any]]]:
        """Perform inference using the appropriate client with optional post-processing.
        
        Args:
            input: Primary input data (e.g., image bytes, numpy array)
            extra_params: Additional parameters for inference (optional)
            apply_post_processing: Whether to apply post-processing
            post_processing_config: Configuration for post-processing
            stream_key: Unique identifier for the input stream
            stream_info: Additional metadata about the stream (optional)
            camera_info: Additional metadata about the camera/source (optional)

        Returns:
            A tuple containing:
                - The inference results (raw or post-processed)
                - Metadata about the inference and post-processing (if applicable)
        """
        if input is None:
            raise ValueError("Input cannot be None")
        
        # Measure model inference time
        model_start_time = time.time()
        
        # Update latest inference time
        self.latest_inference_time = datetime.now(timezone.utc)
        
        # Run model inference
        try:
            raw_results, success = self.model_manager.inference(
                input=input,
                extra_params=extra_params,
                stream_key=stream_key,
                stream_info=stream_info
            )
            model_inference_time = time.time() - model_start_time
            
            if not success:
                raise RuntimeError("Model inference failed")
                
            self.logger.debug(
                f"Model inference executed stream_key={stream_key} time={model_inference_time:.4f}s"
            )
            
        except Exception as exc:
            self.logger.error(f"Model inference failed: {str(exc)}", exc_info=True)
            raise RuntimeError(f"Model inference failed: {str(exc)}") from exc
        
        # If no post-processing requested, return raw results
        if not apply_post_processing or not self.post_processor:
            return raw_results, {
                "timing_metadata": {
                    "model_inference_time_sec": model_inference_time,
                    "post_processing_time_sec": 0.0,
                    "total_time_sec": model_inference_time,
                }
            }

        # Apply post-processing using PostProcessor
        try:
            post_processing_start_time = time.time()
            
            # Use PostProcessor.process() method directly
            result = await self.post_processor.process(
                data=raw_results,
                config=post_processing_config,  # Use stream_key as fallback if no config
                input_bytes=input if isinstance(input, bytes) else None,
                stream_key=stream_key,
                stream_info=stream_info
            )
            
            post_processing_time = time.time() - post_processing_start_time
            
            # Format the response based on PostProcessor result
            if result.is_success():
                # For face recognition use case, return empty raw results
                processed_raw_results = [] if (
                    hasattr(result, 'usecase') and result.usecase == 'face_recognition'
                ) else raw_results
                
                # Extract agg_summary from result data if available
                agg_summary = {}
                if hasattr(result, 'data') and isinstance(result.data, dict):
                    agg_summary = result.data.get("agg_summary", {})
                
                post_processing_result = {
                    "status": "success",
                    "processing_time": result.processing_time,
                    "usecase": getattr(result, 'usecase', ''),
                    "category": getattr(result, 'category', ''),
                    "summary": getattr(result, 'summary', ''),
                    "insights": getattr(result, 'insights', []),
                    "metrics": getattr(result, 'metrics', {}),
                    "predictions": getattr(result, 'predictions', []),
                    "agg_summary": agg_summary,
                    "stream_key": stream_key or "default_stream",
                    "timing_metadata": {
                        "model_inference_time_sec": model_inference_time,
                        "post_processing_time_sec": post_processing_time,
                        "total_time_sec": model_inference_time + post_processing_time,
                    }
                }
                
                return processed_raw_results, post_processing_result
            else:
                # Post-processing failed
                self.logger.error(f"Post-processing failed: {result.error_message}")
                return raw_results, {
                    "status": "post_processing_failed",
                    "error": result.error_message,
                    "error_type": getattr(result, 'error_type', 'ProcessingError'),
                    "processing_time": result.processing_time,
                    "processed_data": raw_results,
                    "stream_key": stream_key or "default_stream",
                    "timing_metadata": {
                        "model_inference_time_sec": model_inference_time,
                        "post_processing_time_sec": post_processing_time,
                        "total_time_sec": model_inference_time + post_processing_time,
                    }
                }
                
        except Exception as e:
            post_processing_time = time.time() - post_processing_start_time
            self.logger.error(f"Post-processing exception: {str(e)}", exc_info=True)
            
            return raw_results, {
                "status": "post_processing_failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "processed_data": raw_results,
                "stream_key": stream_key or "default_stream",
                "timing_metadata": {
                    "model_inference_time_sec": model_inference_time,
                    "post_processing_time_sec": post_processing_time,
                    "total_time_sec": model_inference_time + post_processing_time,
                }
            }