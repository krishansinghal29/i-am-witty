#!/usr/bin/env python3
"""Batch all app-type providers for step 2d metadata enrichment (~9 per batch)."""
import json, os, math

BASE = os.path.join(os.path.dirname(__file__), "..")
PROV = os.path.join(BASE, "output", "step2", "providers.jsonl")
BDIR = os.path.join(BASE, "output", "step2", "app-metadata", "batches")
os.makedirs(BDIR, exist_ok=True)

APP_TYPES = {"mobile-app", "web-app", "ai-tool"}
provs = [json.loads(l) for l in open(PROV)]
apps = [p for p in provs if p.get("type") in APP_TYPES]

size = 9
nb = max(1, math.ceil(len(apps) / size))
per = math.ceil(len(apps) / nb)
manifest = []
for i in range(nb):
    chunk = apps[i*per:(i+1)*per]
    if not chunk:
        continue
    name = f"meta-{i+1}"
    with open(os.path.join(BDIR, f"{name}.jsonl"), "w") as f:
        for p in chunk:
            f.write(json.dumps({"name": p["name"], "type": p["type"],
                                "url": p.get("url",""), "notes": p.get("notes","")},
                               ensure_ascii=False) + "\n")
    manifest.append((name, [p["name"] for p in chunk]))

print(f"{len(apps)} app-type providers -> {len(manifest)} batches\n")
for name, names in manifest:
    print(f"  {name} ({len(names)}): {', '.join(names)}")
