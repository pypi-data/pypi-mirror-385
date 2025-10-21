# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1alpha1 import ClusterTrustBundle, ClusterTrustBundleList, ClusterTrustBundleSpec, PodCertificateRequest, PodCertificateRequestList, PodCertificateRequestSpec, PodCertificateRequestStatus

ClusterTrustBundle = __loader(ClusterTrustBundle)
ClusterTrustBundleList = __loader(ClusterTrustBundleList)
ClusterTrustBundleSpec = __loader(ClusterTrustBundleSpec)
PodCertificateRequest = __loader(PodCertificateRequest)
PodCertificateRequestList = __loader(PodCertificateRequestList)
PodCertificateRequestSpec = __loader(PodCertificateRequestSpec)
PodCertificateRequestStatus = __loader(PodCertificateRequestStatus)

__all__ = ['ClusterTrustBundle', 'ClusterTrustBundleList', 'ClusterTrustBundleSpec', 'PodCertificateRequest', 'PodCertificateRequestList', 'PodCertificateRequestSpec', 'PodCertificateRequestStatus']

