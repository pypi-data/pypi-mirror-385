"""Demo: load a graph_results JSON and run codegen.run_poc_from_results.

Usage: python -m nndesigner.tools.demo_codegen_results
"""
import json
import os
from pathlib import Path

from nndesigner.tools import codegen


def main():
    root = Path(__file__).resolve().parents[2]
    example = root / 'examples' / 'graph_results_example.json'
    if not example.exists():
        print('example graph_results not found:', example)
        return
    with open(example, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('Loaded example graph_results; generating and running PoC...')
    ok = codegen.run_poc_from_results(data)
    print('run_poc_from_results result:', ok)


if __name__ == '__main__':
    main()
