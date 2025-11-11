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

def _msg(tc):
    for tag in ('failure','error'):
        el = tc.find(tag)
        if el is not None:
            m = (el.attrib.get('message') or '').strip()
            if not m:
                m = (el.text or '').strip().replace('\n',' ')
            return m[:200]
    return ''

def _files(pattern):
    if any(ch in pattern for ch in '*?['):
        return glob.glob(pattern, recursive=True)
    return [pattern] if os.path.exists(pattern) else []

def convert_xml_to_csv(xml_pattern, output_csv, component='', test_type='',
                       run_id='', run_number='', commit_sha='', branch='', workflow_name=''):
    files = _files(xml_pattern)
    rows = []
    for f in files:
        try:
            root = ET.parse(f).getroot()
        except Exception as e:
            print(f"Warning: Failed to parse {f}: {e}")
            continue
        default_ts = root.attrib.get('timestamp') or datetime.now(timezone.utc).isoformat()
        for suite in root.iter('testsuite'):
            suite_name = suite.attrib.get('name', component or test_type)
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
                    "run_id": run_id,
                    "run_number": run_number,
                    "commit_sha": commit_sha,
                    "branch": branch,
                    "workflow_name": workflow_name,
                    "timestamp": ts,
                    "source": f,
                })
    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    cols = ["component","test_type","suite","class","test_name","status","duration_seconds",
            "file","message","run_id","run_number","commit_sha","branch","workflow_name",
            "timestamp","source"]
    with open(output_csv, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {output_csv}, rows: {len(rows)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/convert_junit_to_csv.py <input_xml_or_glob> <output_csv> "
              "[component] [test_type] [run_id] [run_number] [sha] [branch] [workflow]")
        sys.exit(1)
    xml_path   = sys.argv[1]
    output_csv = sys.argv[2]
    component  = sys.argv[3] if len(sys.argv) > 3 else ''
    test_type  = sys.argv[4] if len(sys.argv) > 4 else ''
    run_id     = sys.argv[5] if len(sys.argv) > 5 else ''
    run_number = sys.argv[6] if len(sys.argv) > 6 else ''
    sha        = sys.argv[7] if len(sys.argv) > 7 else ''
    branch     = sys.argv[8] if len(sys.argv) > 8 else ''
    workflow   = sys.argv[9] if len(sys.argv) > 9 else ''
    convert_xml_to_csv(xml_path, output_csv, component, test_type, run_id, run_number, sha, branch, workflow)
