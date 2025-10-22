
from typing import Dict, List, Optional
import time
import logging
from matrice_common.session import Session
from matrice_inference.server.stream.utils import CameraConfig


class AppDeployment:
    """Handles app deployment configuration and camera setup for streaming pipeline."""
    
    def __init__(self, session: Session, app_deployment_id: str, connection_timeout: int = 1200):  # Increased from 300 to 1200
        self.app_deployment_id = app_deployment_id
        self.rpc = session.rpc
        self.session = session
        self.connection_timeout = connection_timeout
        self.logger = logging.getLogger(__name__)
    
    def get_input_topics(self) -> List[Dict]:
        """Get input topics for the app deployment."""
        try:
            response = self.rpc.get(f"/v1/inference/get_input_topics_by_app_deployment_id/{self.app_deployment_id}")
            if response.get("success", False):
                return response.get("data", [])
            else:
                self.logger.error(f"Failed to get input topics: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            self.logger.error(f"Exception getting input topics: {str(e)}")
            return []
    
    def get_output_topics(self) -> List[Dict]:
        """Get output topics for the app deployment."""
        try:
            response = self.rpc.get(f"/v1/inference/get_output_topics_by_app_deployment_id/{self.app_deployment_id}")
            if response.get("success", False):
                return response.get("data", [])
            else:
                self.logger.error(f"Failed to get output topics: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            self.logger.error(f"Exception getting output topics: {str(e)}")
            return []
    
    def get_camera_configs(self) -> Dict[str, CameraConfig]:
        """
        Get camera configurations for the streaming pipeline.
        
        Returns:
            Dict[str, CameraConfig]: Dictionary mapping camera_id to CameraConfig
        """
        camera_configs = {}
        
        try:
            # Get input and output topics
            input_topics = self.get_input_topics()
            output_topics = self.get_output_topics()
            
            if not input_topics:
                self.logger.warning("No input topics found for app deployment")
                return camera_configs
            
            # Create mapping of camera_id to output topic
            output_topic_map = {}
            for output_topic in output_topics:
                camera_id = output_topic.get("cameraId")
                if camera_id:
                    output_topic_map[camera_id] = output_topic
            
            # Process each input topic to create camera config
            for input_topic in input_topics:
                try:
                    camera_id = input_topic.get("cameraId")
                    if not camera_id:
                        self.logger.warning("Input topic missing camera ID, skipping")
                        continue
                    
                    # Get corresponding output topic
                    output_topic = output_topic_map.get(camera_id)
                    if not output_topic:
                        self.logger.warning(f"No output topic found for camera {camera_id}, skipping")
                        continue
                    
                    # Get connection info for this server
                    server_id = input_topic.get("serverId")
                    server_type = input_topic.get("serverType", "redis").lower()
                    
                    if not server_id:
                        self.logger.warning(f"No server ID found for camera {camera_id}, skipping")
                        continue
                    
                    connection_info = self.get_and_wait_for_connection_info(server_type, server_id)
                    if not connection_info:
                        self.logger.error(f"Could not get connection info for camera {camera_id}, skipping")
                        continue
                    
                    # Create stream config
                    stream_config = connection_info.copy()
                    stream_config["stream_type"] = server_type
                    
                    # Create camera config
                    camera_config = CameraConfig(
                        camera_id=camera_id,
                        input_topic=input_topic.get("topicName"),
                        output_topic=output_topic.get("topicName"),
                        stream_config=stream_config,
                        enabled=True
                    )
                    
                    camera_configs[camera_id] = camera_config
                    self.logger.info(f"Created camera config for {camera_id} using {server_type}")
                    
                except Exception as e:
                    self.logger.error(f"Error creating config for camera {camera_id}: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully created {len(camera_configs)} camera configurations")
            return camera_configs
            
        except Exception as e:
            self.logger.error(f"Error getting camera configs: {str(e)}")
            return camera_configs
    
    def get_and_wait_for_connection_info(self, server_type: str, server_id: str) -> Optional[Dict]:
        """Get the connection information for the streaming gateway."""
        def _get_kafka_connection_info():
            try:
                response = self.rpc.get(f"/v1/actions/get_kafka_server/{server_id}")
                if response.get("success", False):
                    data = response.get("data")
                    if (
                        data
                        and data.get("ipAddress")
                        and data.get("port")
                        and data.get("status") == "running"
                    ):
                        return {
                            'bootstrap_servers': f'{data["ipAddress"]}:{data["port"]}',
                            'sasl_mechanism': 'SCRAM-SHA-256',
                            'sasl_username': 'matrice-sdk-user',
                            'sasl_password': 'matrice-sdk-password',
                            'security_protocol': 'SASL_PLAINTEXT'
                        }
                    else:
                        self.logger.debug("Kafka connection information is not complete, waiting...")
                        return None
                else:
                    self.logger.debug("Failed to get Kafka connection information: %s", response.get("message", "Unknown error"))
                    return None
            except Exception as exc:
                self.logger.debug("Exception getting Kafka connection info: %s", str(exc))
                return None

        def _get_redis_connection_info():
            try:
                response = self.rpc.get(f"/v1/actions/redis_servers/{server_id}")
                if response.get("success", False):
                    data = response.get("data")
                    if (
                        data
                        and data.get("host")
                        and data.get("port")
                        and data.get("status") == "running"
                    ):
                        return {
                            'host': data["host"],
                            'port': int(data["port"]),
                            'password': data.get("password", ""),
                            'username': data.get("username"),
                            'db': data.get("db", 0),
                            'connection_timeout': 120  # Increased from 30 to 120
                        }
                    else:
                        self.logger.debug("Redis connection information is not complete, waiting...")
                        return None
                else:
                    self.logger.debug("Failed to get Redis connection information: %s", response.get("message", "Unknown error"))
                    return None
            except Exception as exc:
                self.logger.debug("Exception getting Redis connection info: %s", str(exc))
                return None

        start_time = time.time()
        last_log_time = 0
        
        while True:
            current_time = time.time()
            
            # Get connection info based on server type
            connection_info = None
            if server_type == "kafka":
                connection_info = _get_kafka_connection_info()
            elif server_type == "redis":
                connection_info = _get_redis_connection_info()
            else:
                raise ValueError(f"Unsupported server type: {server_type}")
            
            # If we got valid connection info, return it
            if connection_info:
                self.logger.info("Successfully retrieved %s connection information", server_type)
                return connection_info
            
            # Check timeout
            if current_time - start_time > self.connection_timeout:
                error_msg = f"Timeout waiting for {server_type} connection information after {self.connection_timeout} seconds"
                self.logger.error(error_msg)
                
                # Log the last response for debugging
                try:
                    if server_type == "kafka":
                        response = self.rpc.get(f"/v1/actions/get_kafka_server/{server_id}")
                    else:
                        response = self.rpc.get(f"/v1/actions/redis_servers/{server_id}")
                    self.logger.error("Last response received: %s", response)
                except Exception as exc:
                    self.logger.error("Failed to get last response for debugging: %s", str(exc))
                
                return None  # Return None instead of raising exception to allow graceful handling
            
            # Log waiting message every 10 seconds to avoid spam
            if current_time - last_log_time >= 10:
                elapsed = current_time - start_time
                remaining = self.connection_timeout - elapsed
                self.logger.info("Waiting for %s connection information... (%.1fs elapsed, %.1fs remaining)", 
                           server_type, elapsed, remaining)
                last_log_time = current_time
            
            time.sleep(1)