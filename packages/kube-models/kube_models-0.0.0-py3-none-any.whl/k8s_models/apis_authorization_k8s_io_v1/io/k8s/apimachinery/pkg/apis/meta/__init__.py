# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import APIResource, APIResourceList, FieldSelectorRequirement, FieldsV1, LabelSelectorRequirement, ManagedFieldsEntry, ObjectMeta, OwnerReference, Time

APIResource = __loader(APIResource)
APIResourceList = __loader(APIResourceList)
FieldSelectorRequirement = __loader(FieldSelectorRequirement)
FieldsV1 = __loader(FieldsV1)
LabelSelectorRequirement = __loader(LabelSelectorRequirement)
ManagedFieldsEntry = __loader(ManagedFieldsEntry)
ObjectMeta = __loader(ObjectMeta)
OwnerReference = __loader(OwnerReference)

__all__ = ['APIResource', 'APIResourceList', 'FieldSelectorRequirement', 'FieldsV1', 'LabelSelectorRequirement', 'ManagedFieldsEntry', 'ObjectMeta', 'OwnerReference', 'Time']

