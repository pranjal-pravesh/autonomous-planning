#!/usr/bin/env python3
"""
Run all configured experiments sequentially and collate high-level results.
"""

import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

def run(cmd: list[str]) -> int:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.call(cmd)

def main():
    # Ensure venv python is used if active
    python = sys.executable

    # Scaling analysis
    scaling = os.path.join(ROOT, 'scaling', 'scaling_analysis.py')
    if os.path.exists(scaling):
        rc = run([python, scaling])
        if rc != 0:
            print("[warn] Scaling analysis returned non-zero exit code")

    # Heuristic comparison
    heur = os.path.join(ROOT, 'heuristics', 'heuristic_comparison.py')
    if os.path.exists(heur):
        rc = run([python, heur])
        if rc != 0:
            print("[warn] Heuristic comparison returned non-zero exit code")

    print("\n✅ All experiments attempted. Check experiments/*/results for outputs.")

if __name__ == '__main__':
    main()


