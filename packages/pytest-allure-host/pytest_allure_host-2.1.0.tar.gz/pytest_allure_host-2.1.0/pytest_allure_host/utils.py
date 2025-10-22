from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path


def default_run_id() -> str:
    from datetime import datetime

    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")


def build_s3_keys(
    prefix: str,
    project: str,
    branch: str,
    run_id: str,
) -> dict[str, str]:
    base = f"{prefix.rstrip('/')}/{project}/{branch}"
    return {"run": f"{base}/{run_id}/", "latest": f"{base}/latest/"}


def branch_root(prefix: str, project: str, branch: str) -> str:
    return f"{prefix.rstrip('/')}/{project}/{branch}"


def cache_control_for_key(key: str) -> str:
    if key.endswith("index.html"):
        return "no-cache"
    # widgets optional no-cache could be configurable later
    if "/widgets/" in key:
        return "no-cache"
    # History JSON (e.g., latest/history/history-trend.json) changes frequently
    # and should not be cached aggressively to ensure trend views refresh.
    if "/history/" in key and key.endswith(".json"):
        return "no-cache"
    return "public, max-age=31536000, immutable"


def guess_content_type(path: Path) -> str | None:
    ctype, _ = mimetypes.guess_type(str(path))
    # Common overrides if needed later
    return ctype or None


@dataclass
class PublishConfig:
    bucket: str
    prefix: str
    project: str
    branch: str
    run_id: str
    cloudfront_domain: str | None = None
    # Optional explicit region and CloudFront distribution id for stricter preflight
    aws_region: str | None = None
    cloudfront_distribution_id: str | None = None
    ttl_days: int | None = None
    max_keep_runs: int | None = None
    s3_endpoint: str | None = None  # custom S3 endpoint (e.g. LocalStack)
    # optional link to change context (e.g. Jira ticket / work item)
    context_url: str | None = None
    # encryption parameters (optional)
    sse: str | None = None  # e.g. 'AES256' or 'aws:kms'
    sse_kms_key_id: str | None = None
    # arbitrary metadata (jira ticket, environment, etc.)
    metadata: dict | None = None
    # performance tuning
    upload_workers: int | None = None  # parallel upload threads
    copy_workers: int | None = None  # parallel copy threads
    # optional archive artifact (compressed run bundle)
    archive_run: bool | None = None
    archive_format: str | None = None  # 'tar.gz' or 'zip'
    # UI feature toggles
    # allow disabling summary cards dashboard if desired
    summary_cards: bool = True

    @property
    def s3_run_prefix(self) -> str:
        keys = build_s3_keys(
            self.prefix,
            self.project,
            self.branch,
            self.run_id,
        )
        return keys["run"]

    @property
    def s3_latest_prefix(self) -> str:
        keys = build_s3_keys(
            self.prefix,
            self.project,
            self.branch,
            self.run_id,
        )
        return keys["latest"]

    @property
    def s3_latest_prefix_tmp(self) -> str:
        """Temporary staging prefix used during two-phase latest promotion.

        Mirrors publish(): objects are first copied into latest_tmp/ then a
        delete + copy sequence promotes them into latest/. Exposed so
        plan_dry_run can surface this path for CI planning & tests.
        """
        root = f"{self.prefix.rstrip('/')}/{self.project}/{self.branch}"
        return f"{root}/latest_tmp/"

    def url_run(self) -> str | None:
        if not self.cloudfront_domain:
            return None
        base = (
            f"{self.cloudfront_domain.rstrip('/')}/{self.prefix}/"
            f"{self.project}/{self.branch}/{self.run_id}/"
        )
        return base

    def url_latest(self) -> str | None:
        if not self.cloudfront_domain:
            return None
        base = (
            f"{self.cloudfront_domain.rstrip('/')}/{self.prefix}/"
            f"{self.project}/{self.branch}/latest/"
        )
        return base


def compute_dir_size(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def merge_manifest(existing: dict | None, new_entry: dict) -> dict:
    base = existing or {
        "schema": 1,
        "project": new_entry.get("project"),
        "branch": new_entry.get("branch"),
        "updated": 0,
        "runs": [],
    }
    runs = [r for r in base.get("runs", []) if r.get("run_id") != new_entry["run_id"]]
    runs.append(new_entry)
    runs.sort(key=lambda r: r.get("time", 0), reverse=True)
    base["runs"] = runs
    from time import time

    base["updated"] = int(time())
    return base
