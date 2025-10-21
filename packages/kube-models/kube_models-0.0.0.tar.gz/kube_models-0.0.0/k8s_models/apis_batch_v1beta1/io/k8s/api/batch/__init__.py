# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import JobSpec
from .v1beta1 import CronJob, CronJobList, CronJobSpec, CronJobStatus, JobTemplateSpec

JobSpec = __loader(JobSpec)
CronJob = __loader(CronJob)
CronJobList = __loader(CronJobList)
CronJobSpec = __loader(CronJobSpec)
CronJobStatus = __loader(CronJobStatus)
JobTemplateSpec = __loader(JobTemplateSpec)

__all__ = ['JobSpec', 'CronJob', 'CronJobList', 'CronJobSpec', 'CronJobStatus', 'JobTemplateSpec']

