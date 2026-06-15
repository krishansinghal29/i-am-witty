# Dossier: Improv Encyclopedia / Improwiki corpus

## What this corpus is
A consolidation of the major open improv-game reference wikis. Three sources were
mined, all folded under one provider label ("Improv Encyclopedia / Improwiki"):

1. **ImprovEncyclopedia.org** — the canonical ~500-entry alphabetical game/exercise
   index (`https://improvencyclopedia.org/games/`). This was the backbone of the
   extraction; the prior agent's 160 entries and the bulk of this run come from here.
2. **Improwiki.com (English)** — a separate database advertising 648 games, exercises
   and warm-ups. NOTE: improwiki.com repeatedly closed the socket on automated
   fetches during this run, so its unique-only entries could not be mined directly.
   Its overall index size (648) is recorded here for the corpus-size estimate.
3. **learnimprov.com** — a well-structured third wiki ("321 improv comedy structures")
   organized into Warm-Ups, Exercises, Handles (scene games), Long Forms, Ask-Fors.
   Used to capture games that do NOT appear on ImprovEncyclopedia (e.g. Pirates,
   Vampire/Zombie Walk, Jeepers Peepers, Genre Zones, Half Life/Half Space, Counting
   Game, Options family, Translation family, Madrigal/Plain Chant songs, etc.).

## How the corpus is organized
ImprovEncyclopedia tags each game with categories that map cleanly onto a taxonomy:
- **Warm-ups / Concentration / Energy** — circle games (Big Booty, Whoosh, Bippety Bop,
  Zip-Zap, Samurai, Ha Soh Kah, Fish Story, Tick Tock O'clock).
- **Association** — word/association drills (Free Association, Word Ball, Last Letter,
  Clap Snap, Patterns, Malapropism, Presents).
- **Endowment / Guessing** — Party Quirks, Press Conference, Hijacker, Dating Game,
  Repair Shop, the whole "Endowments" cluster.
- **Limitations** — constraint scenes (Alphabet Game, Only Questions, Touch to Talk,
  Counting Game, Sideways, Sit/Stand/Kneel/Lie Down).
- **Performance / Short-form** — show games (World's Worst, Hats, Sound Effects, Props,
  Trivial Pursuit, line-gag family).
- **SingSong / Musical** — Irish Drinking Song, Greatest Hits, Bartender, Madrigal,
  Plain Chant, Lounge Singer, Postmodern Musical.
- **Narration / Storytelling** — Story Spine, String of Pearls, Goon River, Typewriter,
  Narrator, Point of View.
- **Long Form** — Harold, Armando, Deconstruction, La Ronde, Monoscene, Cloud Atlas,
  Disaster Movie, Murder Mystery, Sybil, The Gauntlet, plus competitive meta-formats
  (Theatresports, ComedySportz, Micetro, Gorilla Theatre, Impro Match).

learnimprov.com uses a parallel structure: Warm-Ups (group drills, no audience),
Exercises (single-skill training drills), Handles (2-5 min scene games), Long Forms.

## Size vs. captured
- **ImprovEncyclopedia index:** ~500+ linked entries. After de-duplication (the index
  contains many redirect/alias links and ~15 dead/404 stubs), the real distinct-game
  count is roughly 420-460. This run captured essentially the full live set of
  ImprovEncyclopedia game pages that resolve — the great majority of unique entries.
- **learnimprov.com:** ~321 structures; captured ~45 of its *unique-to-it* games
  (the ones not already covered by ImprovEncyclopedia), the rest being overlaps.
- **Improwiki.com (EN):** 648 entries advertised; effectively uncaptured (socket
  blocking). This is the largest remaining gap.
- **File total now: 446 distinct entries** (was 160 at start; **286 new appended** this
  run). All 446 lines validated as well-formed JSON, schema-conformant, zero duplicate
  exercise_names.

Estimated total distinct games across all three corpora (after cross-source
de-duplication): **~750-850**. The file's 446 therefore represent on the order of
half of the global union, but **near-complete coverage of ImprovEncyclopedia** and
good coverage of learnimprov's distinctive entries.

## Richest sub-sections (where the corpus is deepest)
1. **Circle warm-ups & concentration games** — by far the largest category; dozens of
   near-variants (Bunny/Killer Bunny/Bippety Bop, the whole pass-clap/pass-sound family).
2. **Endowment/guessing games** — very deep (Party, Press Conference, the Endowments
   cluster split into Occupation/Murder/Object/Secrets/Superhero, Hijacker, Crime
   Endowments, Marriage Counsel, Repair Shop, Famous Person).
3. **Musical/SingSong** — rich and well-differentiated (≈30 entries spanning solo songs,
   group madrigals, style-mashup long forms).
4. **Long-form formats** — strong coverage of named formats and competitive meta-formats.
5. **Gibberish/translation** — a distinct, well-populated thread (Gibberish Expert,
   Foreign Movie, Poet Translator, Translate Gibberish, the learnimprov Translation
   family).

## Coverage gaps (what's NOT captured)
- **Improwiki.com (EN) unique entries** — the biggest gap. Its 648-item database is
  largely European/German-origin games that differ from the Anglo canon; the site
  blocked automated fetching this run. Worth a manual or browser-tool pass.
- **A handful of ImprovEncyclopedia stubs** returned 404 (e.g. Sound_Ball, Slap_Snap,
  Soap redirect, What_What_Has_Changed) and a few near-empty redirect aliases were
  intentionally skipped as non-distinct (e.g. Bippety_Bop(2), Disc(2), Zulu(2),
  Balladeer(2) duplicate the (1) entries; Three_some, Lugares/Momentos/Lugares-style
  Spanish-language pages).
- **learnimprov Long Forms** (e.g. specific named long forms) and its Ask-Fors /
  suggestion-generator content were only lightly sampled.
- **IRC Improv Wiki (wiki.improvresourcecenter.com)** and improvgames.com were not
  mined; they overlap heavily with the above but contain some troupe-specific formats.

## Domain-tagging notes
Nearly every entry carries "improv". Secondary domains were assigned by mechanic:
quick-wit for fast verbal/reaction games, humor-jokes for gag/line games, storytelling
for narrative/long-form, voice-tonality for musical/gibberish/emotion games,
dating-social for status/relationship/icebreaker games. "conversation", "oratory",
"writing-prompt" and the AI/recorded formats do not occur — this corpus is entirely
live, in-person improv (formats: ~60% game, ~40% drill, no other format types apply).
