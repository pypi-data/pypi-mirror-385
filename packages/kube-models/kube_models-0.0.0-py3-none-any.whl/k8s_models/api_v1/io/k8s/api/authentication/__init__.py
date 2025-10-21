# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import BoundObjectReference, TokenRequest, TokenRequestSpec, TokenRequestStatus

BoundObjectReference = __loader(BoundObjectReference)
TokenRequest = __loader(TokenRequest)
TokenRequestSpec = __loader(TokenRequestSpec)
TokenRequestStatus = __loader(TokenRequestStatus)

__all__ = ['BoundObjectReference', 'TokenRequest', 'TokenRequestSpec', 'TokenRequestStatus']

