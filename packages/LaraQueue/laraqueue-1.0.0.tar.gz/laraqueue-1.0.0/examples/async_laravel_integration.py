"""
Пример интеграции асинхронной очереди LaraQueue с Laravel.

Этот пример демонстрирует:
- Двустороннюю интеграцию Python <-> Laravel
- Асинхронную обработку Laravel задач в Python
- Отправку задач из Python в Laravel
- Высокую производительность при работе с Laravel
"""

import asyncio
import logging
import time
from typing import Dict, Any

import aioredis
from lara_queue import AsyncQueue, RetryStrategy

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_redis_client() -> aioredis.Redis:
    """Создает асинхронный Redis клиент."""
    return await aioredis.from_url("redis://localhost:6379")


async def process_laravel_jobs():
    """Обрабатывает задачи, отправленные из Laravel."""
    logger.info("=== Обработка Laravel задач в Python ===")
    
    redis_client = await create_redis_client()
    
    # Создаем очередь для обработки Laravel задач
    queue = AsyncQueue(
        client=redis_client,
        queue='python_worker',  # Очередь, которую слушает Python
        max_concurrent_jobs=10,
        enable_metrics=True,
        retry_strategy=RetryStrategy.EXPONENTIAL,
        max_retries=3
    )
    
    # Обработчик email задач из Laravel
    @queue.handler
    async def handle_email_job(data: Dict[str, Any]) -> None:
        """Обрабатывает email задачи из Laravel."""
        job_data = data.get('data', {})
        
        # Извлекаем данные из Laravel job
        to = job_data.get('to', '')
        subject = job_data.get('subject', '')
        body = job_data.get('body', '')
        template = job_data.get('template', 'default')
        
        logger.info(f"Отправляем email: {subject} -> {to}")
        
        # Имитируем отправку email
        await asyncio.sleep(0.5)
        
        # Здесь была бы реальная отправка email
        logger.info(f"Email отправлен успешно: {to}")
    
    # Обработчик уведомлений из Laravel
    @queue.handler
    async def handle_notification_job(data: Dict[str, Any]) -> None:
        """Обрабатывает уведомления из Laravel."""
        job_data = data.get('data', {})
        
        user_id = job_data.get('user_id')
        message = job_data.get('message', '')
        type_notification = job_data.get('type', 'info')
        
        logger.info(f"Отправляем уведомление пользователю {user_id}: {message}")
        
        # Имитируем отправку уведомления (push, SMS, etc.)
        await asyncio.sleep(0.3)
        
        logger.info(f"Уведомление отправлено: {type_notification}")
    
    # Обработчик задач обработки данных из Laravel
    @queue.handler
    async def handle_data_processing_job(data: Dict[str, Any]) -> None:
        """Обрабатывает задачи обработки данных из Laravel."""
        job_data = data.get('data', {})
        
        dataset_id = job_data.get('dataset_id')
        operation = job_data.get('operation', 'process')
        
        logger.info(f"Обрабатываем данные {dataset_id}: {operation}")
        
        # Имитируем обработку данных
        await asyncio.sleep(2.0)
        
        # Здесь была бы реальная обработка данных
        logger.info(f"Данные {dataset_id} обработаны успешно")
    
    # Обработчик задач генерации отчетов из Laravel
    @queue.handler
    async def handle_report_generation_job(data: Dict[str, Any]) -> None:
        """Обрабатывает задачи генерации отчетов из Laravel."""
        job_data = data.get('data', {})
        
        report_type = job_data.get('report_type', 'default')
        date_range = job_data.get('date_range', {})
        user_id = job_data.get('user_id')
        
        logger.info(f"Генерируем отчет {report_type} для пользователя {user_id}")
        
        # Имитируем генерацию отчета
        await asyncio.sleep(3.0)
        
        # Здесь была бы реальная генерация отчета
        logger.info(f"Отчет {report_type} сгенерирован успешно")
    
    logger.info("Запускаем обработку Laravel задач...")
    logger.info("Отправьте задачи из Laravel в очередь 'python_worker'")
    
    # Обрабатываем задачи в течение 60 секунд
    try:
        await asyncio.wait_for(queue.listen(), timeout=60.0)
    except asyncio.TimeoutError:
        logger.info("Время обработки истекло")
    
    # Показываем метрики
    metrics = queue.get_metrics()
    if metrics:
        logger.info(f"Обработано Laravel задач: {metrics['general']['total_processed']}")
        logger.info(f"Успешно: {metrics['general']['total_successful']}")
        logger.info(f"Throughput: {metrics['performance']['throughput_per_second']:.2f} задач/сек")
    
    await redis_client.close()


