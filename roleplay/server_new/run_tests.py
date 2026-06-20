#!/usr/bin/env python3
"""Dependency-free test runner for the simulator. [no pytest needed]

The tests are plain functions using `assert` + `asyncio.run`, so they don't need
pytest. Run from this directory with the shared backend venv:

    ../design/backend/.venv/bin/python run_tests.py
"""
from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))   # make `roleplay_sim` importable without an install


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"t_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    passed = 0
    failures: list[tuple[str, str, str]] = []
    for f in sorted((ROOT / "tests").rglob("test_*.py")):
        mod = _load(f)
        for name in dir(mod):
            fn = getattr(mod, name)
            if name.startswith("test_") and callable(fn):
                try:
                    fn()
                    passed += 1
                except Exception:
                    failures.append((f.name, name, traceback.format_exc()))
    for fname, name, tb in failures:
        print(f"FAIL {fname}::{name}\n{tb}")
    print(f"\n{passed} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
