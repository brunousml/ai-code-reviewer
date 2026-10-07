import json
import csv
import io
from tabulate import tabulate
from dataclasses import asdict, is_dataclass
from typing import Any, List, Dict, Union

from src.code_review_agent.domain.entities.pipeline import Pipeline
from src.code_review_agent.domain.entities.dora_metrics import (
    DeploymentFrequencyMetrics,
    ChangeFailureRateMetrics,
)

# A generic type for what can be formatted
Formattable = Union[DeploymentFrequencyMetrics, ChangeFailureRateMetrics, List[Dict[str, Any]], List[Pipeline]]

def _format_deployment_frequency_table(metrics: DeploymentFrequencyMetrics) -> str:
    data = asdict(metrics)
    headers = ["Metric", "Value"]
    table_data = [
        ["DORA Deployment Frequency", ""],
        ["Project Path", data["project_path"]],
        ["Period", f'{data["start_date"]} to {data["end_date"]}'],
        ["Total Days", data["total_days"]],
        ["Total Successful Deploys (deploy job)", data["total_successful_deploys"]],
        ["Deployments per Day", f'{data["deployments_per_day"]:.2f}'],
        ["Deployments per Week", f'{data["deployments_per_week"]:.2f}'],
    ]
    return tabulate(table_data, headers=headers, tablefmt="grid")

def _format_change_failure_rate_table(metrics: ChangeFailureRateMetrics) -> str:
    data = asdict(metrics)
    headers = ["Metric", "Value"]
    table_data = [
        ["DORA Change Failure Rate", ""],
        ["Project Path", data["project_path"]],
        ["Period", f'{data["start_date"]} to {data["end_date"]}'],
        ["Total Deployment Jobs", data["total_deployment_jobs"]],
        ["Failed Deployment Jobs", data["failed_deployment_jobs"]],
        ["Change Failure Rate", f'{data["change_failure_rate"]:.2f}%'],
    ]
    return tabulate(table_data, headers=headers, tablefmt="grid")

def _format_pipelines_table(pipelines: List[Pipeline]) -> str:
    headers = ["ID", "Status", "Source", "Ref", "Created At", "URL"]
    table_data = [
        [p.id, p.status, p.source, p.ref, p.created_at, p.web_url]
        for p in pipelines
    ]
    return tabulate(table_data, headers=headers, tablefmt="grid")

def _format_merged_mrs_table(mrs: List[Dict[str, Any]]) -> str:
    headers = ["IID", "Title", "Author", "Merged At", "URL"]
    table_data = [
        [mr.get('iid'), mr.get('title'), mr.get('author'), mr.get('merged_at'), mr.get('url')]
        for mr in mrs
    ]
    return tabulate(table_data, headers=headers, tablefmt="grid")

def format_as_table(data: Formattable) -> str:
    """Formats various data types as a table."""
    if isinstance(data, DeploymentFrequencyMetrics):
        return _format_deployment_frequency_table(data)
    elif isinstance(data, ChangeFailureRateMetrics):
        return _format_change_failure_rate_table(data)
    elif isinstance(data, list):
        if not data:
            return "No data to display."
        
        first_item = data[0]
        if isinstance(first_item, Pipeline):
            return _format_pipelines_table(data)
        elif isinstance(first_item, dict) and 'merged_at' in first_item:
            return _format_merged_mrs_table(data)
        else:
            if isinstance(first_item, dict):
                headers = list(first_item.keys())
                table_data = [list(d.values()) for d in data]
                return tabulate(table_data, headers=headers, tablefmt="grid")
            else:
                 raise TypeError(f"Unsupported list element type for table formatting: {type(first_item)}")
    else:
        raise TypeError(f"Unsupported data type for table formatting: {type(data)}")

def format_as_json(data: Formattable) -> str:
    """Formats data as a JSON string."""
    def default_serializer(o):
        if is_dataclass(o):
            return asdict(o)
        return str(o) # Fallback for other types like datetime

    if isinstance(data, list):
        return json.dumps([default_serializer(item) for item in data], indent=4, default=default_serializer)
    
    return json.dumps(data, indent=4, default=default_serializer)

def format_as_csv(data: Formattable) -> str:
    """Formats data as a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)

    if isinstance(data, list):
        if not data:
            return ""
        
        first_item = data[0]
        if is_dataclass(first_item):
            dict_data = [asdict(item) for item in data]
        elif isinstance(first_item, dict):
            dict_data = data
        else:
            raise TypeError(f"Unsupported list element type for CSV formatting: {type(first_item)}")
        
        if not dict_data:
            return ""
            
        headers = list(dict_data[0].keys())
        writer.writerow(headers)
        for item in dict_data:
            writer.writerow(item.values())

    elif is_dataclass(data):
        dict_data = asdict(data)
        writer.writerow(dict_data.keys())
        writer.writerow(dict_data.values())
    
    else:
        raise TypeError(f"Unsupported data type for CSV formatting: {type(data)}")

    return output.getvalue()
