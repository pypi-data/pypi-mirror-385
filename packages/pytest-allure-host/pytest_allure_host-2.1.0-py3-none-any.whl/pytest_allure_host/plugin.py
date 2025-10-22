from __future__ import annotations

import json
import os

import pytest
from botocore.exceptions import BotoCoreError, ClientError

from .config import load_effective_config
from .publisher import plan_dry_run, preflight, publish
from .utils import PublishConfig, default_run_id


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("allure-host")
    group.addoption("--allure-bucket", action="store", help="S3 bucket")
    group.addoption("--allure-prefix", action="store", default="reports")
    group.addoption("--allure-project", action="store", help="Project name")
    group.addoption(
        "--allure-branch",
        action="store",
        default=os.getenv("GIT_BRANCH", "main"),
    )
    group.addoption(
        "--allure-cloudfront",
        action="store",
        default=os.getenv("ALLURE_CLOUDFRONT"),
    )
    group.addoption(
        "--allure-run-id",
        action="store",
        default=os.getenv("ALLURE_RUN_ID", default_run_id()),
    )
    group.addoption("--allure-ttl-days", action="store", type=int, default=None)
    group.addoption("--allure-max-keep-runs", action="store", type=int, default=None)
    group.addoption("--allure-summary-json", action="store", default=None)
    group.addoption("--allure-dry-run", action="store_true")
    group.addoption("--allure-check", action="store_true")
    group.addoption(
        "--allure-context-url",
        action="store",
        default=os.getenv("ALLURE_CONTEXT_URL"),
        help="Optional context hyperlink (e.g. Jira ticket)",
    )
    group.addoption(
        "--allure-config",
        action="store",
        default=None,
        help="YAML config file path (optional)",
    )


def pytest_terminal_summary(  # noqa: C901 - central orchestration, readable
    terminalreporter: pytest.TerminalReporter, exitstatus: int
) -> None:
    config = terminalreporter.config
    bucket = config.getoption("allure_bucket")
    project = config.getoption("allure_project")
    if not bucket or not project:
        return
    prefix = config.getoption("allure_prefix")
    branch = config.getoption("allure_branch")
    cloudfront = config.getoption("allure_cloudfront")
    run_id = config.getoption("allure_run_id")
    ttl_days = config.getoption("allure_ttl_days")
    max_keep_runs = config.getoption("allure_max_keep_runs")
    summary_json = config.getoption("allure_summary_json")
    context_url = config.getoption("allure_context_url")

    cli_overrides = {
        "bucket": bucket,
        "prefix": prefix,
        "project": project,
        "branch": branch,
        "cloudfront": cloudfront,
        "run_id": run_id,
        "ttl_days": ttl_days,
        "max_keep_runs": max_keep_runs,
        "context_url": context_url,
    }
    effective = load_effective_config(cli_overrides, config.getoption("allure_config"))
    cfg_source = effective.get("_config_file")
    if cfg_source:
        terminalreporter.write_line(f"[allure-host] config file: {cfg_source}")
    # Minimal required
    if not effective.get("bucket") or not effective.get("project"):
        return
    pub_cfg = PublishConfig(
        bucket=effective["bucket"],
        prefix=effective.get("prefix") or "reports",
        project=effective["project"],
        branch=effective.get("branch") or branch,
        run_id=effective.get("run_id") or run_id,
        cloudfront_domain=effective.get("cloudfront"),
        ttl_days=effective.get("ttl_days"),
        max_keep_runs=effective.get("max_keep_runs"),
        context_url=effective.get("context_url"),
    )

    try:
        if config.getoption("allure_check"):
            checks = preflight(pub_cfg)
            terminalreporter.write_line(f"Allure preflight: {checks}")
            if summary_json:
                with open(summary_json, "w", encoding="utf-8") as f:
                    json.dump(checks, f, indent=2)
            if not all(checks.values()):
                return
        if config.getoption("allure_dry_run"):
            plan = plan_dry_run(pub_cfg)
            terminalreporter.write_line(f"Allure plan: {plan}")
            if summary_json:
                with open(summary_json, "w", encoding="utf-8") as f:
                    json.dump(plan, f, indent=2)
            return
        out = publish(pub_cfg)
        terminalreporter.write_line(
            f"Allure report published to:\n"
            f"- run: {out.get('run_url') or pub_cfg.s3_run_prefix}\n"
            f"- latest: {out.get('latest_url') or pub_cfg.s3_latest_prefix}"
        )
        if summary_json:
            with open(summary_json, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
    except (ClientError, BotoCoreError, OSError, ValueError) as e:
        # Known error categories: AWS client, IO, JSON/value issues
        terminalreporter.write_line(f"Allure publish failed: {e}")
    except Exception as e:  # noqa: BLE001
        # Fallback catch-all to prevent pytest terminal crash; log generic
        terminalreporter.write_line(f"Allure publish failed with unexpected error: {e}")
