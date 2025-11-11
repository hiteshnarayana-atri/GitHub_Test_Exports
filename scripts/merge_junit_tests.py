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

def _msg(tc):
    for tag in ('failure','error'):
        el = tc.find(tag)
        if el is not None:
            m = (el.attrib.get('message') or '').strip()
            if not m:
                m = (el.text or '').strip().replace('\n',' ')
            return m[:200]
    return ''

def _infer_component_and_type(p):
    # collected/<app>/<backend|frontend>/... or reports/<app>/<backend|frontend>/...
    parts = p.split('/')
    for anchor in ('collected','reports'):
        if anchor in parts:
            i = parts.index(anchor)
            app = parts[i+1] if i+1 < len(parts) else 'unknown'
            part = parts[i+2] if i+2 < len(parts) else 'unknown'
            test_type = 'cypress' if part == 'frontend' else 'pytest' if part == 'backend' else 'unknown'
            return f"{app}", test_type
    return 'unknown', 'unknown'

def main(xml_pattern, output_dir):
    files = glob.glob(xml_pattern, recursive=True)
    if not files:
        print(f"Error: No XML files found matching {xml_pattern}")
        sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)

    rows = []
    for f in files:
        try:
            root = ET.parse(f).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {f}: {e}")
            continue
        default_ts = root.attrib.get('timestamp') or datetime.now(timezone.utc).isoformat()
        component, test_type = _infer_component_and_type(f)

        for suite in root.iter('testsuite'):
            suite_name = suite.attrib.get('name','')
            ts = suite.attrib.get('timestamp', default_ts)
            for tc in suite.iter('testcase'):
                rows.append({
                    "component": component,
                    "test_type": test_type,
                    "suite": suite_name,
                    "class": tc.attrib.get('classname',''),
                    "test_name": tc.attrib.get('name',''),
                    "status": _status(tc),
                    "duration_seconds": tc.attrib.get('time','0'),
                    "file": tc.attrib.get('file',''),
                    "message": _msg(tc),
                    "timestamp": ts,
                    "source": f,
                })

    cols = ["component","test_type","suite","class","test_name","status",
            "duration_seconds","file","message","timestamp","source"]

    out_csv = os.path.join(output_dir, 'all_tests.csv')
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    out_json = os.path.join(output_dir, 'all_tests.json')
    with open(out_json, 'w', encoding='utf-8') as jh:
        json.dump(rows, jh, indent=2)

    print(f"Wrote {out_csv} and {out_json}, count: {len(rows)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/merge_junit_tests.py <xml_pattern> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
