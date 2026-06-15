#!/usr/bin/env python3
"""Group high+medium worth_deep_dive providers into batches for step 2b.

Groups by coarse category (so each agent uses the right research method), splits
each category into batches of ~8-9, writes each batch as a JSONL subset, and prints
a manifest. Step-2b agents read their batch file directly.
"""
import json, os, math
from collections import defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..")
PROV = os.path.join(BASE, "output", "step2", "providers.jsonl")
BATCHDIR = os.path.join(BASE, "output", "step2", "batches")
os.makedirs(BATCHDIR, exist_ok=True)

# coarse category -> which provider types fall in it, and the per-batch size
CATEGORY = {
    "apps":      {"types": {"mobile-app", "web-app", "ai-tool"}, "size": 8},
    "courses":   {"types": {"online-course", "book-program"},    "size": 8},
    "schools":   {"types": {"school"},                            "size": 6},
    "coaches":   {"types": {"coach-program", "youtube-channel"},  "size": 9},
    "community": {"types": {"community", "podcast"},              "size": 6},
}

provs = [json.loads(l) for l in open(PROV)]
hm = [p for p in provs if p.get("worth_deep_dive") in ("high", "medium")]

# bucket by category
buckets = defaultdict(list)
typed = {t: cat for cat, spec in CATEGORY.items() for t in spec["types"]}
for p in hm:
    cat = typed.get(p.get("type"), "community")  # fallback
    buckets[cat].append(p)

manifest = []
for cat, items in buckets.items():
    # high first within a category
    items.sort(key=lambda p: 0 if p.get("worth_deep_dive") == "high" else 1)
    size = CATEGORY[cat]["size"]
    nb = max(1, math.ceil(len(items) / size))
    # even split
    per = math.ceil(len(items) / nb)
    for i in range(nb):
        chunk = items[i*per:(i+1)*per]
        if not chunk:
            continue
        name = f"{cat}-{i+1}" if nb > 1 else cat
        path = os.path.join(BATCHDIR, f"{name}.jsonl")
        with open(path, "w") as f:
            for p in chunk:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        manifest.append((name, len(chunk), [p["name"] for p in chunk]))

manifest.sort()
print(f"{len(hm)} providers -> {len(manifest)} batches\n")
for name, n, names in manifest:
    print(f"  {name:<14} ({n}): {', '.join(names)}")

# write manifest json for the launcher
with open(os.path.join(BATCHDIR, "_manifest.json"), "w") as f:
    json.dump([{"batch": n, "count": c, "providers": p} for n, c, p in manifest],
              f, indent=2, ensure_ascii=False)
print(f"\nmanifest -> {os.path.relpath(os.path.join(BATCHDIR, '_manifest.json'), BASE)}")
