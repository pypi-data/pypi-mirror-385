# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import CertificateSigningRequest, CertificateSigningRequestCondition, CertificateSigningRequestList, CertificateSigningRequestSpec, CertificateSigningRequestStatus

CertificateSigningRequest = __loader(CertificateSigningRequest)
CertificateSigningRequestCondition = __loader(CertificateSigningRequestCondition)
CertificateSigningRequestList = __loader(CertificateSigningRequestList)
CertificateSigningRequestSpec = __loader(CertificateSigningRequestSpec)
CertificateSigningRequestStatus = __loader(CertificateSigningRequestStatus)

__all__ = ['CertificateSigningRequest', 'CertificateSigningRequestCondition', 'CertificateSigningRequestList', 'CertificateSigningRequestSpec', 'CertificateSigningRequestStatus']

