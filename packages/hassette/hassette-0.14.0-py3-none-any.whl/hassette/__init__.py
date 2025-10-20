import logging

from . import events, models, topics
from .config import HassetteConfig
from .core import context
from .core.core import Hassette
from .core.resources.api.api import Api
from .core.resources.app.app import App, AppSync, only_app
from .core.resources.app.app_config import AppConfig, AppConfigT
from .core.resources.base import Resource, Service
from .core.resources.bus import predicates
from .core.resources.bus.bus import Bus
from .core.resources.bus.listeners import Listener, Subscription
from .core.resources.scheduler.classes import CronTrigger, IntervalTrigger, ScheduledJob
from .core.resources.scheduler.scheduler import Scheduler
from .core.resources.task_bucket import TaskBucket
from .enums import ResourceRole, ResourceStatus
from .events import StateChangeEvent
from .models import entities, states
from .models.services import ServiceResponse
from .types import AsyncHandler, Handler, Predicate, TriggerProtocol

logging.getLogger("hassette").addHandler(logging.NullHandler())

__all__ = [
    "Api",
    "App",
    "AppConfig",
    "AppConfigT",
    "AppSync",
    "AsyncHandler",
    "Bus",
    "CronTrigger",
    "Handler",
    "Hassette",
    "HassetteConfig",
    "IntervalTrigger",
    "Listener",
    "Predicate",
    "Resource",
    "ResourceRole",
    "ResourceStatus",
    "ScheduledJob",
    "Scheduler",
    "Service",
    "ServiceResponse",
    "StateChangeEvent",
    "Subscription",
    "TaskBucket",
    "TriggerProtocol",
    "context",
    "entities",
    "events",
    "models",
    "only_app",
    "predicates",
    "states",
    "topics",
]
