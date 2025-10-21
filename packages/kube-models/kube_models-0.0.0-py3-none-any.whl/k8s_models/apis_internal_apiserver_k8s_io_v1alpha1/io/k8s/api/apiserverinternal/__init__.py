# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1alpha1 import ServerStorageVersion, StorageVersion, StorageVersionCondition, StorageVersionList, StorageVersionSpec, StorageVersionStatus

ServerStorageVersion = __loader(ServerStorageVersion)
StorageVersion = __loader(StorageVersion)
StorageVersionCondition = __loader(StorageVersionCondition)
StorageVersionList = __loader(StorageVersionList)
StorageVersionSpec = __loader(StorageVersionSpec)
StorageVersionStatus = __loader(StorageVersionStatus)

__all__ = ['ServerStorageVersion', 'StorageVersion', 'StorageVersionCondition', 'StorageVersionList', 'StorageVersionSpec', 'StorageVersionStatus']

