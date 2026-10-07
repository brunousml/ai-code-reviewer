import logging
import os
from datetime import datetime
from typing import Union, List

from src.ai_code_reviewer.domain.ports.vcs_service import VCSService
from src.ai_code_reviewer.domain.entities.dora_metrics import (
    DeploymentFrequencyMetrics,
    ChangeFailureRateMetrics,
)
from src.ai_code_reviewer.domain.entities.job import Job

logger = logging.getLogger(__name__)

class GetDoraMetricsUseCase:
    """Use case for calculating DORA metrics based on pipeline jobs."""

    DEPLOY_JOB_NAME = os.getenv("DEPLOY_JOB_NAME", "Deploy master")

    def __init__(self, vcs_service: VCSService):
        self.vcs_service = vcs_service

    def execute(
        self, metric: str, project_path: str, start_date: str, end_date: str, **kwargs
    ) -> Union[DeploymentFrequencyMetrics, ChangeFailureRateMetrics]:
        """Calculates a DORA metric based on the provided metric name."""
        
        logger.info(f"Fetching pipelines for project '{project_path}' from {start_date} to {end_date}.")
        pipelines = self.vcs_service.get_pipelines(project_path, start_date, end_date)

        deployment_jobs: List[Job] = []
        for p in pipelines:
            logger.debug(f"Fetching jobs for pipeline {p.id}")
            jobs = self.vcs_service.list_pipeline_jobs(project_path, p.id)
            # Filter for the specific deploy job
            for job in jobs:
                if job.name == self.DEPLOY_JOB_NAME:
                    deployment_jobs.append(job)

        logger.info(f"Found {len(deployment_jobs)} jobs named '{self.DEPLOY_JOB_NAME}'.")

        if metric == "deployment-frequency":
            return self._calculate_deployment_frequency(project_path, start_date, end_date, deployment_jobs)
        elif metric == "change-failure-rate":
            return self._calculate_change_failure_rate(project_path, start_date, end_date, deployment_jobs)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

    def _calculate_deployment_frequency(
        self, project_path: str, start_date: str, end_date: str, deployment_jobs: List[Job]
    ) -> DeploymentFrequencyMetrics:
        successful_deploys = [j for j in deployment_jobs if j.status == 'success']
        total_successful_deploys = len(successful_deploys)

        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        total_days = (end_dt - start_dt).days + 1

        deployments_per_day = total_successful_deploys / total_days if total_days > 0 else 0
        deployments_per_week = deployments_per_day * 7

        return DeploymentFrequencyMetrics(
            metric="Deployment Frequency",
            project_path=project_path,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_successful_deploys=total_successful_deploys,
            deployments_per_day=deployments_per_day,
            deployments_per_week=deployments_per_week,
        )

    def _calculate_change_failure_rate(
        self, project_path: str, start_date: str, end_date: str, deployment_jobs: List[Job]
    ) -> ChangeFailureRateMetrics:
        total_deployment_jobs = len(deployment_jobs)
        failed_deployment_jobs = len([j for j in deployment_jobs if j.status == 'failed'])

        if total_deployment_jobs > 0:
            failure_rate = (failed_deployment_jobs / total_deployment_jobs) * 100
        else:
            failure_rate = 0

        return ChangeFailureRateMetrics(
            metric="Change Failure Rate",
            project_path=project_path,
            start_date=start_date,
            end_date=end_date,
            total_deployment_jobs=total_deployment_jobs,
            failed_deployment_jobs=failed_deployment_jobs,
            change_failure_rate=failure_rate,
        )
