# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import AggregationRule, ClusterRole, ClusterRoleBinding, ClusterRoleBindingList, ClusterRoleList, PolicyRule, Role, RoleBinding, RoleBindingList, RoleList, RoleRef, Subject

AggregationRule = __loader(AggregationRule)
ClusterRole = __loader(ClusterRole)
ClusterRoleBinding = __loader(ClusterRoleBinding)
ClusterRoleBindingList = __loader(ClusterRoleBindingList)
ClusterRoleList = __loader(ClusterRoleList)
PolicyRule = __loader(PolicyRule)
Role = __loader(Role)
RoleBinding = __loader(RoleBinding)
RoleBindingList = __loader(RoleBindingList)
RoleList = __loader(RoleList)
RoleRef = __loader(RoleRef)
Subject = __loader(Subject)

__all__ = ['AggregationRule', 'ClusterRole', 'ClusterRoleBinding', 'ClusterRoleBindingList', 'ClusterRoleList', 'PolicyRule', 'Role', 'RoleBinding', 'RoleBindingList', 'RoleList', 'RoleRef', 'Subject']

