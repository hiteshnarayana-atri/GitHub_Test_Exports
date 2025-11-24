import json
import xml.etree.ElementTree as ET
import glob
import csv
import os
import sys
from datetime import datetime, timezone


FIELDNAMES = [
    "django_app",
    "test_type",
    "suite",
    "class",
    "test_name",
    "status",
    "duration_seconds",
    "test_file",
    "error_message",
    "execution_timestamp",
    "job_uid",
    "job_name",
    "run_id",
    "run_number",
    "commit_sha",
    "ref_name",
    "target_branch",
    "source_branch",
    "pr_title",
    "workflow_name",
    "source_file",
]


def _status(tc):
    if tc.find("failure") is not None:
        return "failed"
    if tc.find("error") is not None:
        return "error"
    if tc.find("skipped") is not None:
        return "skipped"
    return "passed"


def _pr_metadata(default_branch: str):
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return default_branch, default_branch, ""

    try:
        with open(event_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pr = data.get("pull_request", {})
        source_branch = pr.get("head", {}).get("ref", "") or default_branch
        target_branch = pr.get("base", {}).get("ref", "") or default_branch
        pr_title = pr.get("title", "") or ""
        return source_branch, target_branch, pr_title
    except Exception:
        return default_branch, default_branch, ""


def _slug(value: str, max_len: int = 80) -> str:
    value = (value or "").strip().replace(" ", "-")
    cleaned = "".join(c for c in value if c.isalnum() or c in "-_")
    return cleaned[:max_len] or "no-title"


def _infer_from_path(filepath: str):
    if "/notifications/" in filepath:
        django_app = "notifications"
    elif "/base/" in filepath:
        django_app = "base"
    else:
        django_app = "unknown"

    test_type = "cypress" if "/frontend/" in filepath else "pytest"
    return django_app, test_type


def main(xml_pattern: str, output_root: str):
    files = glob.glob(xml_pattern, recursive=True)
    if not files:
        print(f"Error: No XML files found matching {xml_pattern}")
        sys.exit(1)

    ref_name = os.getenv("GITHUB_REF_NAME", "")
    source_branch, target_branch, pr_title = _pr_metadata(ref_name)
    run_id = os.getenv("GITHUB_RUN_ID", "")
    run_number = os.getenv("GITHUB_RUN_NUMBER", "")
    commit_sha = os.getenv("GITHUB_SHA", "")
    workflow_name = os.getenv("GITHUB_WORKFLOW", "")
    execution_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    root_dir = os.path.join(
        output_root,
        target_branch or "unknown-target",
        source_branch or "unknown-source",
        _slug(pr_title),
    )
    os.makedirs(root_dir, exist_ok=True)

    rows = []

    for source_file in files:
        try:
            root = ET.parse(source_file).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {source_file}: {e}")
            continue

        django_app, test_type = _infer_from_path(source_file)
        job_name = f"{django_app}-{test_type}" if django_app != "unknown" else test_type
        job_uid = f"{run_id}:{job_name}" if run_id and job_name else (job_name or run_id)

        for suite in root.iter("testsuite"):
            suite_name = suite.attrib.get("name", "")
            for tc in suite.iter("testcase"):
                msg = ""
                for tag in ("failure", "error", "skipped"):
                    node = tc.find(tag)
                    if node is not None:
                        msg = (node.attrib.get("message") or "").strip()
                        break

                rows.append({
                    "django_app": django_app,
                    "test_type": test_type,
                    "suite": suite_name,
                    "class": tc.attrib.get("classname", ""),
                    "test_name": tc.attrib.get("name", ""),
                    "status": _status(tc),
                    "duration_seconds": tc.attrib.get("time", "0"),
                    "test_file": tc.attrib.get("file", ""),
                    "error_message": msg,
                    "execution_timestamp": execution_ts,
                    "job_uid": job_uid,
                    "job_name": job_name,
                    "run_id": run_id,
                    "run_number": run_number,
                    "commit_sha": commit_sha,
                    "ref_name": ref_name,
                    "target_branch": target_branch,
                    "source_branch": source_branch,
                    "pr_title": pr_title,
                    "workflow_name": workflow_name,
                    "source_file": source_file,
                })

    if not rows:
        print("Error: No test cases found")
        sys.exit(1)

    out_csv = os.path.join(root_dir, "all_tests.csv")
    out_json = os.path.join(root_dir, "all_tests.json")

    with open(out_csv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    with open(out_json, "w") as jh:
        json.dump(rows, jh, indent=2)

    print(f"Wrote {out_csv} and {out_json}, count: {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/merge_junit_tests.py <xml_pattern> <output_root>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
