# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import SelfSubjectReview, SelfSubjectReviewStatus, TokenReview, TokenReviewSpec, TokenReviewStatus, UserInfo

SelfSubjectReview = __loader(SelfSubjectReview)
SelfSubjectReviewStatus = __loader(SelfSubjectReviewStatus)
TokenReview = __loader(TokenReview)
TokenReviewSpec = __loader(TokenReviewSpec)
TokenReviewStatus = __loader(TokenReviewStatus)
UserInfo = __loader(UserInfo)

__all__ = ['SelfSubjectReview', 'SelfSubjectReviewStatus', 'TokenReview', 'TokenReviewSpec', 'TokenReviewStatus', 'UserInfo']

