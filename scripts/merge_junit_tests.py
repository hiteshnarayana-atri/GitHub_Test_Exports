import xml.etree.ElementTree as ET
import glob
import csv
import json
import os
import sys

def status(tc):
    return ('failed' if tc.find('failure') is not None else
            'error'  if tc.find('error')   is not None else
            'skipped'if tc.find('skipped') is not None else 'passed')

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
            
        for suite in root.iter('testsuite'):
            component = 'Frontend' if '/frontend/' in f else ('Backend' if '/backend/' in f else 'unknown')
            for tc in suite.iter('testcase'):
                rows.append({
                    "component": component,
                    "source": f,
                    "suite": suite.attrib.get('name',''),
                    "class": tc.attrib.get('classname',''),
                    "test_name": tc.attrib.get('name',''),
                    "status": status(tc),
                    "duration_seconds": tc.attrib.get('time','0'),
                    "file": tc.attrib.get('file',''),
                })

    if not rows:
        print("Error: No test cases found")
        sys.exit(1)

    # CSV
    out_csv = os.path.join(output_dir, 'all_tests.csv')
    with open(out_csv, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=["component","source","suite","class","test_name","status","duration_seconds","file"])
        w.writeheader()
        w.writerows(rows)

    # JSON
    out_json = os.path.join(output_dir, 'all_tests.json')
    with open(out_json, 'w') as jh:
        json.dump(rows, jh, indent=2)
    
    print(f"Wrote {out_csv} and {out_json}, count: {len(rows)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/merge_all_tests.py <xml_pattern> <output_dir>")
        print("Example: python scripts/merge_all_tests.py 'collected/**/*.xml' collected/out")
        sys.exit(1)
    
    xml_pattern = sys.argv[1]
    output_dir = sys.argv[2]
    main(xml_pattern, output_dir)