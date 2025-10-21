# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import Lease, LeaseList, LeaseSpec

Lease = __loader(Lease)
LeaseList = __loader(LeaseList)
LeaseSpec = __loader(LeaseSpec)

__all__ = ['Lease', 'LeaseList', 'LeaseSpec']

