from dataclasses import dataclass

@dataclass
class DeploymentFrequencyMetrics:
    metric: str
    project_path: str
    start_date: str
    end_date: str
    total_days: int
    total_successful_deploys: int
    deployments_per_day: float
    deployments_per_week: float

@dataclass
class ChangeFailureRateMetrics:
    metric: str
    project_path: str
    start_date: str
    end_date: str
    total_deployment_jobs: int
    failed_deployment_jobs: int
    change_failure_rate: float
