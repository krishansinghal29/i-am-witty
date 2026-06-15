#!/usr/bin/env python3
"""Step 1b — merge the 8 domain JSONL files into one master catalog.

Collapses ONLY exact-name duplicates (case-insensitive, whitespace/punct-normalized),
merging their domain tags. Similar-but-distinct exercises are kept (per user).
Assigns stable IDs EX-0001..., processing domains in a fixed order.
"""
import json, glob, os, re, sys

STEP1 = os.path.join(os.path.dirname(__file__), "..", "output", "step1")
OUT = os.path.join(STEP1, "master-exercises.jsonl")

# Fixed order -> stable IDs
DOMAIN_ORDER = ["storytelling", "humor-jokes", "improv", "quick-wit",
                "dating-social", "oratory", "conversation", "voice-tonality"]

def norm(name):
    s = (name or "").strip().lower()
    s = s.strip('"\'')
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" .!?:;-")
    return s

def longer(a, b):
    a, b = a or "", b or ""
    return a if len(a) >= len(b) else b

def as_list(v):
    if v is None: return []
    if isinstance(v, list): return [x for x in v if x not in (None, "")]
    if isinstance(v, str): return [v] if v.strip() else []
    return [v]

records = {}      # normkey -> merged dict
order = []         # normkeys in first-seen order
collapsed = 0

for domain in DOMAIN_ORDER:
    path = os.path.join(STEP1, f"{domain}.jsonl")
    if not os.path.exists(path):
        print(f"WARN missing {path}", file=sys.stderr); continue
    for line in open(path):
        line = line.strip()
        if not line: continue
        ex = json.loads(line)
        key = norm(ex.get("name"))
        if not key:
            continue
        if key not in records:
            rec = {
                "name": ex.get("name", "").strip(),
                "aliases": as_list(ex.get("aliases")),
                "domains": [],
                "also_helps": [],
                "description": ex.get("description", ""),
                "instructions": ex.get("instructions", ""),
                "format": ex.get("format", ""),
                "duration_minutes": ex.get("duration_minutes", ""),
                "difficulty": ex.get("difficulty", ""),
                "setup": ex.get("setup", ""),
                "skill_targets": as_list(ex.get("skill_targets")),
                "origin": ex.get("origin", ""),
                "source_urls": as_list(ex.get("source_urls")),
                "variations": ex.get("variations", ""),
                "_src_files": [],
            }
            records[key] = rec
            order.append(key)
        else:
            collapsed += 1
            rec = records[key]
            # merge: keep the most detailed text, union the lists
            rec["description"] = longer(rec["description"], ex.get("description"))
            rec["instructions"] = longer(rec["instructions"], ex.get("instructions"))
            rec["variations"] = longer(rec["variations"], ex.get("variations"))
            for f in ("format", "duration_minutes", "difficulty", "setup", "origin"):
                if not rec[f] and ex.get(f):
                    rec[f] = ex[f]
            for f in ("aliases", "skill_targets", "source_urls"):
                for v in as_list(ex.get(f)):
                    if v not in rec[f]:
                        rec[f].append(v)
        rec = records[key]
        # domain from this file's `domain` field (fall back to filename)
        d = ex.get("domain") or domain
        if d not in rec["domains"]:
            rec["domains"].append(d)
        for ah in as_list(ex.get("also_helps")):
            if ah not in rec["also_helps"]:
                rec["also_helps"].append(ah)
        if domain not in rec["_src_files"]:
            rec["_src_files"].append(domain)

# write master
with open(OUT, "w") as out:
    for i, key in enumerate(order, 1):
        rec = records[key]
        rec_out = {"id": f"EX-{i:04d}", **{k: v for k, v in rec.items() if k != "_src_files"}}
        # also_helps shouldn't duplicate primary domains
        rec_out["also_helps"] = [a for a in rec_out["also_helps"] if a not in rec_out["domains"]]
        rec_out["n_source_domains"] = len(rec["_src_files"])
        out.write(json.dumps(rec_out, ensure_ascii=False) + "\n")

print(f"input rows read : {sum(1 for k in records for _ in [0]) + collapsed}")
print(f"unique exercises: {len(order)}")
print(f"collapsed dups  : {collapsed}")
print(f"written to      : {os.path.relpath(OUT)}")

# domain distribution in master
from collections import Counter
c = Counter()
multi = 0
for key in order:
    ds = records[key]["domains"]
    if len(ds) > 1: multi += 1
    for d in ds: c[d] += 1
print("\nper-domain tag counts (a multi-domain exercise counts in each):")
for d in DOMAIN_ORDER:
    print(f"  {d:<16}{c.get(d,0)}")
print(f"exercises tagged in >1 domain: {multi}")
