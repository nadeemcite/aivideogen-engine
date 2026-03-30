from __future__ import annotations

import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from psycopg import connect
from psycopg.rows import tuple_row

from engine.config import get_required_env


def _normalize_database_url(database_url: str) -> tuple[str, str | None]:
    parts = urlsplit(database_url)
    schema_name: str | None = None
    filtered_query: list[tuple[str, str]] = []

    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        if key == "schema":
            schema_name = value
            continue
        filtered_query.append((key, value))

    normalized_url = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(filtered_query), parts.fragment)
    )
    return normalized_url, schema_name


def mark_video_job_run_completed() -> str:
    database_url, schema_name = _normalize_database_url(get_required_env("DATABASE_URL"))
    video_job_run_id = get_required_env("MYVIDS_VIDEO_JOB_RUN_ID")

    connect_kwargs: dict[str, str] = {}
    if schema_name:
        connect_kwargs["options"] = f"-c search_path={schema_name}"

    database_ca_path = os.getenv("DATABASE_CA_PATH")
    if database_ca_path:
        connect_kwargs["sslmode"] = "require"
        connect_kwargs["sslrootcert"] = database_ca_path

    with connect(database_url, **connect_kwargs) as conn:
        with conn.cursor(row_factory=tuple_row) as cur:
            cur.execute(
                """
                select pg_typeof(id)::text
                from "VideoJobRun"
                where id = %s
                limit 1
                """,
                (video_job_run_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(
                    f'No "VideoJobRun" row found for MYVIDS_VIDEO_JOB_RUN_ID={video_job_run_id!r}'
                )

            id_type = row[0]
            if id_type not in {"text", "character varying", "varchar"}:
                raise TypeError(
                    f'"VideoJobRun".id must be a string column, got database type {id_type!r}'
                )

            cur.execute(
                """
                update "VideoJobRun"
                set status = 'COMPLETED'
                where id = %s
                """,
                (video_job_run_id,),
            )
            if cur.rowcount != 1:
                raise RuntimeError(
                    f'Expected to update 1 "VideoJobRun" row, updated {cur.rowcount}'
                )

        conn.commit()

    return video_job_run_id
