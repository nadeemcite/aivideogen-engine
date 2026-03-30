from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from typing import Callable

from engine.config import JobInfo


TaskHandler = Callable[[JobInfo], None]


def probe_ffmpeg(_: JobInfo) -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg is not installed or not on PATH")

    result = subprocess.run(
        ["ffmpeg", "-version"],
        check=True,
        capture_output=True,
        text=True,
    )
    first_line = result.stdout.splitlines()[0] if result.stdout else "unknown"
    print(f"[task:probe_ffmpeg] binary={ffmpeg_path} version={first_line}")


def process_assets(job_info: JobInfo) -> None:
    fingerprint_source = "|".join(
        filter(
            None,
            [
                job_info.job_id,
                job_info.input_uri,
                job_info.output_uri,
                json.dumps(job_info.options, sort_keys=True),
            ],
        )
    )
    fingerprint = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()[:16]
    print(
        "[task:process_assets] simulated processing "
        f"input={job_info.input_uri!r} output={job_info.output_uri!r} "
        f"options={job_info.options} fingerprint={fingerprint}"
    )


def echo_summary(job_info: JobInfo) -> None:
    print(
        "[task:echo_summary] "
        f"job_id={job_info.job_id} tasks={job_info.tasks} "
        f"input_uri={job_info.input_uri!r} output_uri={job_info.output_uri!r}"
    )


TASKS: dict[str, TaskHandler] = {
    "echo_summary": echo_summary,
    "probe_ffmpeg": probe_ffmpeg,
    "process_assets": process_assets,
    "generate_slideshow": lambda _: print("[task:noop] no operation performed"),
}


def run_tasks(job_info: JobInfo) -> None:
    for task_name in job_info.tasks:
        task = TASKS.get(task_name)
        if task is None:
            known_tasks = ", ".join(sorted(TASKS))
            raise ValueError(f"Unknown task {task_name!r}. Known tasks: {known_tasks}")

        print(f"[runner] starting task={task_name}")
        task(job_info)
        print(f"[runner] completed task={task_name}")
