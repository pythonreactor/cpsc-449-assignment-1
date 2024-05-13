from inventory.app import create_app
from rq import (
    Connection,
    Worker
)


def start_worker():
    app = create_app()

    with app.app_context():
        from inventory import redis_queue

        with Connection():
            worker = Worker(queues=[redis_queue], connection=redis_queue.connection)
            worker.work()


if __name__ == '__main__':
    start_worker()
