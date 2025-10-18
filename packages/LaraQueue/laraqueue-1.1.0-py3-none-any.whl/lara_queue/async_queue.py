import asyncio
import json
import logging
import random
import signal
import sys
import time
import uuid
from collections import defaultdict, deque
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import aioredis
from aioredis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
    RedisError
)
from pyee.asyncio import AsyncIOEventEmitter

from .module import phpserialize
from .retry_strategy import RetryStrategy, RetryConfig
from .metrics_collector import MetricsCollector
from .async_metrics_collector import AsyncMetricsCollector

# Setup logger
logger = logging.getLogger(__name__)




class AsyncQueue:
    """Async queue for high loads with asyncio support."""

    def __init__(self, 
                 client: aioredis.Redis, 
                 queue: str,
                 driver: str = 'redis',
                 appname: str = 'laravel', 
                 prefix: str = '_database_', 
                 is_queue_notify: bool = True, 
                 is_horizon: bool = False,
                 dead_letter_queue: Optional[str] = None, 
                 max_retries: int = 3,
                 retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
                 retry_delay: int = 5,
                 retry_max_delay: int = 300,
                 retry_jitter: bool = True,
                 retry_backoff_multiplier: float = 2.0,
                 retry_custom_function: Optional[Callable[[int], int]] = None,
                 retry_exceptions: Optional[List[type]] = None,
                 enable_metrics: bool = True,
                 metrics_history_size: int = 1000,
                 max_concurrent_jobs: int = 10) -> None:
        self.driver = driver
        self.client = client
        self.queue = queue
        self.appname = appname
        self.prefix = prefix
        self.is_queue_notify = is_queue_notify
        self.is_horizon = is_horizon
        self.ee = AsyncIOEventEmitter()
        
        # Graceful shutdown flags
        self._shutdown = False
        self._processing_jobs = 0
        self._shutdown_handlers_registered = False
        self._max_concurrent_jobs = max_concurrent_jobs
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        
        # Dead letter queue configuration
        self.dead_letter_queue = dead_letter_queue or f"{queue}:failed"
        self.max_retries = max_retries
        self._job_retry_count = {}  # Track retry count per job
        
        # Retry configuration
        self.retry_strategy = retry_strategy
        self.retry_delay = retry_delay
        self.retry_max_delay = retry_max_delay
        self.retry_jitter = retry_jitter
        self.retry_backoff_multiplier = retry_backoff_multiplier
        self.retry_custom_function = retry_custom_function
        self.retry_exceptions = retry_exceptions or [Exception]  # Default retry for all exceptions
        
        # Retry statistics
        self._retry_stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'dead_letter_jobs': 0
        }
        
        # Metrics configuration
        self.enable_metrics = enable_metrics
        self.metrics = AsyncMetricsCollector(max_history_size=metrics_history_size) if enable_metrics else None

    async def push(self, name: str, dictObj: Dict[str, Any]) -> None:
        """Asynchronously adds a job to the queue."""
        if self.driver == 'redis':
            await self.redis_push(name, dictObj)

    async def listen(self) -> None:
        """Asynchronously listens to the queue and processes jobs."""
        if self.driver == 'redis':
            # Register shutdown handlers before starting
            if not self._shutdown_handlers_registered:
                self._register_shutdown_handlers()
            await self.redis_pop()

    def handler(self, f: Optional[Callable] = None) -> Union[Callable, Any]:
        """Decorator for registering job handlers."""
        def wrapper(f):
            self.ee._add_event_handler('queued', f, f)
        if f is None:
            return wrapper
        else:
            return wrapper(f)
    
    def _register_shutdown_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        def shutdown_handler(signum: int, frame: Any) -> None:
            signal_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else signum
            logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
            self._shutdown = True
            
            if self._processing_jobs > 0:
                logger.info(f"Waiting for {self._processing_jobs} jobs to finish...")
            else:
                logger.info("No jobs in progress, shutting down immediately")
        
        # Register handlers for SIGTERM and SIGINT
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
        
        self._shutdown_handlers_registered = True
        logger.debug("Async shutdown signal handlers registered (SIGINT, SIGTERM)")
    
    def shutdown(self) -> None:
        """Trigger graceful shutdown manually."""
        logger.info("Manual async shutdown requested")
        self._shutdown = True
    
    def _get_job_id(self, job_data: Dict[str, Any]) -> str:
        """Generate or extract job ID for retry tracking."""
        return job_data.get('uuid', str(uuid.uuid4()))
    
    def _increment_retry_count(self, job_id: str) -> int:
        """Increment retry count for a job."""
        if job_id not in self._job_retry_count:
            self._job_retry_count[job_id] = 0
        self._job_retry_count[job_id] += 1
        return self._job_retry_count[job_id]
    
    def _get_retry_count(self, job_id: str) -> int:
        """Get current retry count for a job."""
        return self._job_retry_count.get(job_id, 0)
    
    def _clear_retry_count(self, job_id: str) -> None:
        """Clear retry count for a job (on success)."""
        if job_id in self._job_retry_count:
            del self._job_retry_count[job_id]
    
    async def _send_to_dead_letter_queue(self, job_data: Dict[str, Any], error: Exception, retry_count: int) -> None:
        """Send failed job to dead letter queue."""
        try:
            dead_letter_data = {
                'original_job': job_data,
                'error': {
                    'type': type(error).__name__,
                    'message': str(error),
                    'timestamp': time.time()
                },
                'retry_count': retry_count,
                'max_retries': self.max_retries,
                'failed_at': time.time(),
                'queue': self.queue
            }
            
            dead_letter_key = f"{self.appname}{self.prefix}queues:{self.dead_letter_queue}"
            await self.client.rpush(dead_letter_key, json.dumps(dead_letter_data))
            
            # Update statistics
            self._retry_stats['dead_letter_jobs'] += 1
            
            logger.warning(f"Job sent to dead letter queue '{self.dead_letter_queue}' after {retry_count} retries")
            logger.debug(f"Dead letter data: {dead_letter_data}")
            
        except Exception as dlq_error:
            logger.error(f"Failed to send job to dead letter queue: {dlq_error}")
            logger.error(f"Original job data: {job_data}")
    
    def _should_retry(self, job_id: str, exception: Exception) -> bool:
        """Check if job should be retried based on retry count and exception type."""
        retry_count = self._get_retry_count(job_id)
        
        # Check retry count
        if retry_count >= self.max_retries:
            return False
        
        # Check exception type
        if not self._is_retryable_exception(exception):
            return False
        
        return True
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if exception type is retryable."""
        return any(isinstance(exception, exc_type) for exc_type in self.retry_exceptions)
    
    def _calculate_retry_delay(self, retry_count: int) -> int:
        """Calculate delay for retry based on strategy."""
        if self.retry_strategy == RetryStrategy.CUSTOM and self.retry_custom_function:
            delay = self.retry_custom_function(retry_count)
        elif self.retry_strategy == RetryStrategy.EXPONENTIAL:
            delay = int(self.retry_delay * (self.retry_backoff_multiplier ** (retry_count - 1)))
        elif self.retry_strategy == RetryStrategy.LINEAR:
            delay = self.retry_delay * retry_count
        elif self.retry_strategy == RetryStrategy.FIXED:
            delay = self.retry_delay
        else:
            delay = self.retry_delay
        
        # Limit by maximum delay
        delay = min(delay, self.retry_max_delay)
        
        # Add jitter to avoid thundering herd
        if self.retry_jitter:
            jitter = random.uniform(0.1, 0.3) * delay
            delay = int(delay + jitter)
        
        return max(1, delay)  # Minimum 1 second
    
    async def _retry_job(self, job_data: Dict[str, Any], retry_count: int) -> None:
        """Retry a failed job with calculated delay."""
        try:
            # Calculate delay based on retry strategy
            delay = self._calculate_retry_delay(retry_count)
            
            # Add retry metadata to job data
            job_data['retry_delay'] = delay
            job_data['retry_attempt'] = retry_count
            job_data['retry_strategy'] = self.retry_strategy.value
            job_data['retry_timestamp'] = time.time()
            
            queue_key = f"{self.appname}{self.prefix}queues:{self.queue}"
            await self.client.rpush(queue_key, json.dumps(job_data))
            
            # Update statistics
            self._retry_stats['total_retries'] += 1
            
            # Record retry in metrics
            if self.metrics:
                job_name = job_data.get('data', {}).get('commandName', 'UnknownJob')
                await self.metrics.record_retry(job_name, retry_count)
            
            logger.info(f"Job retried with {delay}s delay (attempt {retry_count}/{self.max_retries}, strategy: {self.retry_strategy.value})")
            
        except Exception as retry_error:
            logger.error(f"Failed to retry job: {retry_error}")
            self._retry_stats['failed_retries'] += 1
    
    async def get_dead_letter_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get jobs from dead letter queue."""
        try:
            dead_letter_key = f"{self.appname}{self.prefix}queues:{self.dead_letter_queue}"
            jobs = await self.client.lrange(dead_letter_key, 0, limit - 1)
            
            result = []
            for job in jobs:
                try:
                    job_data = json.loads(job)
                    result.append(job_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse dead letter job: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get dead letter jobs: {e}")
            return []
    
    async def reprocess_dead_letter_job(self, job_data: Dict[str, Any]) -> bool:
        """Reprocess a job from dead letter queue."""
        try:
            original_job = job_data.get('original_job', {})
            if not original_job:
                logger.error("No original job data found in dead letter job")
                return False
            
            # Clear retry count for reprocessing
            job_id = self._get_job_id(original_job)
            self._clear_retry_count(job_id)
            
            # Send back to main queue
            queue_key = f"{self.appname}{self.prefix}queues:{self.queue}"
            await self.client.rpush(queue_key, json.dumps(original_job))
            
            logger.info(f"Dead letter job reprocessed: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reprocess dead letter job: {e}")
            return False
    
    async def clear_dead_letter_queue(self) -> int:
        """Clear all jobs from dead letter queue."""
        try:
            dead_letter_key = f"{self.appname}{self.prefix}queues:{self.dead_letter_queue}"
            count = await self.client.llen(dead_letter_key)
            await self.client.delete(dead_letter_key)
            
            logger.info(f"Cleared {count} jobs from dead letter queue")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear dead letter queue: {e}")
            return 0
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            'total_retries': self._retry_stats['total_retries'],
            'successful_retries': self._retry_stats['successful_retries'],
            'failed_retries': self._retry_stats['failed_retries'],
            'dead_letter_jobs': self._retry_stats['dead_letter_jobs'],
            'success_rate': (
                self._retry_stats['successful_retries'] / max(1, self._retry_stats['total_retries'])
            ) * 100,
            'current_retry_config': {
                'strategy': self.retry_strategy.value,
                'max_retries': self.max_retries,
                'delay': self.retry_delay,
                'max_delay': self.retry_max_delay,
                'jitter': self.retry_jitter,
                'backoff_multiplier': self.retry_backoff_multiplier,
                'retryable_exceptions': [exc.__name__ for exc in self.retry_exceptions]
            }
        }
    
    def reset_retry_statistics(self) -> None:
        """Reset retry statistics."""
        self._retry_stats = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'dead_letter_jobs': 0
        }
        logger.info("Async retry statistics reset")
    
    def update_retry_config(self, 
                           max_retries: Optional[int] = None,
                           retry_strategy: Optional[RetryStrategy] = None,
                           retry_delay: Optional[int] = None,
                           retry_max_delay: Optional[int] = None,
                           retry_jitter: Optional[bool] = None,
                           retry_backoff_multiplier: Optional[float] = None,
                           retry_custom_function: Optional[Callable[[int], int]] = None,
                           retry_exceptions: Optional[List[type]] = None) -> None:
        """Update retry configuration at runtime."""
        if max_retries is not None:
            self.max_retries = max_retries
        if retry_strategy is not None:
            self.retry_strategy = retry_strategy
        if retry_delay is not None:
            self.retry_delay = retry_delay
        if retry_max_delay is not None:
            self.retry_max_delay = retry_max_delay
        if retry_jitter is not None:
            self.retry_jitter = retry_jitter
        if retry_backoff_multiplier is not None:
            self.retry_backoff_multiplier = retry_backoff_multiplier
        if retry_custom_function is not None:
            self.retry_custom_function = retry_custom_function
        if retry_exceptions is not None:
            self.retry_exceptions = retry_exceptions
        
        logger.info(f"Async retry configuration updated: {self.get_retry_statistics()['current_retry_config']}")
    
    async def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive metrics."""
        if not self.metrics:
            return None
        return await self.metrics.get_metrics()
    
    async def reset_metrics(self) -> None:
        """Reset all metrics."""
        if self.metrics:
            await self.metrics.reset_metrics()
    
    async def get_recent_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent job history."""
        if not self.metrics:
            return []
        return await self.metrics.get_recent_jobs(limit)
    
    async def get_job_type_metrics(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for specific job type."""
        if not self.metrics:
            return None
        
        metrics = await self.metrics.get_metrics()
        return metrics.get('job_types', {}).get(job_name)
    
    async def get_performance_summary(self) -> Optional[Dict[str, Any]]:
        """Get performance summary."""
        if not self.metrics:
            return None
        
        metrics = await self.metrics.get_metrics()
        return {
            'general': metrics.get('general', {}),
            'performance': metrics.get('performance', {})
        }

    async def _process_job(self, job_data: Dict[str, Any]) -> None:
        """Processes a single job asynchronously."""
        async with self._semaphore:
            self._processing_jobs += 1
            
            try:
                # Record job start time for metrics
                job_name = job_data['data']['commandName']
                start_time = time.time()
                if self.metrics:
                    start_time = await self.metrics.record_job_start(job_name)
                
                try:
                    # Emit event for job processing
                    self.ee.emit(
                        'queued', {'name': job_name, 'data': job_data['data']})
                    
                    # Job processed successfully, clear retry count and update stats
                    job_id = self._get_job_id(job_data)
                    retry_count = self._get_retry_count(job_id)
                    if retry_count > 0:
                        self._retry_stats['successful_retries'] += 1
                    self._clear_retry_count(job_id)
                    
                    # Record successful job in metrics
                    if self.metrics:
                        processing_time = time.time() - start_time
                        await self.metrics.record_job_success(job_name, start_time, processing_time)
                    
                except Exception as e:
                    logger.error(f"Error calling event handler: {e}")
                    
                    # Record failed job in metrics
                    if self.metrics:
                        processing_time = time.time() - start_time
                        await self.metrics.record_job_failure(job_name, start_time, processing_time, e)
                    
                    # Handle job failure with retry/dead letter queue logic
                    job_id = self._get_job_id(job_data)
                    retry_count = self._increment_retry_count(job_id)
                    
                    if self._should_retry(job_id, e):
                        # Retry with calculated delay based on strategy
                        logger.warning(f"Job failed, retrying (attempt {retry_count}/{self.max_retries}, exception: {type(e).__name__})")
                        await self._retry_job(job_data, retry_count)
                    else:
                        # Send to dead letter queue
                        logger.error(f"Job failed after {retry_count} attempts, sending to dead letter queue")
                        await self._send_to_dead_letter_queue(job_data, e, retry_count)
                        self._clear_retry_count(job_id)
                        
            finally:
                self._processing_jobs -= 1

    async def redis_pop(self) -> None:
        """Asynchronously gets and processes jobs from Redis."""
        # Check if shutdown was requested
        if self._shutdown:
            logger.info("Shutdown requested, stopping async worker loop")
            return
        
        try:
            result = await self.client.blpop(
                self.appname + self.prefix + 'queues:' + self.queue, 60)
            
            if result is None:
                # Timeout occurred, check shutdown flag before retrying
                if self._shutdown:
                    logger.info("Shutdown requested during timeout, stopping async worker")
                    return
                logger.debug(f"Timeout waiting for job in queue '{self.queue}', retrying...")
                await self.redis_pop()
                return
                
            key, data = result
            
            try:
                obj = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error from queue '{self.queue}': {e}")
                logger.debug(f"Invalid data: {data}")
                await self.redis_pop()
                return
            
            try:
                command = obj['data']['command']
                # Handle both string and bytes for phpserialize.loads()
                if isinstance(command, str):
                    command = command.encode('utf-8')
                elif isinstance(command, bytes):
                    pass  # Already bytes
                else:
                    logger.error(f"Unexpected command type: {type(command)}")
                    await self.redis_pop()
                    return
                    
                raw = phpserialize.loads(command, object_hook=phpserialize.phpobject)
            except (KeyError, Exception) as e:
                logger.error(f"PHP object deserialization error: {e}")
                logger.error(f"Command type: {type(command)}")
                logger.error(f"Command content: {command[:100] if len(str(command)) > 100 else command}")
                logger.debug(f"Object data: {obj}")
                await self.redis_pop()
                return

            # Process job asynchronously
            asyncio.create_task(self._process_job(obj))

            if self.is_horizon: # TODO
                pass 
            
            if self.is_queue_notify:
                try:
                    await self.client.blpop(
                        self.appname + self.prefix + 'queues:' + self.queue + ':notify', 60)
                except (RedisConnectionError, RedisTimeoutError, RedisError) as e:
                    logger.warning(f"Error reading notify queue: {e}")
                    # Continue working, notify is not critical

            # Check if shutdown was requested while processing
            if self._shutdown:
                logger.info("Shutdown requested, waiting for current jobs to complete")
                # Wait for all jobs to complete
                while self._processing_jobs > 0:
                    await asyncio.sleep(0.1)
                logger.info("All jobs completed, shutting down")
                return
            
            await self.redis_pop()
            
        except RedisConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            
            if self._shutdown:
                logger.info("Shutdown requested, not attempting reconnection")
                return
                
            logger.info("Waiting 5 seconds before reconnecting...")
            await asyncio.sleep(5)
            
            if self._shutdown:
                logger.info("Shutdown requested during reconnection wait")
                return
            
            try:
                await self.redis_pop()
            except Exception as retry_error:
                logger.critical(f"Failed to reconnect to Redis: {retry_error}")
                raise
                
        except RedisTimeoutError as e:
            logger.warning(f"Redis operation timeout: {e}")
            
            if not self._shutdown:
                await self.redis_pop()
            
        except RedisError as e:
            logger.error(f"Redis error: {e}")
            
            if self._shutdown:
                logger.info("Shutdown requested, not retrying after Redis error")
                return
                
            logger.info("Waiting 3 seconds before retry...")
            await asyncio.sleep(3)
            
            if not self._shutdown:
                await self.redis_pop()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping async worker...")
            self._shutdown = True
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error processing async queue: {e}", exc_info=True)
            
            if self._shutdown:
                logger.info("Shutdown requested, not retrying after unexpected error")
                return
                
            await asyncio.sleep(2)
            
            if not self._shutdown:
                await self.redis_pop()

    async def redis_push(self, name: str, dictObj: Dict[str, Any], timeout: Optional[int] = None, delay: Optional[int] = None) -> None:
        """Asynchronously adds a job to Redis queue."""
        try:
            # Serialize PHP object
            try:
                command = phpserialize.dumps(phpserialize.phpobject(name, dictObj))
            except Exception as e:
                logger.error(f"PHP object serialization error '{name}': {e}")
                raise ValueError(f"Failed to serialize job data: {e}") from e
            
            # Prepare job data
            data = {
                "uuid": str(uuid.uuid4()),
                "job": 'Illuminate\\Queue\\CallQueuedHandler@call',
                "data": {
                    "commandName": name,
                    "command": command.decode("utf-8"),  # Decode for JSON
                },
                "timeout": timeout,
                "id": str(time.time()),
                "attempts": 0,
                "delay": delay,
                "maxExceptions": None,
            }
            
            if self.is_queue_notify == False:
                del data['delay']
                del data['maxExceptions']
                data.update({'displayName': name, 'maxTries': None, 'timeoutAt': None})
            
            # Serialize to JSON
            try:
                json_data = json.dumps(data)
            except (TypeError, ValueError) as e:
                logger.error(f"JSON serialization error: {e}")
                raise ValueError(f"Failed to create JSON payload: {e}") from e
            
            # Send to Redis
            queue_key = self.appname + self.prefix + 'queues:' + self.queue
            try:
                await self.client.rpush(queue_key, json_data)
                logger.debug(f"Job '{name}' successfully added to async queue '{self.queue}'")
            except RedisConnectionError as e:
                logger.error(f"Redis connection error while pushing job: {e}")
                raise ConnectionError(f"Failed to connect to Redis: {e}") from e
            except RedisTimeoutError as e:
                logger.error(f"Timeout while pushing job to Redis: {e}")
                raise TimeoutError(f"Redis operation timeout exceeded: {e}") from e
            except RedisError as e:
                logger.error(f"Redis error while pushing job '{name}': {e}")
                raise RuntimeError(f"Redis operation error: {e}") from e
                
        except (ConnectionError, TimeoutError, ValueError, RuntimeError) as e:
            # Re-raise already handled errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error while pushing job '{name}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to add job to async queue: {e}") from e
