# Engine

Sample `uv`-based Python project that builds a Docker image for Google Cloud Run Jobs. This repo only owns the task runner image. Another service can create and execute the Cloud Run Job using the image built from this project.

## Runtime contract

The container reads one required environment variable:

- `JOB_INFO_JSON`: JSON object describing the work to perform

Example payload:

```json
{
  "job_id": "sample-001",
  "tasks": ["echo_summary", "probe_ffmpeg", "process_assets"],
  "input_uri": "gs://example-bucket/input.mp4",
  "output_uri": "gs://example-bucket/output/",
  "options": {
    "preset": "fast",
    "notify": "false"
  }
}
```

Supported sample tasks:

- `echo_summary`
- `probe_ffmpeg`
- `process_assets`

## Local development

Create the lockfile and sync dependencies:

```bash
uv lock
uv sync
```

Run locally:

```bash
export JOB_INFO_JSON='{"job_id":"sample-001","tasks":["echo_summary","probe_ffmpeg","process_assets"],"input_uri":"gs://example-bucket/input.mp4","output_uri":"gs://example-bucket/output/","options":{"preset":"fast","notify":"false"}}'
uv run engine-job
```

## Docker image

The image uses:

- `python:3.12-slim-bookworm` as the base image
- `uv` for dependency installation and execution
- Debian `ffmpeg` installed with `apt-get`

Build locally:

```bash
docker build -t engine:local .
```

Run locally:

```bash
docker run --rm \
  -e JOB_INFO_JSON='{"job_id":"sample-001","tasks":["echo_summary","probe_ffmpeg","process_assets"],"input_uri":"gs://example-bucket/input.mp4","output_uri":"gs://example-bucket/output/","options":{"preset":"fast","notify":"false"}}' \
  engine:local
```

## Artifact Registry

Example tag and push flow:

```bash
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/REPOSITORY/engine:latest .
docker push us-central1-docker.pkg.dev/PROJECT_ID/REPOSITORY/engine:latest
```

The external service that owns Cloud Run Job creation/execution should pass `JOB_INFO_JSON` when it starts the job.
