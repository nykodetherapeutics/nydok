"""GitLab REST API client for the code review and pipeline logs reports.

Configured by the environment variables GITLAB_URL and GITLAB_TOKEN.
"""

import os
from typing import Any
from urllib.parse import quote_plus

import requests  # type: ignore

# Seconds to wait for GitLab to connect or send data; without it a stalled request hangs forever
TIMEOUT = 60


def get_api_url() -> str:
    """Return the REST API URL of the GitLab instance in GITLAB_URL."""
    if not os.environ.get("GITLAB_URL"):
        raise RuntimeError("Environment variable GITLAB_URL is required, but not set")
    return os.environ["GITLAB_URL"] + "/api/v4"


def get_gitlab_token() -> str:
    """Return the GitLab access token in GITLAB_TOKEN."""
    if not os.environ.get("GITLAB_TOKEN"):
        raise RuntimeError("Environment variable GITLAB_TOKEN is required, but not set")
    return os.environ["GITLAB_TOKEN"]


def _session() -> requests.Session:
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {get_gitlab_token()}"
    return session


def _get_paginated_results(session: requests.Session, url: str, params: dict[str, Any]) -> list[Any]:
    """Return the items of all pages of a GitLab list endpoint."""
    params = dict(params)
    params.setdefault("per_page", 100)

    results: list[Any] = []
    next_url: str | None = url
    while next_url:
        resp = session.get(next_url, params=params, timeout=TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"Resource {next_url} returned status code {resp.status_code}.\n{resp.text}")
        results.extend(resp.json())
        next_url = resp.links.get("next", {}).get("url")
        params = {}  # The next page's URL already has the query parameters
    return results


def get_commits_for_ref(repo_path: str, to_ref: str | None = None, from_ref: str | None = None) -> list[str]:
    """Return the IDs of the commits up to `to_ref`, starting after `from_ref` if given."""
    api_commits = _get_paginated_results(
        _session(),
        get_api_url() + f"/projects/{quote_plus(repo_path)}/repository/commits",
        {"ref_name": f"{from_ref}...{to_ref or ''}" if from_ref else to_ref},
    )
    return [c["id"] for c in api_commits]


def fetch_mergerequests(repo_path: str) -> list[dict[str, str]]:
    """Return the merged merge requests of a project, with commit, title, date, author and reviewers."""
    api_mrs = _get_paginated_results(
        _session(),
        get_api_url() + f"/projects/{quote_plus(repo_path)}/merge_requests",
        {"state": "merged"},
    )
    return [
        {
            "merge_commit_sha": mr["merge_commit_sha"],
            "title": mr["title"],
            "merged_at": mr["merged_at"],
            "author": mr["author"]["name"],
            "approved_by": ",".join(sorted(r["name"] for r in mr["reviewers"])),
        }
        for mr in api_mrs
    ]


def get_pipeline_logs(repo_path: str, pipeline_id: int, job_names: list[str] | None = None) -> dict[str, str]:
    """Return the log of each finished job in a pipeline, by job name, optionally only of `job_names`."""
    session = _session()
    project_url = get_api_url() + f"/projects/{quote_plus(repo_path)}"
    api_jobs = _get_paginated_results(
        session,
        f"{project_url}/pipelines/{pipeline_id}/jobs",
        {"scope": ["failed", "success"]},
    )

    logs: dict[str, str] = {}
    for job in api_jobs:
        if job_names and job["name"] not in job_names:
            continue

        resp = session.get(f"{project_url}/jobs/{job['id']}/trace", timeout=TIMEOUT)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to obtain log for job {job['id']}")

        logs[job["name"]] = resp.text

    return logs
