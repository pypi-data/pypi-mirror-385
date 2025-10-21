# auto-generated: explicit re-exports; wrap dataclasses via loader()
# flake8: noqa
from k8s_models.loader import loader as __loader

from .v1 import CronJob, CronJobList, CronJobSpec, CronJobStatus, Job, JobCondition, JobList, JobSpec, JobStatus, JobTemplateSpec, PodFailurePolicy, PodFailurePolicyOnExitCodesRequirement, PodFailurePolicyOnPodConditionsPattern, PodFailurePolicyRule, SuccessPolicy, SuccessPolicyRule, UncountedTerminatedPods

CronJob = __loader(CronJob)
CronJobList = __loader(CronJobList)
CronJobSpec = __loader(CronJobSpec)
CronJobStatus = __loader(CronJobStatus)
Job = __loader(Job)
JobCondition = __loader(JobCondition)
JobList = __loader(JobList)
JobSpec = __loader(JobSpec)
JobStatus = __loader(JobStatus)
JobTemplateSpec = __loader(JobTemplateSpec)
PodFailurePolicy = __loader(PodFailurePolicy)
PodFailurePolicyOnExitCodesRequirement = __loader(PodFailurePolicyOnExitCodesRequirement)
PodFailurePolicyOnPodConditionsPattern = __loader(PodFailurePolicyOnPodConditionsPattern)
PodFailurePolicyRule = __loader(PodFailurePolicyRule)
SuccessPolicy = __loader(SuccessPolicy)
SuccessPolicyRule = __loader(SuccessPolicyRule)
UncountedTerminatedPods = __loader(UncountedTerminatedPods)

__all__ = ['CronJob', 'CronJobList', 'CronJobSpec', 'CronJobStatus', 'Job', 'JobCondition', 'JobList', 'JobSpec', 'JobStatus', 'JobTemplateSpec', 'PodFailurePolicy', 'PodFailurePolicyOnExitCodesRequirement', 'PodFailurePolicyOnPodConditionsPattern', 'PodFailurePolicyRule', 'SuccessPolicy', 'SuccessPolicyRule', 'UncountedTerminatedPods']

