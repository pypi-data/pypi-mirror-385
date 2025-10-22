from __future__ import annotations

import argparse
import os
from pathlib import Path

from . import __version__
from .config import load_effective_config
from .publisher import plan_dry_run, preflight, publish
from .utils import PublishConfig, default_run_id


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("publish-allure")
    p.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit",
    )
    p.add_argument("--config", help="Path to YAML config (optional)")
    p.add_argument("--bucket")
    p.add_argument("--prefix", default=None)
    p.add_argument("--project")
    p.add_argument("--branch", default=os.getenv("GIT_BRANCH", "main"))
    p.add_argument(
        "--run-id",
        default=os.getenv("ALLURE_RUN_ID", default_run_id()),
    )
    p.add_argument("--cloudfront", default=os.getenv("ALLURE_CLOUDFRONT"))
    p.add_argument(
        "--results",
        "--results-dir",
        dest="results",
        default=os.getenv("ALLURE_RESULTS_DIR", "allure-results"),
        help="Path to allure-results directory (alias: --results-dir)",
    )
    p.add_argument(
        "--report",
        default=os.getenv("ALLURE_REPORT_DIR", "allure-report"),
        help="Output directory for generated Allure static report",
    )
    p.add_argument("--ttl-days", type=int, default=None)
    p.add_argument("--max-keep-runs", type=int, default=None)
    p.add_argument(
        "--sse",
        default=os.getenv("ALLURE_S3_SSE"),
        help="Server-side encryption algorithm (AES256 or aws:kms)",
    )
    p.add_argument(
        "--sse-kms-key-id",
        default=os.getenv("ALLURE_S3_SSE_KMS_KEY_ID"),
        help="KMS Key ID / ARN when --sse=aws:kms",
    )
    p.add_argument(
        "--s3-endpoint",
        default=os.getenv("ALLURE_S3_ENDPOINT"),
        help=("Custom S3 endpoint URL (e.g. http://localhost:4566)"),
    )
    p.add_argument("--summary-json", default=None)
    p.add_argument(
        "--context-url",
        default=os.getenv("ALLURE_CONTEXT_URL"),
        help="Optional hyperlink giving change context (e.g. Jira ticket)",
    )
    p.add_argument(
        "--meta",
        action="append",
        default=[],
        metavar="KEY=VAL",
        help=(
            "Attach arbitrary metadata (repeatable). Example: --meta "
            "jira=PROJ-123 --meta env=staging. Adds dynamic columns to "
            "runs index & manifest."
        ),
    )
    p.add_argument("--dry-run", action="store_true", help="Plan only")
    p.add_argument(
        "--check",
        action="store_true",
        help="Run preflight checks (AWS, allure, inputs)",
    )
    p.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip automatic preflight before publish (not recommended)",
    )
    p.add_argument(
        "--verbose-summary",
        action="store_true",
        help="Print extended summary (CDN prefixes, manifest path, metadata)",
    )
    p.add_argument(
        "--allow-duplicate-prefix-project",
        action="store_true",
        help=(
            "Bypass guard preventing prefix==project duplication. "
            "Only use if you intentionally want that folder layout."
        ),
    )
    p.add_argument(
        "--upload-workers",
        type=int,
        default=None,
        help="Parallel upload worker threads (auto if unset)",
    )
    p.add_argument(
        "--copy-workers",
        type=int,
        default=None,
        help="Parallel copy worker threads for latest promotion",
    )
    p.add_argument(
        "--archive-run",
        action="store_true",
        help="Also produce a compressed archive of the run (tar.gz)",
    )
    p.add_argument(
        "--archive-format",
        choices=["tar.gz", "zip"],
        default="tar.gz",
        help="Archive format when --archive-run is set",
    )
    return p.parse_args()


def _parse_metadata(pairs: list[str]) -> dict | None:
    if not pairs:
        return None
    meta: dict[str, str] = {}
    for raw in pairs:
        if "=" not in raw:
            continue
        k, v = raw.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        safe_k = k.lower().replace("-", "_")
        if safe_k and v:
            meta[safe_k] = v
    return meta or None


def _build_cli_overrides(args: argparse.Namespace) -> dict:
    return {
        "bucket": args.bucket,
        "prefix": args.prefix,
        "project": args.project,
        "branch": args.branch,
        "cloudfront": args.cloudfront,
        "run_id": args.run_id,
        # Region and distribution id are expected from env/YAML; no CLI flags needed
        "ttl_days": args.ttl_days,
        "max_keep_runs": args.max_keep_runs,
        "s3_endpoint": args.s3_endpoint,
        "context_url": args.context_url,
        "sse": args.sse,
        "sse_kms_key_id": args.sse_kms_key_id,
    }


