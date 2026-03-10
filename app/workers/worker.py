import os
from redis import Redis
from rq import Worker, Queue
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()


def run() -> None:
    redis_conn = Redis.from_url(settings.redis_url)
    queues = [Queue("notifications", connection=redis_conn)]
    worker = Worker(queues, connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONPATH", "/code")
    run()
