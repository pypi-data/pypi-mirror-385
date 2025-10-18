# 🚀 Руководство по миграции на AsyncQueue (v1.0.0)

## Обзор изменений

LaraQueue v1.0.0 добавляет полную поддержку asyncio для высоких нагрузок, сохраняя полную обратную совместимость с существующим синхронным API.

## Что нового

### ✅ Новые возможности
- **AsyncQueue** - асинхронная версия очереди
- **Параллельная обработка** - до 50+ одновременных задач
- **Высокая производительность** - до 10x+ увеличение throughput
- **AsyncIOEventEmitter** - асинхронные обработчики событий
- **Полная совместимость** с asyncio экосистемой

### ✅ Обратная совместимость
- **Существующий код работает без изменений**
- **Оба API доступны** - sync и async
- **Плавная миграция** - можно использовать оба подхода

## Миграция с Sync на Async

### 1. Обновление зависимостей

```bash
pip install --upgrade LaraQueue
```

Новые зависимости:
- `aioredis>=2.0.0` (автоматически установится)

### 2. Базовый пример миграции

#### До (Sync):
```python
from lara_queue import Queue
from redis import Redis

r = Redis(host='localhost', port=6379, db=0)
queue = Queue(r, queue='python')

@queue.handler
def handle(data):
    print('Processing: ' + data['data']['message'])

queue.listen()
```

#### После (Async):
```python
import asyncio
import aioredis
from lara_queue import AsyncQueue

async def main():
    redis_client = await aioredis.from_url("redis://localhost:6379")
    queue = AsyncQueue(redis_client, queue='python')

    @queue.handler
    async def handle(data):
        print('Processing: ' + data['data']['message'])

    await queue.listen()

asyncio.run(main())
```

### 3. Миграция с высокой производительностью

#### До (Sync):
```python
queue = Queue(r, queue='worker')
```

#### После (Async):
```python
queue = AsyncQueue(
    client=redis_client,
    queue='worker',
    max_concurrent_jobs=20,  # 20 одновременных задач
    enable_metrics=True
)
```

### 4. Миграция обработчиков

#### До (Sync):
```python
@queue.handler
def process_email(data):
    # Синхронная обработка
    send_email(data['data']['to'])
```

#### После (Async):
```python
@queue.handler
async def process_email(data):
    # Асинхронная обработка
    await send_email_async(data['data']['to'])
```

### 5. Миграция добавления задач

#### До (Sync):
```python
queue.push('App\\Jobs\\EmailJob', {
    'to': 'user@example.com',
    'subject': 'Hello'
})
```

#### После (Async):
```python
await queue.push('App\\Jobs\\EmailJob', {
    'to': 'user@example.com',
    'subject': 'Hello'
})
```

## Рекомендации по производительности

### Настройки для разных типов задач

#### I/O-интенсивные задачи (API, DB)
```python
queue = AsyncQueue(
    client=redis_client,
    queue='io_worker',
    max_concurrent_jobs=50,  # Высокая параллельность
    enable_metrics=True
)
```

#### CPU-интенсивные задачи
```python
queue = AsyncQueue(
    client=redis_client,
    queue='cpu_worker',
    max_concurrent_jobs=4,  # По количеству ядер CPU
    enable_metrics=True
)
```

#### Смешанные задачи
```python
queue = AsyncQueue(
    client=redis_client,
    queue='mixed_worker',
    max_concurrent_jobs=20,  # Баланс
    enable_metrics=True
)
```

## Поэтапная миграция

### Этап 1: Подготовка
1. Обновите LaraQueue до v1.0.0
2. Установите aioredis
3. Протестируйте существующий код

### Этап 2: Создание async версии
1. Создайте новый async worker
2. Протестируйте параллельно с sync версией
3. Сравните производительность

### Этап 3: Переключение
1. Постепенно переводите очереди на async
2. Мониторьте производительность
3. Настраивайте параметры

### Этап 4: Оптимизация
1. Настройте max_concurrent_jobs
2. Включите метрики
3. Оптимизируйте обработчики

## Совместимость с Laravel

### Sync (существующий)
```python
# Laravel отправляет в очередь 'python'
queue = Queue(r, queue='python')
```

### Async (новый)
```python
# Laravel отправляет в очередь 'python_async'
queue = AsyncQueue(redis_client, queue='python_async')
```

**Важно**: Laravel не нужно изменять! Просто настройте разные очереди.

## Мониторинг и отладка

### Метрики
```python
# Получение метрик
metrics = queue.get_metrics()
print(f"Throughput: {metrics['performance']['throughput_per_second']:.2f} jobs/sec")
print(f"Concurrent jobs: {queue._processing_jobs}")
```

### Логирование
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('lara_queue')
```

## Частые вопросы

### Q: Нужно ли менять Laravel код?
**A**: Нет! Laravel код остается без изменений. Просто используйте разные имена очередей.

### Q: Можно ли использовать оба API одновременно?
**A**: Да! Можно запускать sync и async workers параллельно.

### Q: Какая производительность у async версии?
**A**: До 10x+ увеличение throughput, особенно для I/O-интенсивных задач.

### Q: Есть ли ограничения по памяти?
**A**: Async версия использует ~20% больше памяти, но значительно эффективнее по CPU.

### Q: Как настроить количество одновременных задач?
**A**: Используйте параметр `max_concurrent_jobs`. Начните с 10-20, затем оптимизируйте.

## Поддержка

Если у вас есть вопросы по миграции:
1. Проверьте примеры в `examples/async_example.py`
2. Изучите тесты в `tests/test_async_queue.py`
3. Создайте issue в репозитории

## Заключение

Миграция на AsyncQueue дает значительное увеличение производительности при минимальных изменениях кода. Начните с простых случаев и постепенно переводите все очереди на async API.