async def send_jobs_to_laravel():
    """Отправляет задачи из Python в Laravel."""
    logger.info("=== Отправка задач из Python в Laravel ===")
    
    redis_client = await create_redis_client()
    
    # Создаем очередь для отправки задач в Laravel
    queue = AsyncQueue(
        client=redis_client,
        queue='laravel_worker',  # Очередь, которую слушает Laravel
        enable_metrics=True
    )
    
    # Отправляем различные типы задач в Laravel
    
    # 1. Задача обновления пользователя
    await queue.push('App\\Jobs\\UpdateUserJob', {
        'user_id': 123,
        'data': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'last_login': time.time()
        }
    })
    logger.info("Отправлена задача обновления пользователя")
    
    # 2. Задача очистки кэша
    await queue.push('App\\Jobs\\ClearCacheJob', {
        'cache_keys': ['users', 'products', 'categories'],
        'tags': ['user_data', 'product_data']
    })
    logger.info("Отправлена задача очистки кэша")
    
    # 3. Задача резервного копирования
    await queue.push('App\\Jobs\\BackupJob', {
        'backup_type': 'database',
        'tables': ['users', 'orders', 'products'],
        'compression': True
    })
    logger.info("Отправлена задача резервного копирования")
    
    # 4. Задача синхронизации с внешним API
    await queue.push('App\\Jobs\\SyncExternalApiJob', {
        'api_endpoint': 'https://api.external.com/sync',
        'data': {
            'users': [1, 2, 3, 4, 5],
            'sync_type': 'full'
        }
    })
    logger.info("Отправлена задача синхронизации с API")
    
    # 5. Задача отправки уведомлений
    await queue.push('App\\Jobs\\SendNotificationJob', {
        'notification_type': 'email',
        'recipients': ['user1@example.com', 'user2@example.com'],
        'template': 'welcome',
        'data': {
            'app_name': 'MyApp',
            'welcome_message': 'Добро пожаловать!'
        }
    })
    logger.info("Отправлена задача отправки уведомлений")
    
    # 6. Массовая отправка задач
    logger.info("Отправляем массовые задачи...")
    for i in range(20):
        await queue.push('App\\Jobs\\BatchProcessJob', {
            'batch_id': f'batch_{i}',
            'items': list(range(i * 10, (i + 1) * 10)),
            'process_type': 'update'
        })
    
    logger.info("Отправлено 20 массовых задач")
    
    # Показываем метрики отправки
    metrics = queue.get_metrics()
    if metrics:
        logger.info(f"Отправлено задач в Laravel: {metrics['general']['total_processed']}")
    
    await redis_client.close()


