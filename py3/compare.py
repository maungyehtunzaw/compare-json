# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
compare_json_keys.py

A script to compare the keys and values of two JSON files (including nested keys) and export the differences.
"""
import json
import argparse
import os
import sys
from typing import Any, Dict, Tuple


def flatten_json(data: Any, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested JSON into a flat dict with dot-separated keys.
    :param data: JSON object (dict or list)
    :param parent_key: prefix for key
    :param sep: separator between keys
    :return: flat dict mapping flattened key paths to values
    """
    items: Dict[str, Any] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_json(v, new_key, sep=sep))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(flatten_json(v, new_key, sep=sep))
    else:
        items[parent_key] = data
    return items


def compare_json(
    file1: str,
    file2: str
) -> Dict[str, Any]:
    """
    Compare two JSON files by keys and values.
    Returns a dict with:
      - only_in_<file1>
      - only_in_<file2>
      - differing_values: list of {key, value1, value2}
      - in_both: list of keys with identical values
    """
    # Validate files exist
    for path in (file1, file2):
        if not os.path.isfile(path):
            print(f"Error: cannot find JSON file at '{path}'", file=sys.stderr)
            sys.exit(1)

    # Load JSON data
    with open(file1, 'r', encoding='utf-8') as f:
        data1 = json.load(f)
    with open(file2, 'r', encoding='utf-8') as f:
        data2 = json.load(f)

    # Flatten nested structure
    flat1 = flatten_json(data1)
    flat2 = flatten_json(data2)

    keys1 = set(flat1.keys())
    keys2 = set(flat2.keys())

    only1 = sorted(keys1 - keys2)
    only2 = sorted(keys2 - keys1)

    in_both = []
    diffs = []
    for key in sorted(keys1 & keys2):
        if flat1[key] != flat2[key]:
            diffs.append({
                'key': key,
                os.path.basename(file1): flat1[key],
                os.path.basename(file2): flat2[key]
            })
        else:
            in_both.append(key)

    return {
        f'only_in_{os.path.basename(file1)}': only1,
        f'only_in_{os.path.basename(file2)}': only2,
        'differing_values': diffs,
        'in_both_identical': in_both
    }


def main():
    parser = argparse.ArgumentParser(
        description='Compare JSON keys and values of two files and export the differences.'
    )
    parser.add_argument('file1', help='First JSON file path')
    parser.add_argument('file2', help='Second JSON file path')
    parser.add_argument('-o', '--output', default='differences.json',
                        help='Output file for differences (JSON format)')

    args = parser.parse_args()

    result = compare_json(args.file1, args.file2)

    # Write result
    with open(args.output, 'w', encoding='utf-8') as out:
        json.dump(result, out, indent=2, ensure_ascii=False)

    print(f"Differences (including value diffs) written to {args.output}")


if __name__ == '__main__':
    main()
    ##py compare.py ../data/en.json ../data/zh.json
