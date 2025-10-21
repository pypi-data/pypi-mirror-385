# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import Endpoint, EndpointConditions, EndpointHints, EndpointPort, EndpointSlice, EndpointSliceList, ForNode, ForZone

Endpoint = __loader(Endpoint)
EndpointConditions = __loader(EndpointConditions)
EndpointHints = __loader(EndpointHints)
EndpointPort = __loader(EndpointPort)
EndpointSlice = __loader(EndpointSlice)
EndpointSliceList = __loader(EndpointSliceList)
ForNode = __loader(ForNode)
ForZone = __loader(ForZone)

__all__ = ['Endpoint', 'EndpointConditions', 'EndpointHints', 'EndpointPort', 'EndpointSlice', 'EndpointSliceList', 'ForNode', 'ForZone']

