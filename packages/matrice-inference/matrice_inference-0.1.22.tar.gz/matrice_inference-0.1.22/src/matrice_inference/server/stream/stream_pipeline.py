"""
Streaming pipeline using MatriceStream and updated inference interface:
Direct processing with priority queues, dynamic camera configuration

Architecture:
Consumer workers (threading) -> Priority Queue -> Inference workers (threading) -> 
Priority Queue -> Post-processing workers (threading) -> Priority Queue -> Producer workers (threading)

Features:
- Start without initial configuration
- Dynamic camera configuration while running
- Support for both Kafka and Redis streams
- Integration with updated InferenceInterface and PostProcessor
- Maximum throughput with direct processing
- Low latency with no batching delays  
- Multi-camera support with topic routing
- Thread-based parallelism for inference and post-processing
- Non-blocking threading for consumers/producers
"""

import logging
import queue
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from matrice_analytics.post_processing.post_processor import PostProcessor
from matrice_inference.server.inference_interface import InferenceInterface
from matrice_inference.server.stream.consumer_worker import ConsumerWorker
from matrice_inference.server.stream.inference_worker import InferenceWorker
from matrice_inference.server.stream.post_processing_worker import PostProcessingWorker
from matrice_inference.server.stream.producer_worker import ProducerWorker
from matrice_inference.server.stream.utils import CameraConfig



