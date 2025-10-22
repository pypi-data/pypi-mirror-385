import logging
import gc
from typing import Tuple, Any, Optional, List, Callable, Dict

class ModelManager:
    """Minimal ModelManager that focuses on model lifecycle and prediction calls."""

    def __init__(
        self,
        action_tracker: Any,
        load_model: Optional[Callable] = None,
        predict: Optional[Callable] = None,
        batch_predict: Optional[Callable] = None,
        num_model_instances: int = 1,
        model_path: Optional[str] = None, # For local model loading testing
    ):
        """Initialize the ModelManager

        Args:
            action_tracker: Tracker for monitoring actions.
            load_model: Function to load the model.
            predict: Function to run predictions.
            batch_predict: Function to run batch predictions.
            num_model_instances: Number of model instances to create.
            model_path: Path to the model directory.
        """
        try:
            self.load_model = self._create_load_model_wrapper(load_model)
            self.predict = self._create_prediction_wrapper(predict)
            self.batch_predict = self._create_prediction_wrapper(batch_predict)
            self.action_tracker = action_tracker
            
            # Model instances
            self.model_instances = []
            self._round_robin_counter = 0
            self.model_path = model_path
            
            for _ in range(num_model_instances):
                self.scale_up()
        except Exception as e:
            logging.error(f"Failed to initialize ModelManager: {str(e)}")
            raise

    def _create_load_model_wrapper(self, load_model_func: Callable):
        """Create a wrapper function that handles parameter passing to the load model function.

        Args:
            load_model_func: The load model function to wrap

        Returns:
            A wrapper function that handles parameter passing safely
        """
        if not load_model_func:
            return load_model_func

        def wrapper():
            """Wrapper that safely calls the load model function with proper parameter handling."""
            try:
                # Get function parameter names
                param_names = load_model_func.__code__.co_varnames[
                    : load_model_func.__code__.co_argcount
                ]
                
                arg_count = load_model_func.__code__.co_argcount
                
                # Handle case where function has exactly 1 argument and it's not named
                if arg_count == 1 and param_names and param_names[0] in ['_', 'arg', 'args']:
                    # Pass action_tracker as positional argument
                    if self.action_tracker is not None:
                        return load_model_func(self.action_tracker)
                    else:
                        # Try calling with no arguments if action_tracker is None
                        return load_model_func()
                
                # Handle case where function has exactly 1 argument with a recognizable name
                if arg_count == 1 and param_names:
                    param_name = param_names[0]
                    # Check if it's likely to want action_tracker
                    if param_name in ["action_tracker", "actionTracker", "tracker"]:
                        return load_model_func(self.action_tracker)
                    elif param_name in ["model_path", "path"] and self.model_path is not None:
                        return load_model_func(self.model_path)
                    else:
                        # Pass action_tracker as fallback for single argument functions
                        return load_model_func(self.action_tracker if self.action_tracker is not None else None)
                
                # Build filtered parameters based on what the function accepts (original logic for multi-param functions)
                filtered_params = {}
                
                # Add action_tracker if the function accepts it
                if self.action_tracker is not None:
                    if "action_tracker" in param_names:
                        filtered_params["action_tracker"] = self.action_tracker
                    elif "actionTracker" in param_names:
                        filtered_params["actionTracker"] = self.action_tracker
                
                # Add model_path if the function accepts it
                if "model_path" in param_names and self.model_path is not None:
                    filtered_params["model_path"] = self.model_path

                return load_model_func(**filtered_params)

            except Exception as e:
                error_msg = f"Load model function execution failed: {str(e)}"
                logging.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e

        return wrapper

    def scale_up(self):
        """Load the model into memory (scale up)"""
        try:
            self.model_instances.append(self.load_model())
            return True
        except Exception as e:
            logging.error(f"Failed to scale up model: {str(e)}")
            return False

    def scale_down(self):
        """Unload the model from memory (scale down)"""
        if not self.model_instances:
            return True
        try:
            del self.model_instances[-1]
            gc.collect()
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True
        except Exception as e:
            logging.error(f"Failed to scale down model: {str(e)}")
            return False

    def get_model(self):
        """Get the model instance in round-robin fashion"""
        if not self.model_instances:
            logging.warning("No model instances available")
            return None

        order = self._round_robin_counter % len(self.model_instances)
        # Get the current model instance
        model = self.model_instances[order]
        if not model:
            logging.error("No model instance found, will try to load model")
            self.model_instances[order] = self.load_model()
            model = self.model_instances[order]

        # Increment counter for next call
        self._round_robin_counter = (self._round_robin_counter + 1) % len(
            self.model_instances
        )

        return model

    def _create_prediction_wrapper(self, predict_func: Callable):
        """Create a wrapper function that handles parameter passing to the prediction function.

        Args:
            predict_func: The prediction function to wrap

        Returns:
            A wrapper function that handles parameter passing safely
        """

        def wrapper(model, input: bytes, extra_params: Dict[str, Any]=None, stream_key: Optional[str]=None, stream_info: Optional[Dict[str, Any]]=None) -> dict:
            """Wrapper that safely calls the prediction function with proper parameter handling."""
            try:
                # Ensure extra_params is a dictionary
                if extra_params is None:
                    extra_params = {}
                elif isinstance(extra_params, list):
                    logging.warning(f"extra_params received as list instead of dict, converting: {extra_params}")
                    # Convert list to dict if possible, otherwise use empty dict
                    if len(extra_params) == 0:
                        extra_params = {}
                    elif all(isinstance(item, dict) for item in extra_params):
                        # Merge all dictionaries in the list
                        merged_params = {}
                        for item in extra_params:
                            merged_params.update(item)
                        extra_params = merged_params
                    else:
                        logging.error(f"Cannot convert extra_params list to dict: {extra_params}")
                        extra_params = {}
                elif not isinstance(extra_params, dict):
                    logging.warning(f"extra_params is not a dict, using empty dict instead. Received: {type(extra_params)}")
                    extra_params = {}
                
                param_names = predict_func.__code__.co_varnames[
                    : predict_func.__code__.co_argcount
                ]
                filtered_params = {
                    k: v for k, v in extra_params.items() if k in param_names
                }

                # Build arguments list
                args = [model, input]

                # Add stream_key if the function accepts it (regardless of its value)
                if "stream_key" in param_names:
                    filtered_params["stream_key"] = stream_key

                if "stream_info" in param_names:
                    filtered_params["stream_info"] = stream_info

                return predict_func(*args, **filtered_params)

            except Exception as e:
                error_msg = f"Prediction function execution failed: {str(e)}"
                logging.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg) from e

        return wrapper

    def inference(self, input: bytes, extra_params: Dict[str, Any]=None, stream_key: Optional[str]=None, stream_info: Optional[Dict[str, Any]]=None) -> Tuple[dict, bool]:
        """Run inference on the provided input data.

        Args:
            input: Primary input data (can be image bytes or numpy array)
            extra_params: Additional parameters for inference (optional)
            stream_key: Stream key for the inference
            stream_info: Stream info for the inference
        Returns:
            Tuple of (results, success_flag)

        Raises:
            ValueError: If input data is invalid
        """
        if input is None:
            raise ValueError("Input data cannot be None")
        
        try:
            model = self.get_model()
            results = self.predict(model, input, extra_params, stream_key, stream_info)
            if self.action_tracker:
                results = self.action_tracker.update_prediction_results(results)
            return results, True
        except Exception as e:
            logging.error(f"Inference failed: {str(e)}")
            return None, False

    def batch_inference(
        self, input: List[bytes], extra_params: Dict[str, Any]=None, stream_key: Optional[str]=None, stream_info: Optional[Dict[str, Any]]=None
    ) -> Tuple[dict, bool]:
        """Run batch inference on the provided input data.

        Args:
            input: Primary input data
            extra_params: Additional parameters for inference (optional)
            stream_key: Stream key for the inference
            stream_info: Stream info for the inference
        Returns:
            Tuple of (results, success_flag)

        Raises:
            ValueError: If input data is invalid
        """
        if input is None:
            raise ValueError("Input data cannot be None")
        try:
            model = self.get_model()
            if not self.batch_predict:
                logging.error("Batch prediction function not found")
                return None, False
            results = self.batch_predict(model, input, extra_params, stream_key, stream_info)
            if self.action_tracker:
                for result in results:
                    self.action_tracker.update_prediction_results(result)
            return results, True
        except Exception as e:
            logging.error(f"Batch inference failed: {str(e)}")
            return None, False
        
# TODO: Add multi model execution with torch.cuda.stream()