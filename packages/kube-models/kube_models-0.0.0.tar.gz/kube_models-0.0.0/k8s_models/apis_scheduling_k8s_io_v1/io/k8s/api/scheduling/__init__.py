# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import PriorityClass, PriorityClassList

PriorityClass = __loader(PriorityClass)
PriorityClassList = __loader(PriorityClassList)

__all__ = ['PriorityClass', 'PriorityClassList']

