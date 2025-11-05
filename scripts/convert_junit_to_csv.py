import xml.etree.ElementTree as ET
import csv
import os
import sys
import glob

def get_test_status(testcase):
    if testcase.find('failure') is not None:
        return 'failed'
    elif testcase.find('error') is not None:
        return 'error'
    elif testcase.find('skipped') is not None:
        return 'skipped'
    return 'passed'

def convert_xml_to_csv(xml_path, output_csv, component='', suite=''):
    if '*' in xml_path:
        xml_files = glob.glob(xml_path, recursive=True)
    else:
        xml_files = [xml_path] if os.path.exists(xml_path) else []

    if not xml_files:
        print(f"Warning: No XML files found at {xml_path}")
        xml_files = []

    rows = []
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for test_suite in root.iter('testsuite'):
                current_suite = test_suite.attrib.get('name', suite or component)
                
                for testcase in test_suite.iter('testcase'):
                    rows.append([
                        component,
                        current_suite,
                        testcase.attrib.get('classname', ''),
                        testcase.attrib.get('name', ''),
                        get_test_status(testcase),
                        testcase.attrib.get('time', '0'),
                        testcase.attrib.get('file', ''),
                    ])
        except Exception as e:
            print(f"Warning: Failed to parse {xml_file}: {e}")
            continue
    
    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["component", "suite", "class", "test_name", "status", "duration_seconds", "file"])
        writer.writerows(rows)
    print(f"Wrote {output_csv}, rows: {len(rows)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/convert_junit_to_csv.py <input_xml> <output_csv> [component] [suite]")
        sys.exit(1)
    xml_path = sys.argv[1]
    output_csv = sys.argv[2]
    component = sys.argv[3] if len(sys.argv) > 3 else ''
    suite = sys.argv[4] if len(sys.argv) > 4 else ''
    convert_xml_to_csv(xml_path, output_csv, component, suite)