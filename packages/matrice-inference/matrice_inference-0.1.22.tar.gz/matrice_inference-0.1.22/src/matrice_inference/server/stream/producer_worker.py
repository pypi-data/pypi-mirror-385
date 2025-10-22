import asyncio
import json
import logging
import queue
import threading
import time
from typing import Any, Dict, Optional

from matrice_common.stream.matrice_stream import MatriceStream
from matrice_inference.server.stream.utils import CameraConfig

class ProducerWorker:
    """Handles message production to streams with clean resource management."""

    DEFAULT_DB = 0

    def __init__(
        self,
        worker_id: int,
        output_queue: queue.PriorityQueue,
        camera_configs: Dict[str, CameraConfig],
        message_timeout: float
    ):
        self.worker_id = worker_id
        self.output_queue = output_queue
        self.camera_configs = camera_configs
        self.message_timeout = message_timeout
        self.running = False
        self.producer_streams: Dict[str, MatriceStream] = {}
        self.logger = logging.getLogger(f"{__name__}.producer.{worker_id}")
    
    def start(self) -> threading.Thread:
        """Start the producer worker in a separate thread."""
        self.running = True
        thread = threading.Thread(
            target=self._run,
            name=f"ProducerWorker-{self.worker_id}",
            daemon=False
        )
        thread.start()
        return thread
    
    def stop(self):
        """Stop the producer worker."""
        self.running = False
    
    def _run(self) -> None:
        """Main producer loop with proper resource management."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.logger.info(f"Started producer worker {self.worker_id}")

        try:
            loop.run_until_complete(self._initialize_streams())
            self._process_messages(loop)
        except Exception as e:
            self.logger.error(f"Fatal error in producer worker: {e}")
        finally:
            self._cleanup_resources(loop)

    def _process_messages(self, loop: asyncio.AbstractEventLoop) -> None:
        """Main message processing loop."""
        while self.running:
            try:
                task = self._get_task_from_queue()
                if task:
                    loop.run_until_complete(self._send_message_safely(task))
            except Exception as e:
                self.logger.error(f"Producer error: {e}")
                time.sleep(0.1)

    def _get_task_from_queue(self) -> Optional[Dict[str, Any]]:
        """Get task from output queue with timeout handling."""
        try:
            priority, timestamp, task_data = self.output_queue.get(timeout=self.message_timeout)
            return task_data
        except queue.Empty:
            return None
        except Exception as e:
            self.logger.error(f"Error getting task from queue: {e}")
            return None

    def _cleanup_resources(self, loop: asyncio.AbstractEventLoop) -> None:
        """Clean up streams and event loop resources."""
        for stream in self.producer_streams.values():
            try:
                loop.run_until_complete(stream.async_close())
            except Exception as e:
                self.logger.error(f"Error closing producer stream: {e}")

        try:
            loop.close()
        except Exception as e:
            self.logger.error(f"Error closing event loop: {e}")

        self.logger.info(f"Producer worker {self.worker_id} stopped")

    async def _initialize_streams(self) -> None:
        """Initialize producer streams for all cameras with proper error handling."""
        try:
            from matrice_common.stream.matrice_stream import MatriceStream, StreamType

            for camera_id, camera_config in self.camera_configs.items():
                try:
                    await self._initialize_camera_stream(camera_id, camera_config, StreamType)
                except Exception as e:
                    self.logger.error(f"Failed to initialize producer stream for camera {camera_id}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to initialize producer streams: {e}")
            raise

    async def _initialize_camera_stream(
        self, camera_id: str, camera_config: CameraConfig, StreamType: Any
    ) -> None:
        """Initialize producer stream for a single camera."""
        from matrice_common.stream.matrice_stream import MatriceStream

        stream_type = self._get_stream_type(camera_config.stream_config, StreamType)
        stream_params = self._build_stream_params(camera_config.stream_config, stream_type, StreamType)

        producer_stream = MatriceStream(stream_type, **stream_params)
        await producer_stream.async_setup(camera_config.output_topic)
        self.producer_streams[camera_id] = producer_stream

        self.logger.info(
            f"Initialized {stream_type.value} producer stream for camera {camera_id} in worker {self.worker_id}"
        )

    def _get_stream_type(self, stream_config: Dict[str, Any], StreamType: Any) -> Any:
        """Determine stream type from configuration."""
        stream_type_str = stream_config.get("stream_type", "kafka").lower()
        return StreamType.KAFKA if stream_type_str == "kafka" else StreamType.REDIS

    def _build_stream_params(self, stream_config: Dict[str, Any], stream_type: Any, StreamType: Any) -> Dict[str, Any]:
        """Build stream parameters based on type."""
        if stream_type == StreamType.KAFKA:
            return {
                "bootstrap_servers": stream_config.get("bootstrap_servers", "localhost:9092"),
                "sasl_username": stream_config.get("sasl_username", "matrice-sdk-user"),
                "sasl_password": stream_config.get("sasl_password", "matrice-sdk-password"),
                "sasl_mechanism": stream_config.get("sasl_mechanism", "SCRAM-SHA-256"),
                "security_protocol": stream_config.get("security_protocol", "SASL_PLAINTEXT"),
            }
        else:
            return {
                "host": stream_config.get("host", "localhost"),
                "port": stream_config.get("port", 6379),
                "password": stream_config.get("password"),
                "username": stream_config.get("username"),
                "db": stream_config.get("db", self.DEFAULT_DB),
            }
    
    async def _send_message_safely(self, task_data: Dict[str, Any]) -> None:
        """Send message to the appropriate stream with validation and error handling."""
        try:
            if not self._validate_task_data(task_data):
                return

            camera_id = task_data["camera_id"]

            if not self._validate_camera_availability(camera_id):
                return

            await self._send_message_to_stream(task_data, camera_id)

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    def _validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate that task data contains required fields."""
        required_fields = ["camera_id", "message_key", "data"]
        for field in required_fields:
            if field not in task_data:
                self.logger.error(f"Missing required field '{field}' in task data")
                return False
        return True

    def _validate_camera_availability(self, camera_id: str) -> bool:
        """Validate that camera and its stream are available."""
        if camera_id not in self.producer_streams or camera_id not in self.camera_configs:
            self.logger.warning(f"Camera {camera_id} not found in producer streams or configs")
            return False

        camera_config = self.camera_configs[camera_id]
        if not camera_config.enabled:
            self.logger.debug(f"Camera {camera_id} is disabled, skipping message")
            return False

        return True

    async def _send_message_to_stream(self, task_data: Dict[str, Any], camera_id: str) -> None:
        """Send message to the stream for the specified camera."""
        producer_stream = self.producer_streams[camera_id]
        camera_config = self.camera_configs[camera_id]

        await producer_stream.async_add_message(
            camera_config.output_topic,
            json.dumps(task_data["data"]),
            key=task_data["message_key"]
        )

