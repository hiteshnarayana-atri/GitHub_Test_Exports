import xml.etree.ElementTree as ET
import glob
import csv
import json
import os
import sys
from datetime import datetime, timezone

def _status(tc):
    return ('failed' if tc.find('failure') is not None else
            'error'  if tc.find('error')   is not None else
            'skipped'if tc.find('skipped') is not None else 'passed')

def main(xml_pattern, output_dir):
    files = glob.glob(xml_pattern, recursive=True)
    if not files:
        print(f"Error: No XML files found matching {xml_pattern}")
        sys.exit(1)

    # --- GitHub metadata (optional) ---
    run_id      = sys.argv[3] if len(sys.argv) > 3 else ''
    run_number  = sys.argv[4] if len(sys.argv) > 4 else ''
    commit_sha  = sys.argv[5] if len(sys.argv) > 5 else ''
    branch      = sys.argv[6] if len(sys.argv) > 6 else ''
    workflow    = sys.argv[7] if len(sys.argv) > 7 else ''
    now_iso     = datetime.now(timezone.utc).isoformat(timespec="seconds")

    os.makedirs(output_dir, exist_ok=True)
    rows = []

    for f in files:
        try:
            root = ET.parse(f).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {f}: {e}")
            continue

        for suite in root.iter('testsuite'):
            suite_name = suite.attrib.get('name','')
            for tc in suite.iter('testcase'):
                msg = ''
                for tag in ('failure', 'error', 'skipped'):
                    node = tc.find(tag)
                    if node is not None:
                        msg = (node.attrib.get('message') or '').strip()
                        break

                # derive component & test_type from path (lightweight heuristic)
                component = 'notifications' if '/notifications/' in f else ('base' if '/base/' in f else 'unknown')
                test_type = 'cypress' if '/frontend/' in f else 'pytest'

                rows.append({
                    "component": component,
                    "test_type": test_type,
                    "suite": suite_name,
                    "class": tc.attrib.get('classname',''),
                    "test_name": tc.attrib.get('name',''),
                    "status": _status(tc),
                    "duration_seconds": tc.attrib.get('time','0'),
                    "file": tc.attrib.get('file',''),
                    "message": msg,
                    "run_id": run_id,
                    "run_number": run_number,
                    "commit_sha": commit_sha,
                    "branch": branch,
                    "workflow_name": workflow,
                    "timestamp": now_iso,
                    "source": f,
                })

    if not rows:
        print("Error: No test cases found")
        sys.exit(1)

    out_csv  = os.path.join(output_dir, 'all_tests.csv')
    out_json = os.path.join(output_dir, 'all_tests.json')

    fieldnames = [
        "component","test_type","suite","class","test_name",
        "status","duration_seconds","file","message",
        "run_id","run_number","commit_sha","branch","workflow_name",
        "timestamp","source"
    ]
    with open(out_csv, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

    with open(out_json, 'w') as jh:
        json.dump(rows, jh, indent=2)

    print(f"Wrote {out_csv} and {out_json}, count: {len(rows)})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/merge_junit_tests.py <xml_pattern> <output_dir> [run_id] [run_number] [sha] [branch] [workflow]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