class StreamingPipeline:
    """Optimized streaming pipeline with dynamic camera configuration and clean resource management."""

    DEFAULT_QUEUE_SIZE = 5000
    DEFAULT_MESSAGE_TIMEOUT = 10.0
    DEFAULT_INFERENCE_TIMEOUT = 30.0
    DEFAULT_SHUTDOWN_TIMEOUT = 30.0

    def __init__(
        self,
        inference_interface: InferenceInterface,
        post_processor: PostProcessor,
        inference_queue_maxsize: int = DEFAULT_QUEUE_SIZE,
        postproc_queue_maxsize: int = DEFAULT_QUEUE_SIZE,
        output_queue_maxsize: int = DEFAULT_QUEUE_SIZE,
        message_timeout: float = DEFAULT_MESSAGE_TIMEOUT,
        inference_timeout: float = DEFAULT_INFERENCE_TIMEOUT,
        shutdown_timeout: float = DEFAULT_SHUTDOWN_TIMEOUT,
        camera_configs: Optional[Dict[str, CameraConfig]] = None,
    ):
        self.inference_interface = inference_interface
        self.post_processor = post_processor
        self.message_timeout = message_timeout
        self.inference_timeout = inference_timeout
        self.shutdown_timeout = shutdown_timeout

        self.camera_configs: Dict[str, CameraConfig] = camera_configs or {}
        self.running = False
        self.logger = logging.getLogger(__name__)

        self._setup_queues(inference_queue_maxsize, postproc_queue_maxsize, output_queue_maxsize)
        self._setup_executors()
        self._setup_workers()
        # Frame cache instance (initialized lazily at start)
        self.frame_cache = None

    def _setup_queues(self, inference_size: int, postproc_size: int, output_size: int) -> None:
        """Initialize priority queues for pipeline stages."""
        self.inference_queue = queue.PriorityQueue(maxsize=inference_size)
        self.postproc_queue = queue.PriorityQueue(maxsize=postproc_size)
        self.output_queue = queue.PriorityQueue(maxsize=output_size)

    def _setup_executors(self) -> None:
        """Initialize thread pool executors."""
        # Single-thread executors to preserve strict ordering
        self.inference_executor = ThreadPoolExecutor(max_workers=1)
        self.postprocessing_executor = ThreadPoolExecutor(max_workers=1)

    def _setup_workers(self) -> None:
        """Initialize worker containers."""
        self.consumer_workers: Dict[str, List[ConsumerWorker]] = {}
        self.inference_workers: List = []
        self.postproc_workers: List = []
        self.producer_workers: List = []
        self.worker_threads: List = []
    
    async def start(self) -> None:
        """Start the pipeline with proper error handling."""
        if self.running:
            self.logger.warning("Pipeline already running")
            return

        self.running = True
        self.logger.info("Starting streaming pipeline...")

        try:
            # Initialize frame cache before workers
            self._initialize_frame_cache()
            await self._create_workers()
            self._start_workers()
            self._log_startup_info()
        except Exception as e:
            self.logger.error(f"Failed to start pipeline: {e}")
            await self.stop()
            raise

    def _log_startup_info(self) -> None:
        """Log pipeline startup information."""
        consumer_count = sum(len(workers) for workers in self.consumer_workers.values())
        self.logger.info(
            f"Pipeline started - Cameras: {len(self.camera_configs)}, "
            f"Consumers: {consumer_count}, Inference: {len(self.inference_workers)}, "
            f"PostProc: {len(self.postproc_workers)}, Producers: {len(self.producer_workers)}"
        )
    
    async def stop(self) -> None:
        """Stop the pipeline gracefully with proper cleanup."""
        if not self.running:
            return

        self.logger.info("Stopping pipeline...")
        self.running = False

        self._stop_workers()
        self._wait_for_threads()
        self._shutdown_executors()

        # Stop frame cache if running
        try:
            if self.frame_cache:
                self.frame_cache.stop()
        except Exception:
            pass

        self.logger.info("Pipeline stopped")

    def _wait_for_threads(self) -> None:
        """Wait for all worker threads to complete."""
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=self.shutdown_timeout)

    def _shutdown_executors(self) -> None:
        """Shutdown thread pool executors."""
        self.inference_executor.shutdown(wait=False)
        self.postprocessing_executor.shutdown(wait=False)
    
    async def add_camera_config(self, camera_config: CameraConfig) -> bool:
        """
        Add a camera configuration dynamically while pipeline is running.
        
        Args:
            camera_config: Camera configuration to add
            
        Returns:
            bool: True if successfully added, False otherwise
        """
        try:
            camera_id = camera_config.camera_id
            
            if camera_id in self.camera_configs:
                self.logger.warning(f"Camera {camera_id} already exists, updating configuration")
                # Stop existing workers for this camera
                await self._stop_camera_workers(camera_id)
            
            # Add camera config
            self.camera_configs[camera_id] = camera_config
            
            # Create workers for this camera if pipeline is running
            if self.running:
                await self._create_camera_workers(camera_config)
                self._start_camera_workers(camera_id)
            
            self.logger.info(f"Successfully added camera configuration for {camera_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to add camera config for {camera_config.camera_id}: {str(e)}")
            return False
    
    async def remove_camera_config(self, camera_id: str) -> bool:
        """
        Remove a camera configuration dynamically.
        
        Args:
            camera_id: ID of camera to remove
            
        Returns:
            bool: True if successfully removed, False otherwise
        """
        try:
            if camera_id not in self.camera_configs:
                self.logger.warning(f"Camera {camera_id} does not exist")
                return False
            
            # Stop workers for this camera
            await self._stop_camera_workers(camera_id)
            
            # Remove camera config
            del self.camera_configs[camera_id]
            
            self.logger.info(f"Successfully removed camera configuration for {camera_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to remove camera config for {camera_id}: {str(e)}")
            return False
    
    async def update_camera_config(self, camera_config: CameraConfig) -> bool:
        """
        Update an existing camera configuration.
        
        Args:
            camera_config: Updated camera configuration
            
        Returns:
            bool: True if successfully updated, False otherwise
        """
        return await self.add_camera_config(camera_config)
    
    def enable_camera(self, camera_id: str) -> bool:
        """Enable a camera configuration."""
        return self._set_camera_state(camera_id, True, "enabled")

    def disable_camera(self, camera_id: str) -> bool:
        """Disable a camera configuration."""
        return self._set_camera_state(camera_id, False, "disabled")

    def _set_camera_state(self, camera_id: str, enabled: bool, state_name: str) -> bool:
        """Set camera enabled state."""
        if camera_id in self.camera_configs:
            self.camera_configs[camera_id].enabled = enabled
            self.logger.info(f"Camera {camera_id} {state_name}")
            return True
        return False
      
    
    async def _create_workers(self) -> None:
        """Create all worker instances for the pipeline."""
        await self._create_consumer_workers()
        self._create_inference_worker()
        self._create_postprocessing_worker()
        self._create_producer_worker()

    async def _create_consumer_workers(self) -> None:
        """Create consumer workers for all cameras."""
        for camera_config in self.camera_configs.values():
            await self._create_camera_workers(camera_config)

    def _create_inference_worker(self) -> None:
        """Create single inference worker."""
        worker = InferenceWorker(
            worker_id=0,
            inference_queue=self.inference_queue,
            postproc_queue=self.postproc_queue,
            inference_executor=self.inference_executor,
            message_timeout=self.message_timeout,
            inference_timeout=self.inference_timeout,
            inference_interface=self.inference_interface
        )
        self.inference_workers.append(worker)

    def _create_postprocessing_worker(self) -> None:
        """Create single post-processing worker."""
        worker = PostProcessingWorker(
            worker_id=0,
            postproc_queue=self.postproc_queue,
            output_queue=self.output_queue,
            postprocessing_executor=self.postprocessing_executor,
            message_timeout=self.message_timeout,
            inference_timeout=self.inference_timeout,
            post_processor=self.post_processor,
            frame_cache=self.frame_cache,
        )
        self.postproc_workers.append(worker)

    def _create_producer_worker(self) -> None:
        """Create single producer worker."""
        worker = ProducerWorker(
            worker_id=0,
            output_queue=self.output_queue,
            camera_configs=self.camera_configs,
            message_timeout=self.message_timeout
        )
        self.producer_workers.append(worker)
    
    async def _create_camera_workers(self, camera_config: CameraConfig) -> None:
        """Create consumer workers for a specific camera."""
        camera_id = camera_config.camera_id

        worker = ConsumerWorker(
            camera_id=camera_id,
            worker_id=0,
            stream_config=camera_config.stream_config,
            input_topic=camera_config.input_topic,
            inference_queue=self.inference_queue,
            message_timeout=self.message_timeout,
            camera_config=camera_config,
            frame_cache=self.frame_cache
        )

        self.consumer_workers[camera_id] = [worker]
    
    def _start_workers(self) -> None:
        """Start all worker instances and track their threads."""
        self._start_all_camera_workers()
        self._start_worker_group(self.inference_workers)
        self._start_worker_group(self.postproc_workers)
        self._start_worker_group(self.producer_workers)

    def _start_all_camera_workers(self) -> None:
        """Start consumer workers for all cameras."""
        for camera_id in self.consumer_workers:
            self._start_camera_workers(camera_id)

    def _start_worker_group(self, workers: List) -> None:
        """Start a group of workers and track their threads."""
        for worker in workers:
            thread = worker.start()
            self.worker_threads.append(thread)
    
    def _start_camera_workers(self, camera_id: str) -> None:
        """Start consumer workers for a specific camera."""
        if camera_id in self.consumer_workers:
            self._start_worker_group(self.consumer_workers[camera_id])
    
    def _stop_workers(self) -> None:
        """Stop all worker instances gracefully."""
        self._stop_all_camera_workers()
        self._stop_worker_group(self.inference_workers)
        self._stop_worker_group(self.postproc_workers)
        self._stop_worker_group(self.producer_workers)

    def _stop_all_camera_workers(self) -> None:
        """Stop all camera consumer workers."""
        for workers in self.consumer_workers.values():
            self._stop_worker_group(workers)

    def _stop_worker_group(self, workers: List) -> None:
        """Stop a group of workers."""
        for worker in workers:
            worker.stop()
    
    async def _stop_camera_workers(self, camera_id: str) -> None:
        """Stop consumer workers for a specific camera."""
        if camera_id in self.consumer_workers:
            self._stop_worker_group(self.consumer_workers[camera_id])
            del self.consumer_workers[camera_id]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics."""
        return {
            "running": self.running,
            "camera_count": len(self.camera_configs),
            "enabled_cameras": sum(1 for config in self.camera_configs.values() if config.enabled),
            "queue_sizes": {
                "inference": self.inference_queue.qsize(),
                "postproc": self.postproc_queue.qsize(),
                "output": self.output_queue.qsize(),
            },
            "worker_counts": {
                "consumers": sum(len(workers) for workers in self.consumer_workers.values()),
                "inference_workers": len(self.inference_workers),
                "postproc_workers": len(self.postproc_workers),
                "producers": len(self.producer_workers),
            },
            "thread_counts": {
                "total_threads": len(self.worker_threads),
                "active_threads": len([t for t in self.worker_threads if t.is_alive()]),
            },
            "camera_configs": {
                camera_id: {
                    "input_topic": config.input_topic,
                    "output_topic": config.output_topic,
                    "enabled": config.enabled,
                    "stream_type": config.stream_config.get("stream_type", "kafka")
                }
                for camera_id, config in self.camera_configs.items()
            }
        }

    def _initialize_frame_cache(self) -> None:
        """Initialize RedisFrameCache with TTL 10 minutes, deriving connection from Redis cameras if available."""
        try:
            # Find a Redis camera config for connection params
            host = "localhost"
            port = 6379
            password = None
            username = None
            db = 0

            for cfg in self.camera_configs.values():
                sc = cfg.stream_config or {}
                st = sc.get("stream_type", "kafka").lower()
                if st == "redis":
                    host = sc.get("host", host)
                    port = sc.get("port", port)
                    password = sc.get("password", password)
                    username = sc.get("username", username)
                    db = sc.get("db", db)
                    break

            # Lazy import to avoid dependency issues if not used
            from matrice_inference.server.stream.frame_cache import RedisFrameCache
            self.frame_cache = RedisFrameCache(
                host=host,
                port=port,
                db=db,
                password=password,
                username=username,
                ttl_seconds=600,  # 10 minutes
                worker_threads=1,  # conservative to avoid contention
            )
            self.frame_cache.start()
            self.logger.info("Initialized RedisFrameCache with 10-minute TTL")
        except Exception as e:
            self.frame_cache = None
            self.logger.warning(f"Frame cache initialization failed; proceeding without cache: {e}")
