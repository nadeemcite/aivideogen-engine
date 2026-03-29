from __future__ import annotations

import json
import sys

from engine.config import describe_environment, load_job_info
from engine.tasks import run_tasks


def main() -> int:
    print("[runner] starting")
    try:
        job_info = load_job_info()
        print(f"[runner] environment={json.dumps(describe_environment(), sort_keys=True)}")
        print(f"[runner] job_id={job_info.job_id} task_count={len(job_info.tasks)}")
        run_tasks(job_info)
    except Exception as exc:
        print(f"[runner] failed: {exc}", file=sys.stderr)
        return 1

    print(f"[runner] success job_id={job_info.job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
