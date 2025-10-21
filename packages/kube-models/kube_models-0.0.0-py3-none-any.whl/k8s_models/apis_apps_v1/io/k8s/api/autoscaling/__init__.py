# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import Scale, ScaleSpec, ScaleStatus

Scale = __loader(Scale)
ScaleSpec = __loader(ScaleSpec)
ScaleStatus = __loader(ScaleStatus)

__all__ = ['Scale', 'ScaleSpec', 'ScaleStatus']

