# Seed word lists

These plain-text word lists are the random *seeds* fed to the exercise
**generators** (see `app/prompts/generator_strategies.py`). A seed nudges the
LLM toward a specific, unexpected corner of the space so that successive
generations stay varied — left to its own devices, the model collapses to a
handful of stock scenarios.

Each file is one lowercase, single-token word per line, alphabetically sorted.

## Files

**Base lists** — raw WordNet vocabulary, one part of speech each:

| File | Words | Source |
|------|------:|--------|
| `verbs.txt` | 8,405 | WordNet `index.verb` |
| `adjectives.txt` | 17,873 | WordNet `index.adj` |
| `adverbs.txt` | 3,629 | WordNet `index.adv` |
| `nouns.txt` | 55,239 | WordNet `index.noun` |

**Derived lists** — a base list filtered/ranked by a psycholinguistic norm, for
higher-quality seeds. These are *precomputed, committed assets*, not runtime
artifacts — the generator reads them directly and does no filtering per request.

| File | Words | = base ∩ norm | Use |
|------|------:|--------------|-----|
| `nouns_concrete.txt` | 4,537 | nouns ∩ concreteness | everyday concrete objects (the `object` seed) |
| `verbs_common.txt` | 3,687 | verbs ∩ frequency | de-archaicized verbs |
| `adjectives_common.txt` | 4,477 | adjectives ∩ frequency | de-archaicized adjectives |
| `adverbs_common.txt` | 828 | adverbs ∩ frequency | de-archaicized adverbs |
| `emotive_words.txt` | 2,336 | (verbs∪adj∪nouns) ∩ arousal | emotionally charged seeds (e.g. the "big emotion" technique) |
| `vivid_words.txt` | 1,704 | all POS ∩ imageability | highly picturable words |

## Sources & recipes

### WordNet — base POS lists

Princeton WordNet, a lexical database for English. <https://wordnet.princeton.edu/>

Each list is WordNet's lemma column for that part of speech, with multi-word
entries (anything containing `_`) and punctuated/proper forms removed, then
lowercased and de-duplicated. This is why the vocabulary skews wide and includes
archaic/technical lemmas (`abacinate`, `abaxial`, …) — raw WordNet, not curated
everyday English. `verbs/adjectives/adverbs.txt` were inherited (WordNet 3.0
era); `nouns.txt` was extracted later from WordNet 3.1 (immaterial ~0.1% drift).

```
awk 'NF>2 && $1 !~ /^ /{print $1}' index.noun \
  | tr 'A-Z' 'a-z' | grep -E '^[a-z]+$' | LC_ALL=C sort -u > nouns.txt
```

### Brysbaert concreteness — `nouns_concrete.txt`

Raw WordNet nouns are full of proper nouns, Latin/taxonomic names, chemicals,
and abstractions — bad seeds for a *tiltable object*. Filtered to common,
physical things by joining against concreteness ratings.

- **Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014).** Concreteness ratings
  for 40 thousand generally known English word lemmas. *Behavior Research
  Methods.* The file also carries **SUBTLEX-US** frequency.
  Mirror: `github.com/ArtsEngine/concreteness` →
  `Concreteness_ratings_Brysbaert_et_al_BRM.txt`

Filter (single-word rows): in `nouns.txt` · `Conc.M >= 4.0` · `SUBTLEX >= 20`.

### SUBTLEX-US frequency — `*_common.txt`

Word frequencies from 51M words of US film/TV subtitles. Used purely to
*de-archaicize* the base lists (drop lemmas absent from real usage) while keeping
the full concrete↔abstract spread — so it suits adjectives/adverbs, where a
concreteness filter would wrongly delete useful abstract words.

- **Brysbaert, M., & New, B. (2009).** Moving beyond Kučera and Francis… *Behavior
  Research Methods.*
  Mirror: `github.com/AusterweilLab/snafu-py` → `frequency/subtlex-us.csv`
  (`word,freq_per_million`).

Filter: base list ∩ `freq_per_million >= 0.5` (≈ used ≥25× in the corpus; this
drops `abacinate`, `moil`, `guffaw` but keeps `fold`, `scrub`, `savor`, `groan`).

### Warriner VAD — `emotive_words.txt`

Valence / arousal / dominance ratings (1–9). High **arousal** marks emotionally
charged words, useful as seeds for the "big emotion" technique (a level-10
reaction to something mundane).

- **Warriner, A. B., Kuperman, V., & Brysbaert, M. (2013).** Norms of valence,
  arousal, and dominance for 13,915 English lemmas. *Behavior Research Methods.*
  Mirror: `github.com/JULIELab/XANEW` → `Ratings_Warriner_et_al.csv`
  (`A.Mean.Sum` = mean arousal).

Filter: word in verbs∪adjectives∪nouns · `arousal >= 5.0` · `freq_per_million >= 0.5`.

### MRC Psycholinguistic Database — `vivid_words.txt`

Imageability ratings (how easily a word evokes a mental image; 100–700).
Imageability's close cousin is concreteness, but MRC covers all parts of speech,
so this captures picturable *verbs* and *adjectives* (`swim`, `golden`), not just
nouns.

- **Coltheart, M. (1981).** The MRC Psycholinguistic Database. *Quarterly Journal
  of Experimental Psychology.*
  Mirror: `github.com/samzhang111/mrc-psycholinguistics` → `mrc2.dct`
  (fixed-width; imageability = `line[31:34]`, word = `line[51:].split('|')[0]`).

Filter: word in any base list · `imageability >= 500` (take max across entries).

## Licensing

- **WordNet** — permissive [WordNet License](https://wordnet.princeton.edu/license-and-commercial-use) (free use with attribution).
- **Brysbaert concreteness, SUBTLEX-US, Warriner VAD** — released for free academic & commercial use with citation (see papers above).
- **MRC Psycholinguistic Database** — freely available for research use.
