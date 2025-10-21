# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import APIService, APIServiceCondition, APIServiceList, APIServiceSpec, APIServiceStatus, ServiceReference

APIService = __loader(APIService)
APIServiceCondition = __loader(APIServiceCondition)
APIServiceList = __loader(APIServiceList)
APIServiceSpec = __loader(APIServiceSpec)
APIServiceStatus = __loader(APIServiceStatus)
ServiceReference = __loader(ServiceReference)

__all__ = ['APIService', 'APIServiceCondition', 'APIServiceList', 'APIServiceSpec', 'APIServiceStatus', 'ServiceReference']