async def high_volume_processing():
    """Обработка большого объема задач с высокой производительностью."""
    logger.info("=== Высокопроизводительная обработка ===")
    
    redis_client = await create_redis_client()
    
    # Создаем высокопроизводительную очередь
    queue = AsyncQueue(
        client=redis_client,
        queue='high_volume_worker',
        max_concurrent_jobs=50,  # 50 одновременных задач
        enable_metrics=True,
        metrics_history_size=10000,
        retry_strategy=RetryStrategy.LINEAR,
        retry_delay=1,
        max_retries=2
    )
    
    # Быстрый обработчик для высоких нагрузок
    @queue.handler
    async def fast_processor(data: Dict[str, Any]) -> None:
        """Быстрый обработчик для высоких нагрузок."""
        job_data = data.get('data', {})
        task_id = job_data.get('task_id', 'unknown')
        operation = job_data.get('operation', 'process')
        
        # Имитируем быструю обработку
        await asyncio.sleep(0.05)  # 50ms обработка
        
        # Иногда генерируем ошибки для демонстрации retry
        if hash(task_id) % 20 == 0:  # 5% ошибок
            raise ValueError(f"Временная ошибка в задаче {task_id}")
    
    # Генерируем большое количество задач
    task_count = 500
    logger.info(f"Генерируем {task_count} задач...")
    
    start_time = time.time()
    for i in range(task_count):
        await queue.push('App\\Jobs\\FastProcessJob', {
            'task_id': f'task_{i}',
            'operation': 'process',
            'data': f'Task data {i}',
            'priority': i % 5
        })
    
    generation_time = time.time() - start_time
    logger.info(f"Сгенерировано {task_count} задач за {generation_time:.2f} секунд")
    
    # Обрабатываем задачи
    process_start = time.time()
    try:
        await asyncio.wait_for(queue.listen(), timeout=60.0)
    except asyncio.TimeoutError:
        pass
    
    process_time = time.time() - process_start
    
    # Показываем результаты
    metrics = queue.get_metrics()
    if metrics:
        logger.info(f"Результаты высокопроизводительной обработки:")
        logger.info(f"  Время обработки: {process_time:.2f} секунд")
        logger.info(f"  Обработано: {metrics['general']['total_processed']} задач")
        logger.info(f"  Успешно: {metrics['general']['total_successful']}")
        logger.info(f"  Неудачно: {metrics['general']['total_failed']}")
        logger.info(f"  Throughput: {metrics['performance']['throughput_per_second']:.2f} задач/сек")
        logger.info(f"  Среднее время: {metrics['performance']['avg_processing_time']:.3f} сек")
        
        # Показываем retry статистику
        retry_stats = queue.get_retry_statistics()
        logger.info(f"  Retry статистика:")
        logger.info(f"    Всего retry: {retry_stats['total_retries']}")
        logger.info(f"    Успешные retry: {retry_stats['successful_retries']}")
        logger.info(f"    Процент успеха: {retry_stats['success_rate']:.1f}%")
    
    await redis_client.close()


async def real_time_monitoring():
    """Мониторинг в реальном времени."""
    logger.info("=== Мониторинг в реальном времени ===")
    
    redis_client = await create_redis_client()
    
    queue = AsyncQueue(
        client=redis_client,
        queue='monitoring_worker',
        max_concurrent_jobs=5,
        enable_metrics=True
    )
    
    @queue.handler
    async def monitored_task(data: Dict[str, Any]) -> None:
        """Задача с мониторингом."""
        job_data = data.get('data', {})
        task_type = job_data.get('type', 'default')
        
        # Имитируем работу с разной продолжительностью
        duration = {'fast': 0.1, 'medium': 0.5, 'slow': 1.0}[task_type]
        await asyncio.sleep(duration)
    
    # Добавляем задачи
    for i in range(30):
        task_type = ['fast', 'medium', 'slow'][i % 3]
        await queue.push('App\\Jobs\\MonitoredJob', {
            'type': task_type,
            'task_id': i
        })
    
    # Запускаем мониторинг в фоне
    async def monitor_metrics():
        """Мониторинг метрик в фоне."""
        while True:
            await asyncio.sleep(5)  # Каждые 5 секунд
            
            metrics = queue.get_metrics()
            if metrics:
                general = metrics['general']
                performance = metrics['performance']
                
                logger.info(f"Мониторинг: {general['total_processed']} задач, "
                           f"{performance['throughput_per_second']:.1f} задач/сек, "
                           f"{general['success_rate']:.1f}% успех")
    
    # Запускаем мониторинг и обработку параллельно
    monitor_task = asyncio.create_task(monitor_metrics())
    listen_task = asyncio.create_task(queue.listen())
    
    try:
        await asyncio.wait_for(listen_task, timeout=30.0)
    except asyncio.TimeoutError:
        pass
    finally:
        monitor_task.cancel()
    
    await redis_client.close()


async def main():
    """Главная функция с примерами интеграции."""
    logger.info("Запуск примеров интеграции LaraQueue с Laravel")
    
    try:
        # Запускаем все примеры
        await process_laravel_jobs()
        await asyncio.sleep(2)
        
        await send_jobs_to_laravel()
        await asyncio.sleep(2)
        
        await high_volume_processing()
        await asyncio.sleep(2)
        
        await real_time_monitoring()
        
    except Exception as e:
        logger.error(f"Ошибка в примерах интеграции: {e}")
    
    logger.info("Все примеры интеграции завершены")


if __name__ == "__main__":
    # Запускаем примеры
    asyncio.run(main())
