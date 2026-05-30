"""
One-time script to generate English adjective and adverb word lists from WordNet.
Output:
    app/data/adjectives.txt — one adjective per line, sorted alphabetically.
    app/data/adverbs.txt    — one adverb per line, sorted alphabetically.

Usage:
    python scripts/download_adjectives.py
"""

import os
import sys


def main():
    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        print("NLTK not available. Run: pip install nltk", file=sys.stderr)
        sys.exit(1)

    try:
        wn.all_synsets()
    except LookupError:
        print("WordNet data not found. Run: python -c \"import nltk; nltk.download('wordnet')\"", file=sys.stderr)
        sys.exit(1)

    adjectives = set()
    for pos in [wn.ADJ, wn.ADJ_SAT]:
        for synset in wn.all_synsets(pos=pos):
            for lemma in synset.lemmas():
                word = lemma.name().lower()
                if word.isalpha():
                    adjectives.add(word)

    adjectives = sorted(adjectives)

    output_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "adjectives.txt")
    output_path = os.path.abspath(output_path)

    with open(output_path, "w") as f:
        f.write("\n".join(adjectives))

    print(f"Saved {len(adjectives)} adjectives to {output_path}")

    adverbs = set()
    for synset in wn.all_synsets(pos=wn.ADV):
        for lemma in synset.lemmas():
            word = lemma.name().lower()
            if word.isalpha():
                adverbs.add(word)

    adverbs = sorted(adverbs)

    adverbs_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "adverbs.txt")
    adverbs_path = os.path.abspath(adverbs_path)

    with open(adverbs_path, "w") as f:
        f.write("\n".join(adverbs))

    print(f"Saved {len(adverbs)} adverbs to {adverbs_path}")


if __name__ == "__main__":
    main()
