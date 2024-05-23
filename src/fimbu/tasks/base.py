import asyncio
import contextlib
from collections.abc import Callable
from typing import ClassVar
from urllib.parse import urlparse

import dramatiq
import jinja2
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import CurrentMessage


redis_parameters = urlparse(settings.redis_url)
redis_broker = RedisBroker(
    host=redis_parameters.hostname,
    port=redis_parameters.port,
    username=redis_parameters.username,
    password=redis_parameters.password,
    # Heroku Redis with TLS use self-signed certs, so we need to tinker a bit
    ssl=redis_parameters.scheme == "rediss",
    ssl_cert_reqs=None,
)
redis_broker.add_middleware(CurrentMessage())
dramatiq.set_broker(redis_broker)


SendTask = Callable[..., None]


def send_task(task: dramatiq.Actor, *args, **kwargs):
    logger.debug("Send task", task=task.actor_name)
    task.send(*args, **kwargs)



class TaskError(Exception):
    pass


class ObjectDoesNotExistTaskError(TaskError):
    def __init__(self, object_type: type[BaseModel], id: str):
        super().__init__(f"{object_type.__name__} with id {id} does not exist.")


class TaskBase:
    __name__: ClassVar[str]

    def __init__(
        self,
        send_task: SendTask = send_task,
    ) -> None:
        self.email_provider = email_provider
        self.send_task = send_task


    def __call__(self, *args, **kwargs):
        with asyncio.Runner() as runner:
            BabelMiddleware(app=None, **get_babel_middleware_kwargs())
            logger.info("Start task", task=self.__name__)
            result = runner.run(self.run(*args, **kwargs))
            logger.info("Done task", task=self.__name__)
            return result
