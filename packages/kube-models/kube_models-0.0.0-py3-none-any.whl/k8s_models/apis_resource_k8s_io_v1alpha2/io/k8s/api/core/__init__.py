# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import NodeSelector, NodeSelectorRequirement, NodeSelectorTerm

NodeSelector = __loader(NodeSelector)
NodeSelectorRequirement = __loader(NodeSelectorRequirement)
NodeSelectorTerm = __loader(NodeSelectorTerm)

__all__ = ['NodeSelector', 'NodeSelectorRequirement', 'NodeSelectorTerm']

