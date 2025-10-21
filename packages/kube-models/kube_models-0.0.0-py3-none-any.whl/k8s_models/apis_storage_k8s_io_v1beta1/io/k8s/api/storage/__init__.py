# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1beta1 import VolumeAttributesClass, VolumeAttributesClassList

VolumeAttributesClass = __loader(VolumeAttributesClass)
VolumeAttributesClassList = __loader(VolumeAttributesClassList)

__all__ = ['VolumeAttributesClass', 'VolumeAttributesClassList']

