import json
import xml.etree.ElementTree as ET
import csv
import os
import sys
import glob
from datetime import datetime, timezone

def _status(tc):
    """Determine the status of a test case based on its XML tags."""
    return ('failed' if tc.find('failure') is not None else
            'error'  if tc.find('error')   is not None else
            'skipped'if tc.find('skipped') is not None else 'passed')

def _get_pr_metadata(default_branch):
    """Extract PR metadata from GitHub event file"""

    event_path = os.getenv('GITHUB_EVENT_PATH')
    if not event_path or not os.path.exists(event_path):
        return default_branch,default_branch,""
    
    try:
        with open(event_path, 'r',encoding="utf-8") as f:
            pr = json.load(f).get("pull_request", {})

        return (
            pr.get("head", {}).get("ref", "") or default_branch,
            pr.get("base", {}).get("ref", "") or default_branch,
            pr.get("title", "") or ""
        )
    except Exception:
        return default_branch, default_branch, ""
    

def _get_github_metadata():
    """Collect GitHub Actions environment variables"""
    ref_name = os.getenv("GITHUB_REF_NAME", "")
    source_branch, target_branch, pr_title = _get_pr_metadata(ref_name)
    
    django_app = sys.argv[3] if len(sys.argv) > 3 else ""
    test_type = sys.argv[4] if len(sys.argv) > 4 else ""
    job_name = f"{django_app}-{test_type}" if django_app and test_type else os.getenv("GITHUB_JOB", "")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    
    return {
        'job_uid': f"{run_id}:{job_name}" if run_id and job_name else (job_name or run_id),
        'job_name': job_name,
        'run_id': run_id,
        'run_number': os.getenv("GITHUB_RUN_NUMBER", ""),
        'commit_sha': os.getenv("GITHUB_SHA", ""),
        'ref_name': ref_name,
        'target_branch': target_branch,
        'source_branch': source_branch,
        'pr_title': pr_title,
        'workflow_name': os.getenv("GITHUB_WORKFLOW", ""),
        'timestamp': datetime.now(timezone.utc).isoformat(timespec="seconds")
    }
    
def convert_xml_to_csv(xml_path, output_csv, django_app='', test_type=''):
    """Convert JUnit XML test results to CSV format."""
    xml_files = glob.glob(xml_path, recursive=True) if '*' in xml_path else ([xml_path] if os.path.exists(xml_path) else [])
    if not xml_files:
        print(f"Warning: No XML files found at {xml_path}")

    gh = _get_github_metadata()
    rows = []

    for xf in xml_files:
        try:
            root = ET.parse(xf).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {xf}: {e}")
            continue

        for suite in root.iter('testsuite'):
            suite_name = suite.attrib.get('name', django_app or '')
            for tc in suite.iter('testcase'):
                msg = next((tc.find(tag).attrib.get('message', '').strip() 
                           for tag in ('failure', 'error', 'skipped') if tc.find(tag) is not None), '')

                rows.append([
                    django_app, test_type, suite_name,
                    tc.attrib.get('classname', ''),
                    tc.attrib.get('name', ''),
                    _status(tc),
                    tc.attrib.get('time', '0'),
                    tc.attrib.get('file', ''),
                    msg,
                    gh['timestamp'], gh['job_uid'], gh['job_name'],
                    gh['run_id'], gh['run_number'], gh['commit_sha'],
                    gh['ref_name'], gh['target_branch'], gh['source_branch'],
                    gh['pr_title'], gh['workflow_name'], xf
                ])

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='') as f:
        csv.writer(f).writerows([
            ["django_app", "test_type", "suite", "class", "test_name",
             "status", "duration_seconds", "test_file", "error_message",
             "execution_timestamp", "job_uid", "job_name", "run_id", "run_number",
             "commit_sha", "ref_name", "target_branch", "source_branch",
             "pr_title", "workflow_name", "source_file"]
        ] + rows)

    print(f"Wrote {output_csv}, rows: {len(rows)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/convert_junit_to_csv.py <input_xml> <output_csv> [component] [test_type] [run_id] [run_number] [sha] [branch] [workflow]")
        sys.exit(1)
    convert_xml_to_csv(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else '', sys.argv[4] if len(sys.argv)>4 else '')
