import logging
import numpy as np
import requests
import time
from typing import Tuple, Any, List, Union
from matrice_inference.server.model.triton_server import TritonServer, TritonInference

class TritonModelManager:
    """Model manager for Triton Inference Server, aligned with pipeline and inference interface."""

    def __init__(
        self,
        model_name: str,
        model_path: str,
        runtime_framework: str,
        internal_server_type: str,
        internal_port: int,
        internal_host: str,
        input_size: Union[int, List[int]] = 640, # Priority Obj det
        num_classes: int = 10,
        num_model_instances: int = 1,
        use_dynamic_batching: bool = False,
        max_batch_size: int = 8,
        is_yolo: bool = False,
        is_ocr: bool = False,
        use_trt_accelerator: bool = False,
    ):
        try:
            if internal_server_type not in ["rest", "grpc"]:
                logging.warning(f"Invalid internal_server_type '{internal_server_type}', defaulting to 'rest'")

            self.internal_server_type = internal_server_type
            self.internal_port = internal_port
            self.internal_host = internal_host
            self.use_dynamic_batching = use_dynamic_batching
            self.max_batch_size = max_batch_size

            self.triton_server = TritonServer(
                model_name=model_name,
                model_path=model_path,
                runtime_framework=runtime_framework,
                input_size=input_size,
                num_classes=num_classes,
                dynamic_batching=use_dynamic_batching,
                num_model_instances=num_model_instances,
                max_batch_size=max_batch_size,
                connection_protocol=internal_server_type,
                is_yolo=is_yolo,
                is_ocr=is_ocr,
                use_trt_accelerator=use_trt_accelerator,
            )
            
            logging.info(f"Starting Triton server on {internal_host}:{internal_port}...")
            self.triton_server_process = self.triton_server.setup(internal_port)

            logging.info("Waiting for Triton server to be ready...")
            self._wait_for_ready()

            self.client = TritonInference(
                server_type=self.triton_server.connection_protocol,
                model_name=model_name,
                internal_port=internal_port,
                internal_host=internal_host,
                runtime_framework=self.triton_server.runtime_framework,
                is_yolo = self.triton_server.is_yolo,
                input_size=input_size,
            )
            
            logging.info(f"Initialized TritonModelManager with {num_model_instances} client instances, protocol: {self.triton_server.connection_protocol}")
            
        except Exception as e:
            logging.error(f"Failed to initialize TritonModelManager: {str(e)}", exc_info=True)
            raise

    def _wait_for_ready(self):
        """Wait for Triton server to be ready with fixed retries and 5s sleep."""
        max_attempts = 30  # 150 seconds wait time
        for attempt in range(max_attempts):
            try:
                if self.internal_server_type == "rest":
                    response = requests.get(
                        f"http://{self.internal_host}:{self.internal_port}/v2/health/ready",
                        timeout=5
                    )
                    if response.status_code == 200:
                        logging.info("=========  Triton server is ready (REST) =========")
                        break
                    else:
                        logging.info(f"Attempt {attempt + 1}/{max_attempts} - server not ready, retrying in 5 seconds...")
                        time.sleep(5)

                else:  # gRPC
                    try:
                        import tritonclient.grpc as grpcclient
                    except ImportError:
                        grpcclient = None

                    if grpcclient is None:
                        raise ImportError("tritonclient.grpc required for gRPC")

                    with grpcclient.InferenceServerClient(f"{self.internal_host}:{self.internal_port}") as client:
                        if client.is_server_ready():
                            logging.info("=========  Triton server is ready (gRPC) =========")
                            break
                        else:
                            logging.info(f"Attempt {attempt + 1}/{max_attempts} - server not ready, retrying in 5 seconds...")
                            time.sleep(5)

            except Exception as e:
                if attempt < max_attempts - 1:
                    logging.info(f"Attempt {attempt + 1}/{max_attempts} failed, retrying in 5 seconds... (Error: {str(e)})")
                    time.sleep(5)
                else:
                    logging.error("Triton server failed to become ready after maximum attempts")
                    raise

    def inference(
        self,
        input: bytes,
    ) -> Tuple[Any, bool]:
        """Perform synchronous single inference using TritonInference client.

        Args:
            input: Primary input data (e.g., image bytes).
        
        Returns:
            Tuple of (results, success_flag).
        """
        if input is None:
            raise ValueError("Input data cannot be None")
        try:
            client = self.client
            if not client:
                raise RuntimeError("No Triton client available")
            results = client.inference(input)
            results = client.format_response(results)
            return results, True
        except Exception as e:
            logging.error(f"Triton sync inference failed for: {str(e)}", exc_info=True)
            return None, False

    async def async_inference(
        self,
        input: Union[bytes, np.ndarray],
    ) -> Tuple[Any, bool]:
        """Perform asynchronous single inference using TritonInference client.
        Args:
            input: Primary input data (Image bytes or numpy array).
        
        Returns:
            Tuple of (results, success_flag).
        """
        

        if input is None:
            logging.error("Input data cannot be None")
            raise ValueError("Input data cannot be None")
        try:
            client = self.client
            if not client:
                logging.error("No Triton client available")
                raise RuntimeError("No Triton client available")
            results = await client.async_inference(input)
            results = client.format_response(results)
            logging.info(f"Async inference result: {results}")
            return results, True
        except Exception as e:
            logging.error(f"Triton async inference failed: {e}")
            return {"error": str(e), "predictions": None}, False

    def batch_inference(
        self,
        input: List[bytes],
    ) -> Tuple[List[Any], bool]:
        """Perform synchronous batch inference using TritonInference client.

        Args:
            input: List of primary input data (e.g., image bytes).
        
        Returns:
            Tuple of (results_list, success_flag).
        """
        if not input:
            raise ValueError("Batch input cannot be None")
        try:
            client = self.client
            if not client:
                raise RuntimeError("No Triton client available")
            results = []

            if self.use_dynamic_batching:
                input_array = self._preprocess_batch_inputs(input, client)
                batch_results = client.inference(input_array)
                results = self._split_batch_results(batch_results, len(input))
            else:
                for inp in input:
                    result = client.inference(inp)
                    results.append(result)

            results = [client.format_response(result) for result in results]
            return results, True
        except Exception as e:
            logging.error(f"Triton sync batch inference failed for: {str(e)}", exc_info=True)
            return None, False

    async def async_batch_inference(
        self,
        input: List[bytes],
    ) -> Tuple[List[Any], bool]:
        """Perform asynchronous batch inference using TritonInference client.

        Args:
            input: List of primary input data (e.g., image bytes).

        Returns:
            Tuple of (results_list, success_flag).
        """
        if not input:
            raise ValueError("Batch input cannot be None")
        try:
            client = self.client
            if not client:
                raise RuntimeError("No Triton client available")
            results = []

            if self.use_dynamic_batching:
                input_array = self._preprocess_batch_inputs(input, client)
                batch_results = await client.async_inference(input_array)
                split_results = self._split_batch_results(batch_results, len(input))
                results = [client.format_response(r) for r in split_results]
            else:
                for inp in input:
                    res = await client.async_inference(inp)
                    results.append(client.format_response(res))

            return results, True
        except Exception as e:
            logging.error(f"Triton async batch inference failed for: {str(e)}", exc_info=True)
            return None, False
        
    def _preprocess_batch_inputs(self, input: List[bytes], client: TritonInference) -> np.ndarray:
        """Preprocess batch inputs for Triton dynamic batching.

        Args:
            input: List of input data (e.g., image bytes).
            client: TritonInference client for shape and data type information.

        Returns:
            Preprocessed NumPy array for batch inference.
        """
        try:
            batch_inputs = []
            for inp in input:
                arr = client._preprocess_input(inp)

                if arr.ndim == 4 and arr.shape[0] == 1:
                    arr = np.squeeze(arr, axis=0)

                if arr.ndim != 3:
                    logging.warning(f"Unexpected input shape {arr.shape}, expected (C,H,W) after preprocessing")

                batch_inputs.append(arr)

            # Stack into final batch (B, C, H, W)
            stacked = np.stack(batch_inputs, axis=0)
            # Ensure C-contiguous (important for Triton)
            return np.ascontiguousarray(stacked)

        except Exception as e:
            logging.error(f"Failed to preprocess batch inputs: {str(e)}", exc_info=True)
            raise


    def _split_batch_results(self, batch_results: np.ndarray, batch_size: int) -> List[Any]:
        """Split batch results into individual results.

        Args:
            batch_results: NumPy array of batch inference results.
            batch_size: Number of inputs in the batch.

        Returns:
            List of individual results.
        """
        try:
            if batch_results.ndim == 1:
                return [batch_results] * batch_size
            return [batch_results[i] for i in range(batch_size)]
        except Exception as e:
            logging.error(f"Failed to split batch results: {str(e)}", exc_info=True)
            raise