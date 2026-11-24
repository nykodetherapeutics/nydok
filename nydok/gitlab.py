import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests  # type: ignore

# Seconds to wait for GitLab to connect or send data; without it a stalled request hangs forever
TIMEOUT = 60


def get_api_url() -> str:
    if not os.environ.get("GITLAB_URL"):
        raise RuntimeError("Environment variable GITLAB_URL is required, but not set")
    return os.environ["GITLAB_URL"] + "/api/v4"


def get_gitlab_token() -> str:
    if not os.environ.get("GITLAB_TOKEN"):
        raise RuntimeError("Environment variable GITLAB_TOKEN is required, but not set")
    return os.environ["GITLAB_TOKEN"]


def _get_paginated_results(url: str, params: Dict[str, Any]) -> List[Any]:
    params = dict(params)
    params.setdefault("per_page", 100)

    def _get_results(next_page: Optional[str] = None):
        fetch_url = next_page if next_page else url
        resp = requests.get(
            fetch_url,
            params=params,
            headers={"Authorization": f"Bearer {get_gitlab_token()}"},
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Resource {fetch_url} returned status code {resp.status_code}.\n{resp.text}"
            )

        return resp.json(), resp.links.get("next", {}).get("url")

    api_results, next_page = _get_results()
    while next_page:
        next_jobs, next_page = _get_results(next_page)
        api_results.extend(next_jobs)
    return api_results


def get_commits_for_ref(
    repo_path: str, to_ref: Optional[str] = None, from_ref: Optional[str] = None
) -> List[str]:
    """Fetches all commit ids for given branch"""

    url_encoded_repo_path = quote_plus(repo_path)

    api_commits = _get_paginated_results(
        get_api_url() + f"/projects/{url_encoded_repo_path}/repository/commits",
        {"ref_name": f"{from_ref}...{to_ref or ''}" if from_ref else to_ref},
    )

    commits = [c["id"] for c in api_commits]
    return commits


def fetch_mergerequests(repo_path: str) -> List[Dict[str, str]]:
    url_encoded_repo_path = quote_plus(repo_path)

    api_mrs = _get_paginated_results(
        get_api_url() + f"/projects/{url_encoded_repo_path}/merge_requests",
        {
            "state": "merged",
        },
    )

    merge_requests = []
    for mr in api_mrs:
        merge_requests.append(
            {
                "merge_commit_sha": mr["merge_commit_sha"],
                "title": mr["title"],
                "merged_at": mr["merged_at"],
                "author": mr["author"]["name"],
                "approved_by": ",".join(sorted(r["name"] for r in mr["reviewers"])),
            }
        )
    return merge_requests


def get_pipeline_logs(
    repo_path: str, pipeline_id: int, job_names: Optional[List[str]] = None
) -> Dict[str, str]:
    url_encoded_repo_path = quote_plus(repo_path)

    api_jobs = _get_paginated_results(
        get_api_url() + f"/projects/{url_encoded_repo_path}/pipelines/{str(pipeline_id)}/jobs",
        {
            "scope": ["failed", "success"],
        },
    )

    logs: Dict[str, str] = {}
    for job in api_jobs:
        if job_names and job["name"] not in job_names:
            continue

        resp = requests.get(
            get_api_url() + f"/projects/{url_encoded_repo_path}/jobs/{str(job['id'])}/trace",
            headers={"Authorization": f"Bearer {get_gitlab_token()}"},
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to obtain log for job {job['id']}")

        logs[job["name"]] = resp.text

    return logs
