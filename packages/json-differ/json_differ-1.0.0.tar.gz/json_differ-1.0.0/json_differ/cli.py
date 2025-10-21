#!/usr/bin/env python3
import argparse
import json
import sys
from .core import json_diff, to_pretty_json

def main():
    parser = argparse.ArgumentParser(prog='json-differ',
                                     description='Compare two JSON files and show a structured diff.')
    parser.add_argument('file1', help='Path to first JSON file')
    parser.add_argument('file2', help='Path to second JSON file')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty-print JSON output')
    parser.add_argument('--compact', '-c', action='store_true', help='Print compact one-line JSON')
    args = parser.parse_args()

    try:
        with open(args.file1, 'r', encoding='utf-8') as f1:
            json1 = json.load(f1)
    except Exception as e:
        print(f"Failed to load {args.file1}: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(args.file2, 'r', encoding='utf-8') as f2:
            json2 = json.load(f2)
    except Exception as e:
        print(f"Failed to load {args.file2}: {e}", file=sys.stderr)
        sys.exit(2)

    result = json_diff(json1, json2)
    if args.compact:
        print(json.dumps(result, separators=(',', ':'), ensure_ascii=False))
    else:
        print(to_pretty_json(result))

if __name__ == '__main__':
    main()
