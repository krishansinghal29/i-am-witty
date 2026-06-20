"""Tunable magnitudes loaded from config/defaults.yaml. [P8]

The deterministic core imports `TUNING` and reads magnitudes from it, so balance
can be tuned in one place (and overridden) without editing logic. Falls back to
the dataclass defaults if the YAML is missing or partial.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

_PATH = Path(__file__).resolve().parent / "defaults.yaml"


@dataclass(frozen=True)
class Tuning:
    accrual_rate: float = 0.30
    comfort_accrual: float = 0.5
    at_risk_band: float = 1.0
    eighty_band: float = 1.5
    at_risk_comfort: float = 45.0
    lock_severity: float = 2.5
    base_engagement_drain: float = 1.0
    flaky_fraction: float = 0.7


def load_tuning() -> Tuning:
    try:
        import yaml
        raw = (yaml.safe_load(_PATH.read_text(encoding="utf-8")) or {}).get("tuning", {})
    except Exception:
        raw = {}
    known = {f.name for f in fields(Tuning)}
    overrides = {k: float(v) for k, v in raw.items() if k in known}
    return Tuning(**overrides)


TUNING = load_tuning()
