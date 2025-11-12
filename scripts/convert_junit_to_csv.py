import xml.etree.ElementTree as ET
import csv
import os
import sys
import glob
from datetime import datetime, timezone

def _status(tc):
    return ('failed' if tc.find('failure') is not None else
            'error'  if tc.find('error')   is not None else
            'skipped'if tc.find('skipped') is not None else 'passed')

def convert_xml_to_csv(xml_path, output_csv, component='', test_type=''):
    xml_files = glob.glob(xml_path, recursive=True) if '*' in xml_path else ([xml_path] if os.path.exists(xml_path) else [])
    if not xml_files:
        print(f"Warning: No XML files found at {xml_path}")

    # --- GitHub metadata (optional) ---
    run_id      = sys.argv[5] if len(sys.argv) > 5 else ''
    run_number  = sys.argv[6] if len(sys.argv) > 6 else ''
    commit_sha  = sys.argv[7] if len(sys.argv) > 7 else ''
    branch      = sys.argv[8] if len(sys.argv) > 8 else ''
    workflow    = sys.argv[9] if len(sys.argv) > 9 else ''
    now_iso     = datetime.now(timezone.utc).isoformat(timespec="seconds")

    rows = []
    for xf in xml_files:
        try:
            root = ET.parse(xf).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {xf}: {e}")
            continue

        for suite in root.iter('testsuite'):
            suite_name = suite.attrib.get('name', component or '')
            for tc in suite.iter('testcase'):
                msg = ''
                for tag in ('failure', 'error', 'skipped'):
                    node = tc.find(tag)
                    if node is not None:
                        msg = (node.attrib.get('message') or '').strip()
                        break

                rows.append([
                    component,
                    test_type,
                    suite_name,
                    tc.attrib.get('classname',''),
                    tc.attrib.get('name',''),
                    _status(tc),
                    tc.attrib.get('time','0'),
                    tc.attrib.get('file',''),
                    msg,
                    run_id, run_number, commit_sha, branch, workflow,
                    now_iso,
                    xf,
                ])

    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([
            "component","test_type","suite","class","test_name",
            "status","duration_seconds","file","message",
            "run_id","run_number","commit_sha","branch","workflow_name",
            "timestamp","source"
        ])
        w.writerows(rows)
    print(f"Wrote {output_csv}, rows: {len(rows)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/convert_junit_to_csv.py <input_xml> <output_csv> [component] [test_type] [run_id] [run_number] [sha] [branch] [workflow]")
        sys.exit(1)
    convert_xml_to_csv(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else '', sys.argv[4] if len(sys.argv)>4 else '')