def _effective_config(args: argparse.Namespace) -> tuple[dict, PublishConfig]:
    overrides = _build_cli_overrides(args)
    effective = load_effective_config(overrides, args.config)
    cfg_source = effective.get("_config_file")
    if cfg_source:
        print(f"[config] loaded settings from {cfg_source}")
    missing = [k for k in ("bucket", "project") if not effective.get(k)]
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(
            f"Missing required config values: {missing_list}. Provide via CLI, env, or YAML."
        )
    cfg = PublishConfig(
        bucket=effective["bucket"],
        prefix=effective.get("prefix") or "reports",
        project=effective["project"],
        branch=effective.get("branch") or args.branch,
        run_id=effective.get("run_id") or args.run_id,
        cloudfront_domain=effective.get("cloudfront"),
        aws_region=effective.get("aws_region"),
        cloudfront_distribution_id=effective.get("cloudfront_distribution_id"),
        ttl_days=effective.get("ttl_days"),
        max_keep_runs=effective.get("max_keep_runs"),
        s3_endpoint=effective.get("s3_endpoint"),
        context_url=effective.get("context_url"),
        sse=effective.get("sse"),
        sse_kms_key_id=effective.get("sse_kms_key_id"),
        metadata=_parse_metadata(args.meta),
        upload_workers=args.upload_workers,
        copy_workers=args.copy_workers,
        archive_run=args.archive_run,
        archive_format=args.archive_format if args.archive_run else None,
    )
    # Guard against accidental duplication like prefix==project producing
    # 'reports/reports/<branch>/...' paths. This is usually unintentional
    # and makes report URLs longer / redundant. Fail fast so users can
    # correct config explicitly (they can still deliberately choose this
    # by changing either value slightly, e.g. prefix='reports',
    # project='team-reports').
    if cfg.prefix == cfg.project and not getattr(args, "allow_duplicate_prefix_project", False):
        parts = [
            "Invalid config: prefix and project are identical (",
            f"'{cfg.project}'). ",
            "This yields duplicated S3 paths (",
            f"{cfg.prefix}/{cfg.project}/<branch>/...). ",
            "Set distinct values (e.g. prefix='reports', project='payments').",
        ]
        raise SystemExit("".join(parts))
    return effective, cfg


def _write_json(path: str, payload: dict) -> None:
    import json

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _print_publish_summary(
    cfg: PublishConfig,
    out: dict,
    verbose: bool = False,
) -> None:
    print("Publish complete")
    if out.get("run_url"):
        print(f"Run URL: {out['run_url']}")
    if out.get("latest_url"):
        print(f"Latest URL: {out['latest_url']}")
    # Main aggregated runs index (HTML) at branch root if CDN configured
    if cfg.cloudfront_domain:
        branch_root = f"{cfg.prefix}/{cfg.project}/{cfg.branch}"
        cdn_root = cfg.cloudfront_domain.rstrip("/")
        runs_index_url = f"{cdn_root}/{branch_root}/runs/index.html"
        print(f"Runs Index URL: {runs_index_url}")
    run_prefix = out.get("run_prefix") or cfg.s3_run_prefix
    latest_prefix = out.get("latest_prefix") or cfg.s3_latest_prefix
    print(f"S3 run prefix: s3://{cfg.bucket}/{run_prefix}")
    print(f"S3 latest prefix: s3://{cfg.bucket}/{latest_prefix}")
    print(
        "Report files: "
        f"{out.get('report_files', '?')}  Size: "
        f"{out.get('report_size_bytes', '?')} bytes"
    )
    if verbose and cfg.cloudfront_domain:
        # Duplicate earlier lines but clarify this is the CDN-root mapping
        print("CDN run prefix (index root):", cfg.url_run())
        print("CDN latest prefix (index root):", cfg.url_latest())
    if verbose:
        # Manifest stored at branch root under runs/index.json
        branch_root = f"{cfg.prefix}/{cfg.project}/{cfg.branch}"
        manifest_key = f"{branch_root}/runs/index.json"
        print("Manifest object:", f"s3://{cfg.bucket}/{manifest_key}")
        if cfg.metadata:
            print("Metadata keys:", ", ".join(sorted(cfg.metadata.keys())))
        if cfg.sse:
            print("Encryption:", cfg.sse, cfg.sse_kms_key_id or "")


def main() -> int:  # noqa: C901 (reduced but keep guard just in case)
    args = parse_args()
    if args.version:
        print(__version__)
        return 0
    effective, cfg = _effective_config(args)
    # Construct explicit Paths honoring custom results/report dirs
    paths = None
    try:
        mod = __import__("pytest_allure_host.publisher", fromlist=["Paths"])
        paths = mod.publisher.Paths(
            results=Path(args.results),
            report=Path(args.report),
        )
    except Exception:  # pragma: no cover - defensive fallback
        from .publisher import Paths  # type: ignore

        paths = Paths(results=Path(args.results), report=Path(args.report))

    def _checks_pass(chk: dict) -> bool:
        # Only consider boolean values as pass/fail gates
        bool_vals = [v for v in chk.values() if isinstance(v, bool)]
        return all(bool_vals) if bool_vals else True

    if args.check:
        checks = preflight(cfg, paths=paths)
        print(checks)
        # Concise success line for humans
        if all(v for v in checks.values() if isinstance(v, bool)):
            bucket = cfg.bucket
            region = getattr(cfg, "aws_region", None) or checks.get("bucket_region") or "?"
            dist = (
                getattr(cfg, "cloudfront_distribution_id", None)
                or checks.get("cloudfront_distribution_id")
                or "?"
            )
            print(f"[preflight] OK — bucket={bucket}, region={region}, distribution={dist}")
        if not _checks_pass(checks):
            return 2
    if args.dry_run:
        plan = plan_dry_run(cfg, paths=paths)
        print(plan)
        if args.summary_json:
            _write_json(args.summary_json, plan)
        return 0
    # Automatic preflight prior to publish unless explicitly skipped
    if not args.skip_preflight:
        checks = preflight(cfg, paths=paths)
        if not _checks_pass(checks):
            print("Preflight failed; refusing to publish. Details:")
            print(checks)
            return 2
        # Concise success line for humans
        bucket = cfg.bucket
        region = getattr(cfg, "aws_region", None) or checks.get("bucket_region") or "?"
        dist = (
            getattr(cfg, "cloudfront_distribution_id", None)
            or checks.get("cloudfront_distribution_id")
            or "?"
        )
        print(f"[preflight] OK — bucket={bucket}, region={region}, distribution={dist}")
    out = publish(cfg, paths=paths)
    print(out)  # raw dict for backward compatibility
    _print_publish_summary(cfg, out, verbose=args.verbose_summary)
    if args.summary_json:
        _write_json(args.summary_json, out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
