# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import APIVersions, ServerAddressByClientCIDR

APIVersions = __loader(APIVersions)
ServerAddressByClientCIDR = __loader(ServerAddressByClientCIDR)

__all__ = ['APIVersions', 'ServerAddressByClientCIDR']

