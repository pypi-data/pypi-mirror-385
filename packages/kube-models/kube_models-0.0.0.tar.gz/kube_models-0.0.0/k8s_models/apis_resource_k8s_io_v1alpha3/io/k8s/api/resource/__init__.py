# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1alpha3 import CELDeviceSelector, DeviceSelector, DeviceTaint, DeviceTaintRule, DeviceTaintRuleList, DeviceTaintRuleSpec, DeviceTaintSelector

CELDeviceSelector = __loader(CELDeviceSelector)
DeviceSelector = __loader(DeviceSelector)
DeviceTaint = __loader(DeviceTaint)
DeviceTaintRule = __loader(DeviceTaintRule)
DeviceTaintRuleList = __loader(DeviceTaintRuleList)
DeviceTaintRuleSpec = __loader(DeviceTaintRuleSpec)
DeviceTaintSelector = __loader(DeviceTaintSelector)

__all__ = ['CELDeviceSelector', 'DeviceSelector', 'DeviceTaint', 'DeviceTaintRule', 'DeviceTaintRuleList', 'DeviceTaintRuleSpec', 'DeviceTaintSelector']

