import json
import xml.etree.ElementTree as ET
import csv
import os
import sys
import glob
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


def _get_pr_metadata(default_branch: str):
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


def _github_context(django_app: str, test_type: str):
    ref_name = os.getenv("GITHUB_REF_NAME", "")
    source_branch, target_branch, pr_title = _get_pr_metadata(ref_name)

    run_id = os.getenv("GITHUB_RUN_ID", "")
    job_name = f"{django_app}-{test_type}" if django_app and test_type else os.getenv(
        "GITHUB_JOB", ""
    )
    job_uid = f"{run_id}:{job_name}" if run_id and job_name else (job_name or run_id)

    return {
        "django_app": django_app,
        "test_type": test_type,
        "run_id": run_id,
        "run_number": os.getenv("GITHUB_RUN_NUMBER", ""),
        "commit_sha": os.getenv("GITHUB_SHA", ""),
        "ref_name": ref_name,
        "target_branch": target_branch,
        "source_branch": source_branch,
        "pr_title": pr_title,
        "workflow_name": os.getenv("GITHUB_WORKFLOW", ""),
        "job_uid": job_uid,
        "job_name": job_name,
        "execution_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def convert_xml_to_csv(xml_path: str, output_csv: str, django_app: str = "", test_type: str = ""):
    if "*" in xml_path:
        xml_files = glob.glob(xml_path, recursive=True)
    else:
        xml_files = [xml_path] if os.path.exists(xml_path) else []

    if not xml_files:
        print(f"Warning: No XML files found at {xml_path}")

    ctx = _github_context(django_app, test_type)
    rows = []

    for source_file in xml_files:
        try:
            root = ET.parse(source_file).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {source_file}: {e}")
            continue

        for suite in root.iter("testsuite"):
            suite_name = suite.attrib.get("name", django_app or "")
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
                    "execution_timestamp": ctx["execution_timestamp"],
                    "job_uid": ctx["job_uid"],
                    "job_name": ctx["job_name"],
                    "run_id": ctx["run_id"],
                    "run_number": ctx["run_number"],
                    "commit_sha": ctx["commit_sha"],
                    "ref_name": ctx["ref_name"],
                    "target_branch": ctx["target_branch"],
                    "source_branch": ctx["source_branch"],
                    "pr_title": ctx["pr_title"],
                    "workflow_name": ctx["workflow_name"],
                    "source_file": source_file,
                })

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output_csv}, rows: {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/convert_junit_to_csv.py <input_xml> <output_csv> [django_app] [test_type]")
        sys.exit(1)

    xml_path = sys.argv[1]
    output_csv = sys.argv[2]
    django_app = sys.argv[3] if len(sys.argv) > 3 else ""
    test_type = sys.argv[4] if len(sys.argv) > 4 else ""

    convert_xml_to_csv(xml_path, output_csv, django_app, test_type)
