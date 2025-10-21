# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import PodDisruptionBudget, PodDisruptionBudgetList, PodDisruptionBudgetSpec, PodDisruptionBudgetStatus

PodDisruptionBudget = __loader(PodDisruptionBudget)
PodDisruptionBudgetList = __loader(PodDisruptionBudgetList)
PodDisruptionBudgetSpec = __loader(PodDisruptionBudgetSpec)
PodDisruptionBudgetStatus = __loader(PodDisruptionBudgetStatus)

__all__ = ['PodDisruptionBudget', 'PodDisruptionBudgetList', 'PodDisruptionBudgetSpec', 'PodDisruptionBudgetStatus']

