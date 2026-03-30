# Engine

Sample `uv`-based Python project that builds a Docker image for Google Cloud Run Jobs. This repo only owns the task runner image. Another service can create and execute the Cloud Run Job using the image built from this project.

## Runtime contract

The container reads these required environment variables:

- `JOB_INFO_JSON`: JSON object describing the work to perform
- `DATABASE_URL`: PostgreSQL connection string used after task execution
- `MYVIDS_VIDEO_JOB_RUN_ID`: string identifier for the `"VideoJobRun"` row to update
- `DATABASE_CA_PATH` (optional): CA certificate path used to enable SSL for PostgreSQL connections in production

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
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME'
export MYVIDS_VIDEO_JOB_RUN_ID='sample-video-job-run-id'
# Optional in production when the server requires SSL.
export DATABASE_CA_PATH='/etc/ssl/certs/db-ca.pem'
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
  -e DATABASE_URL='postgresql://USER:PASSWORD@HOST:5432/DBNAME' \
  -e MYVIDS_VIDEO_JOB_RUN_ID='sample-video-job-run-id' \
  -e DATABASE_CA_PATH='/etc/ssl/certs/db-ca.pem' \
  engine:local
```

## Artifact Registry

Example tag and push flow:

```bash
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/REPOSITORY/engine:latest .
docker push us-central1-docker.pkg.dev/PROJECT_ID/REPOSITORY/engine:latest
```

After all tasks succeed, the runner connects to PostgreSQL using `DATABASE_URL`, verifies `"VideoJobRun".id` is a string-typed column, and commits:

```sql
update "VideoJobRun" set status = 'COMPLETED' where id = $1
```

If `DATABASE_CA_PATH` is set, the PostgreSQL connection is created with SSL enabled using that CA certificate.

The external service that owns Cloud Run Job creation/execution should pass all required environment variables when it starts the job.
