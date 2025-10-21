# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1alpha1 import GroupVersionResource, MigrationCondition, StorageVersionMigration, StorageVersionMigrationList, StorageVersionMigrationSpec, StorageVersionMigrationStatus

GroupVersionResource = __loader(GroupVersionResource)
MigrationCondition = __loader(MigrationCondition)
StorageVersionMigration = __loader(StorageVersionMigration)
StorageVersionMigrationList = __loader(StorageVersionMigrationList)
StorageVersionMigrationSpec = __loader(StorageVersionMigrationSpec)
StorageVersionMigrationStatus = __loader(StorageVersionMigrationStatus)

__all__ = ['GroupVersionResource', 'MigrationCondition', 'StorageVersionMigration', 'StorageVersionMigrationList', 'StorageVersionMigrationSpec', 'StorageVersionMigrationStatus']

