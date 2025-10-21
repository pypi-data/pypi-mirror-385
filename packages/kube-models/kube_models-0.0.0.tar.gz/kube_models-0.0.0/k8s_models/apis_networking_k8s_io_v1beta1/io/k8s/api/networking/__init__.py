# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1beta1 import IPAddress, IPAddressList, IPAddressSpec, ParentReference, ServiceCIDR, ServiceCIDRList, ServiceCIDRSpec, ServiceCIDRStatus

IPAddress = __loader(IPAddress)
IPAddressList = __loader(IPAddressList)
IPAddressSpec = __loader(IPAddressSpec)
ParentReference = __loader(ParentReference)
ServiceCIDR = __loader(ServiceCIDR)
ServiceCIDRList = __loader(ServiceCIDRList)
ServiceCIDRSpec = __loader(ServiceCIDRSpec)
ServiceCIDRStatus = __loader(ServiceCIDRStatus)

__all__ = ['IPAddress', 'IPAddressList', 'IPAddressSpec', 'ParentReference', 'ServiceCIDR', 'ServiceCIDRList', 'ServiceCIDRSpec', 'ServiceCIDRStatus']

