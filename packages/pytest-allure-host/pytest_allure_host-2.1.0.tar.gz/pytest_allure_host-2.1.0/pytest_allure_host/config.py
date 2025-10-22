"""Configuration loading utilities (YAML + env) for Allure hosting publisher.

Precedence (highest first):
1. Explicit CLI / pytest flag values
2. Environment variables (ALLURE_BUCKET, ALLURE_PREFIX, ...)
3. YAML file values (provided via --config or auto-discovered)
4. Built-in defaults

Auto-discovery order if --config not supplied:
- ./allure-host.yml
- ./allure-host.yaml
- ./.allure-host.yml
- ./.allure-host.yaml

YAML schema (example):

    bucket: my-reports-bucket
    prefix: reports
    project: payments
    branch: main
    ttl_days: 30
    max_keep_runs: 20
    cloudfront: https://reports.example.com
    retention:
      default_ttl_days: 30           # alias of ttl_days
      max_keep_runs: 20              # duplicate path accepted

Unknown keys are ignored (forward compatible).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILENAMES = [
    # YAML (legacy / original)
    "allure-host.yml",
    "allure-host.yaml",
    ".allure-host.yml",
    ".allure-host.yaml",
    # TOML (new preferred simple format)
    "allurehost.toml",
    ".allurehost.toml",
    # Additional generic app config names people often use:
    "application.yml",
    "application.yaml",
]

ENV_MAP = {
    "bucket": "ALLURE_BUCKET",
    "prefix": "ALLURE_PREFIX",
    "project": "ALLURE_PROJECT",
    "branch": "ALLURE_BRANCH",
    "cloudfront": "ALLURE_CLOUDFRONT",
    # Optional explicit region and distribution id for stricter preflight
    "aws_region": "ALLURE_AWS_REGION",
    "cloudfront_distribution_id": "ALLURE_CLOUDFRONT_DISTRIBUTION_ID",
    "run_id": "ALLURE_RUN_ID",
    "ttl_days": "ALLURE_TTL_DAYS",
    "max_keep_runs": "ALLURE_MAX_KEEP_RUNS",
    "s3_endpoint": "ALLURE_S3_ENDPOINT",
    "context_url": "ALLURE_CONTEXT_URL",
}


@dataclass
class LoadedConfig:
    source_file: Path | None
    data: dict[str, Any]


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            content = yaml.safe_load(f) or {}
        if not isinstance(content, dict):
            return {}
        return content
    except FileNotFoundError:
        return {}
    except Exception:
        # best effort - ignore malformed file
        return {}


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        import sys

        if sys.version_info >= (3, 11):  # stdlib tomllib
            import tomllib  # type: ignore
        else:  # fallback to optional dependency
            import tomli as tomllib  # type: ignore
    except Exception:  # pragma: no cover - toml not available
        return {}
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:  # pragma: no cover - malformed
        return {}


def discover_yaml_config(explicit: str | None = None) -> LoadedConfig:
    if explicit:
        p = Path(explicit)
        if p.suffix.lower() == ".toml":
            return LoadedConfig(
                source_file=p if p.exists() else None,
                data=_read_toml(p),
            )
        return LoadedConfig(
            source_file=p if p.exists() else None,
            data=_read_yaml(p),
        )
    for name in CONFIG_FILENAMES:
        p = Path(name)
        if p.exists():
            if p.suffix.lower() == ".toml":
                return LoadedConfig(source_file=p, data=_read_toml(p))
            return LoadedConfig(source_file=p, data=_read_yaml(p))
    return LoadedConfig(source_file=None, data={})


def merge_config(
    yaml_cfg: dict[str, Any],
    env: dict[str, str],
    cli_overrides: dict[str, Any],
) -> dict[str, Any]:
    merged: dict[str, Any] = {}

    # start with YAML
    merged.update(yaml_cfg)

    # retention nested block normalization
    retention = yaml_cfg.get("retention")
    if isinstance(retention, dict):
        merged.setdefault("ttl_days", retention.get("default_ttl_days"))
        merged.setdefault("max_keep_runs", retention.get("max_keep_runs"))

    # env overrides
    for key, env_var in ENV_MAP.items():
        if env_var in env and env[env_var]:
            merged[key] = env[env_var]

    # explicit CLI overrides (ignore None only)
    for k, v in cli_overrides.items():
        if v is not None:
            merged[k] = v

    # type adjust
    for int_field in ("ttl_days", "max_keep_runs"):
        if int_field in merged and merged[int_field] not in (None, ""):
            try:
                merged[int_field] = int(merged[int_field])
            except ValueError:
                merged[int_field] = None

    return merged


def load_effective_config(
    cli_args: dict[str, Any], explicit_config: str | None = None
) -> dict[str, Any]:
    loaded = discover_yaml_config(explicit_config)
    data = merge_config(loaded.data, os.environ, cli_args)
    data["_config_file"] = str(loaded.source_file) if loaded.source_file else None
    return data
