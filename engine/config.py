from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class JobInfo:
    job_id: str
    tasks: list[str]
    input_uri: str | None = None
    output_uri: str | None = None
    options: dict[str, str] = field(default_factory=dict)


def load_job_info() -> JobInfo:
    raw_job_info = os.getenv("JOB_INFO_JSON")
    if not raw_job_info:
        raise ValueError("JOB_INFO_JSON is required")

    try:
        payload = json.loads(raw_job_info)
    except json.JSONDecodeError as exc:
        raise ValueError("JOB_INFO_JSON must be valid JSON") from exc

    if not isinstance(payload, dict):
        raise ValueError("JOB_INFO_JSON must decode to a JSON object")

    job_id = payload.get("job_id")
    tasks = payload.get("tasks")
    input_uri = payload.get("input_uri")
    output_uri = payload.get("output_uri")
    options = payload.get("options", {})

    if not isinstance(job_id, str) or not job_id:
        raise ValueError("JOB_INFO_JSON.job_id must be a non-empty string")

    if not isinstance(tasks, list) or not tasks or not all(
        isinstance(task, str) and task for task in tasks
    ):
        raise ValueError("JOB_INFO_JSON.tasks must be a non-empty list of strings")

    if input_uri is not None and not isinstance(input_uri, str):
        raise ValueError("JOB_INFO_JSON.input_uri must be a string when provided")

    if output_uri is not None and not isinstance(output_uri, str):
        raise ValueError("JOB_INFO_JSON.output_uri must be a string when provided")

    if not isinstance(options, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in options.items()
    ):
        raise ValueError("JOB_INFO_JSON.options must be an object of string values")

    return JobInfo(
        job_id=job_id,
        tasks=tasks,
        input_uri=input_uri,
        output_uri=output_uri,
        options=options,
    )


def describe_environment() -> dict[str, Any]:
    return {
        "project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "region": os.getenv("CLOUD_RUN_REGION"),
        "job_name": os.getenv("CLOUD_RUN_JOB"),
        "execution": os.getenv("CLOUD_RUN_EXECUTION"),
        "task_index": os.getenv("CLOUD_RUN_TASK_INDEX"),
        "task_count": os.getenv("CLOUD_RUN_TASK_COUNT"),
    }


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required")
    return value
