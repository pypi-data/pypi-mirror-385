# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1beta1 import ClusterTrustBundle, ClusterTrustBundleList, ClusterTrustBundleSpec

ClusterTrustBundle = __loader(ClusterTrustBundle)
ClusterTrustBundleList = __loader(ClusterTrustBundleList)
ClusterTrustBundleSpec = __loader(ClusterTrustBundleSpec)

__all__ = ['ClusterTrustBundle', 'ClusterTrustBundleList', 'ClusterTrustBundleSpec']

