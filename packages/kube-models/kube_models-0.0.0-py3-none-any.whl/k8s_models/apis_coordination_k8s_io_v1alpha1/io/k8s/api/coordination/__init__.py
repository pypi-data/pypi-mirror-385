# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1alpha1 import LeaseCandidate, LeaseCandidateList, LeaseCandidateSpec

LeaseCandidate = __loader(LeaseCandidate)
LeaseCandidateList = __loader(LeaseCandidateList)
LeaseCandidateSpec = __loader(LeaseCandidateSpec)

__all__ = ['LeaseCandidate', 'LeaseCandidateList', 'LeaseCandidateSpec']

