
from litestar_saq import CronJob, QueueConfig, SAQConfig
from fimbu.conf import settings
from fimbu.core.types import ApplicationType

__all__ = ["install_saq_plugin"]

def install_saq_plugin(app: ApplicationType) -> None:
    """Install saq plugin."""

    saq = SAQConfig(
        redis=settings.redis.client,
        web_enabled=settings.SAQ_WEB_ENABLED,
        worker_processes=settings.SAQ_PROCESSES,
        use_server_lifespan=settings.SAQ_USE_SERVER_LIFESPAN,
        queue_configs=[
            QueueConfig(
                name="system-tasks",
                tasks=["app.domain.system.tasks.system_task", "app.domain.system.tasks.system_upkeep"],
                scheduled_tasks=[
                    CronJob(
                        function="app.domain.system.tasks.system_upkeep",
                        unique=True,
                        cron="0 * * * *",
                        timeout=500,
                    ),
                ],
            ),
            QueueConfig(
                name="background-tasks",
                tasks=["app.domain.system.tasks.background_worker_task"],
                scheduled_tasks=[
                    CronJob(
                        function="app.domain.system.tasks.background_worker_task",
                        unique=True,
                        cron="* * * * *",
                        timeout=300,
                    ),
                ],
            ),
        ],
    )

    if isinstance(app, ApplicationType):
        app.set_config(
            'plugins',
            [saq]
        )
    else:
        raise TypeError("app must be an instance or Application")
