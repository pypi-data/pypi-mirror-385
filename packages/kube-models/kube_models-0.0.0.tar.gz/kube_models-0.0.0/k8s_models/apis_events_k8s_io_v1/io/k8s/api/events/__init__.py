# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import Event, EventList, EventSeries

Event = __loader(Event)
EventList = __loader(EventList)
EventSeries = __loader(EventSeries)

__all__ = ['Event', 'EventList', 'EventSeries']

