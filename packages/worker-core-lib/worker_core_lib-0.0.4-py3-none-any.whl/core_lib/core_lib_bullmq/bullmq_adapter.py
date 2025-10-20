"""
BullMQ adapter implementation of the WorkerBackendPort.

This adapter provides BullMQ-specific implementation for queue and worker
operations, maintaining compatibility with existing BullMQ-based code.
"""
import logging
from typing import Any, Dict, Optional, Callable

from bullmq import Queue, Worker
from redis.asyncio import Redis

from .worker_backend_port import WorkerBackendPort
from ..core_lib_config.settings import get_settings

logger = logging.getLogger(__name__)


class BullMQAdapter(WorkerBackendPort):
    """
    BullMQ implementation of the WorkerBackendPort interface.
    
    This adapter wraps BullMQ Queue and Worker functionality, providing
    a standardized interface for queue operations while maintaining all
    BullMQ-specific features and optimizations.
    """

    def __init__(self):
        """Initialize the BullMQ adapter with Redis connection."""
        self._redis_url: Optional[str] = None
        self._redis_client: Optional[Redis] = None
        self._queue_cache: Dict[str, Queue] = {}
        logger.info("BullMQAdapter initialized")

    def _get_redis_url(self) -> str:
        """Get or create Redis URL from settings."""
        if self._redis_url is None:
            settings = get_settings()
            self._redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
            logger.info(f"Initialized Redis URL: {self._redis_url}")
        return self._redis_url

    def _get_redis_client(self) -> Redis:
        """Get or create Redis client instance."""
        if self._redis_client is None:
            redis_url = self._get_redis_url()
            logger.info(f"Creating Redis client for URL: {redis_url}")
            self._redis_client = Redis.from_url(redis_url, decode_responses=False)
        return self._redis_client

    def _get_queue(self, queue_name: str) -> Queue:
        """
        Get or create a BullMQ Queue instance.
        
        Queues are cached to maintain connection context and prevent
        connection loss issues with the BullMQ library.
        
        Args:
            queue_name: Name of the queue
            
        Returns:
            BullMQ Queue instance
        """
        if queue_name not in self._queue_cache:
            logger.info(f"Creating and caching new BullMQ Queue instance for '{queue_name}'")
            redis_client = self._get_redis_client()
            self._queue_cache[queue_name] = Queue(queue_name, {"connection": redis_client})
        
        return self._queue_cache[queue_name]

    async def add_job(
        self, 
        queue_name: str, 
        job_name: str, 
        data: Dict[str, Any], 
        opts: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a job to a BullMQ queue.

        Args:
            queue_name: Name of the queue to add the job to
            job_name: Name/type of the job
            data: Job data/payload
            opts: Optional job options (priority, delay, etc.)

        Returns:
            Job ID as a string

        Raises:
            Exception: If job addition fails
        """
        try:
            queue = self._get_queue(queue_name)
            logger.debug(f"Adding job '{job_name}' to queue '{queue_name}'")
            
            job = await queue.add(job_name, data, opts or {})
            
            logger.info(f"Job '{job_name}' added to queue '{queue_name}' with ID: {job.id}")
            return job.id

        except Exception as e:
            logger.error(f"Failed to add job to queue '{queue_name}'", exc_info=True)
            raise e

    async def create_worker(
        self,
        queue_name: str,
        processor: Callable[[Any, str], Any],
        connection_config: Optional[Dict[str, Any]] = None
    ) -> Worker:
        """
        Create a BullMQ Worker instance for processing jobs.

        Args:
            queue_name: Name of the queue to process jobs from
            processor: Async function to process jobs (receives job and token)
            connection_config: Optional connection configuration (defaults to Redis URL)

        Returns:
            BullMQ Worker instance

        Raises:
            Exception: If worker creation fails
        """
        try:
            # Use provided connection config or default to Redis URL
            connection = connection_config or {"connection": self._get_redis_url()}
            
            logger.info(f"Creating BullMQ Worker for queue: {queue_name}")
            worker = Worker(queue_name, processor, connection)
            
            return worker

        except Exception as e:
            logger.error(f"Failed to create worker for queue '{queue_name}'", exc_info=True)
            raise e

    async def close_worker(self, worker: Worker) -> None:
        """
        Close a BullMQ Worker instance and clean up resources.

        Args:
            worker: The BullMQ Worker instance to close

        Raises:
            Exception: If worker closure fails
        """
        try:
            if worker and not worker.closed:
                await worker.close()
                logger.info(f"Worker closed successfully")
        except Exception as e:
            logger.error("Failed to close worker", exc_info=True)
            raise e

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information for the BullMQ backend.

        Returns:
            Dictionary containing Redis connection details
        """
        settings = get_settings()
        return {
            "backend": "bullmq",
            "redis_url": self._get_redis_url(),
            "redis_host": settings.REDIS_HOST,
            "redis_port": settings.REDIS_PORT,
        }
