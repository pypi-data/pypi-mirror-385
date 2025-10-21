# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import APIGroup, APIGroupList, GroupVersionForDiscovery, ServerAddressByClientCIDR

APIGroup = __loader(APIGroup)
APIGroupList = __loader(APIGroupList)
GroupVersionForDiscovery = __loader(GroupVersionForDiscovery)
ServerAddressByClientCIDR = __loader(ServerAddressByClientCIDR)

__all__ = ['APIGroup', 'APIGroupList', 'GroupVersionForDiscovery', 'ServerAddressByClientCIDR']

