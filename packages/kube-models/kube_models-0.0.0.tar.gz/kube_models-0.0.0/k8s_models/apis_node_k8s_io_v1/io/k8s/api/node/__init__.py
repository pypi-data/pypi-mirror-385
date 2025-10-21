# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import Overhead, RuntimeClass, RuntimeClassList, Scheduling

Overhead = __loader(Overhead)
RuntimeClass = __loader(RuntimeClass)
RuntimeClassList = __loader(RuntimeClassList)
Scheduling = __loader(Scheduling)

__all__ = ['Overhead', 'RuntimeClass', 'RuntimeClassList', 'Scheduling']

