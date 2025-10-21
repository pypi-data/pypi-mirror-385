# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import CrossVersionObjectReference, HorizontalPodAutoscaler, HorizontalPodAutoscalerList, HorizontalPodAutoscalerSpec, HorizontalPodAutoscalerStatus

CrossVersionObjectReference = __loader(CrossVersionObjectReference)
HorizontalPodAutoscaler = __loader(HorizontalPodAutoscaler)
HorizontalPodAutoscalerList = __loader(HorizontalPodAutoscalerList)
HorizontalPodAutoscalerSpec = __loader(HorizontalPodAutoscalerSpec)
HorizontalPodAutoscalerStatus = __loader(HorizontalPodAutoscalerStatus)

__all__ = ['CrossVersionObjectReference', 'HorizontalPodAutoscaler', 'HorizontalPodAutoscalerList', 'HorizontalPodAutoscalerSpec', 'HorizontalPodAutoscalerStatus']

