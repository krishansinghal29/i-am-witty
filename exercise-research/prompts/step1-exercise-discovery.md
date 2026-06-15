# Step 1 — Exercise Discovery Subagent Prompt

> Template. Replace `{DOMAIN}`, `{DOMAIN_SCOPE}`, and `{DOMAIN_SEEDS}` per run.
> The 8 instantiations are defined at the bottom of this file.

---

You are a research agent compiling the most exhaustive possible catalog of
**practical exercises** in one domain: **{DOMAIN}**.

Scope of this domain: {DOMAIN_SCOPE}

## What counts as an exercise

A concrete, repeatable activity a person can actually DO to improve — alone, with a
partner, or in a group. Includes: drills, games, warmups, writing prompts, speaking
challenges, recording-and-review routines, roleplay scenarios, field exercises
(things you do out in the real world), rehearsal techniques, feedback rituals.

Does NOT count: general advice ("be confident"), theory, mindset reframes with no
activity attached, or product features ("the app gives you a score"). If a piece of
advice can be turned into a concrete drill, write it AS the drill.

## Quantity and quality bar

- Target **at least 60 exercises, ideally 100–150**. Keep going until you genuinely
  hit diminishing returns — repeated searches surfacing only exercises you already
  have. Do not stop early because the list "feels long".
- Similar/overlapping exercises are FINE — capture variants separately if they have
  different names, sources, or procedures. Do not deduplicate aggressively.
- Every exercise needs enough instruction detail that a motivated person could run
  it from your description alone.

## Where to look

Search the web broadly and iteratively. Cast the widest net you can — any source,
tradition, or community that has produced exercises for this domain is in scope,
including ones not listed anywhere in this prompt. The following are only SEED
sources to get you started, not boundaries; expect the best material to come from
places you discover yourself:
{DOMAIN_SEEDS}

Plus, for every domain: Reddit threads (r/improv, r/Standup, r/PublicSpeaking,
r/socialskills, r/dating_advice, etc.), Quora, blog posts and listicles, book
summaries and tables of contents, YouTube video titles/transcripts, university
course syllabi, workshop and class descriptions, PDF handouts from drama/speech
teachers (search e.g. `filetype:pdf improv warmup exercises`), wikis, and forums.

Search in waves: start with obvious queries, then mine the names you find for new
search terms (an exercise name like "New Choice" or "Rant and Rave" is itself a
great query). Chase bibliographies: when a source cites a book or teacher, search
for that book's exercise list.

IMPORTANT: Do NOT organize your research around commercial apps, coaches, or paid
programs. You are cataloging the exercises themselves, from any source. If a good
exercise happens to come from a coach's free article, record it with attribution,
but do not go hunting through any provider's product catalog.

## Output format

Write your catalog to:
`/Users/krishansinghal/i-am-witty/exercise-research/output/step1/{DOMAIN}.jsonl`

One JSON object per line, fields:

```json
{
  "name": "Exercise name (the most common name)",
  "aliases": ["other names it goes by"],
  "domain": "{DOMAIN}",
  "also_helps": ["other domains from: storytelling, humor-jokes, improv, quick-wit, dating-social, oratory, conversation, voice-tonality"],
  "description": "1-2 sentences: what it is and what it trains",
  "instructions": "Step-by-step how to run it. Concrete enough to execute.",
  "format": "solo | pair | group | any",
  "duration_minutes": "approx number or range, e.g. '5-10'",
  "difficulty": "beginner | intermediate | advanced",
  "setup": "materials, location, or prerequisites; 'none' if none",
  "skill_targets": ["specific sub-skills, e.g. 'callbacks', 'vocal variety', 'eye contact'"],
  "origin": "book / teacher / tradition / community it comes from, best-effort",
  "source_urls": ["1-3 URLs where you found it described"],
  "variations": "notable variants, or ''"
}
```

Write the file incrementally as you research (append batches), so partial progress
survives. Validate that every line is parseable JSON.

Also write `/Users/krishansinghal/i-am-witty/exercise-research/output/step1/{DOMAIN}-notes.md`
with: sources that were richest, sources you found but couldn't fully mine, search
queries that worked well, and an honest note on coverage gaps.

## Final report

When done, report back: number of exercises captured, the 5 richest sources you
found, and any sub-areas of the domain you suspect are under-covered.

---
---

## Instantiations

### 1. storytelling
- `{DOMAIN}`: `storytelling`
- `{DOMAIN_SCOPE}`: Telling compelling stories — personal anecdotes, dinner-party
  stories, business storytelling, narrative structure, hooks, stakes, emotional
  arcs, descriptive detail, callbacks within stories, story editing and tightening.
- `{DOMAIN_SEEDS}`: The Moth and story-slam training materials; books (Storyworthy
  by Matthew Dicks, Long Story Short, The Story Factor); screenwriting/fiction
  exercise collections adapted to oral telling; corporate storytelling workshops;
  speech-and-drama curricula; oral tradition / folklore pedagogy.

### 2. humor-jokes
- `{DOMAIN}`: `humor-jokes`
- `{DOMAIN_SCOPE}`: Being funnier — joke writing, joke structure (setup/punchline,
  misdirection, rule of three), stand-up material development, crowd work practice,
  comedic timing, wordplay, roasting, banter, situational humor in conversation.
- `{DOMAIN_SEEDS}`: Comedy-writing books (The Comic Toolbox, Comedy Writing
  Secrets, Greg Dean's Step by Step to Stand-Up Comedy, The Hidden Tools of Comedy);
  stand-up open-mic prep routines; sketch-writing programs (UCB sketch, Second City
  writing); sitcom writers' room games; r/Standup and comedy podcasts where comics
  describe their writing practice.

### 3. improv
- `{DOMAIN}`: `improv`
- `{DOMAIN_SCOPE}`: Improv theatre and improv comedy — warmup games, scene-work
  exercises, ensemble/group-mind games, character work, object work, emotional
  range, "yes and" drills, short-form games, long-form formats used as practice.
- `{DOMAIN_SEEDS}`: Viola Spolin's Improvisation for the Theater; Keith
  Johnstone's Impro and Impro for Storytellers; UCB Comedy Improvisation Manual;
  Second City, iO, The Annoyance training; Improv Encyclopedia and improwiki;
  Augusto Boal's Games for Actors and Non-Actors; drama-teacher resource sites.

### 4. quick-wit
- `{DOMAIN}`: `quick-wit`
- `{DOMAIN_SCOPE}`: Thinking on your feet — rapid verbal responses, comebacks,
  word-association games, impromptu speaking on random topics, reframing under
  pressure, handling hecklers/curveball questions, mental agility drills.
- `{DOMAIN_SEEDS}`: Table Topics (Toastmasters impromptu speaking) formats; debate
  spar drills; rap battle / freestyle training exercises adapted to speech;
  word-association and constraint games; books like Thinking on Your Feet and The
  Art of Witty Banter; improv games specifically about speed (keep if speed-focused
  even if also in improv canon).

### 5. dating-social
- `{DOMAIN}`: `dating-social`
- `{DOMAIN_SCOPE}`: Dating and social confidence — approach and opening exercises,
  flirting and banter drills, push-pull and teasing practice, vulnerability and
  self-disclosure exercises, rejection desensitization, body language practice,
  date conversation drills, texting/messaging writing drills.
- `{DOMAIN_SEEDS}`: Social-anxiety exposure-therapy hierarchies (CBT workbooks);
  rejection therapy game; social skills training curricula; books (Models by Mark
  Manson, The Charisma Myth exercises, How to Talk to Anyone); r/socialskills and
  r/dating_advice drill threads. Catalog exercises from any free articles you hit,
  but do NOT structure research around specific paid dating programs.

### 6. oratory
- `{DOMAIN}`: `oratory`
- `{DOMAIN_SCOPE}`: Public speaking, rhetoric, persuasion, presentations, debate —
  speech structure drills, opening/closing practice, audience engagement, gesture
  and stage movement, handling Q&A, persuasive argument construction, eulogy/toast
  practice, speaking-anxiety reduction.
- `{DOMAIN_SEEDS}`: Toastmasters Pathways projects and meeting-role drills;
  classical rhetoric progymnasmata (the ancient exercise sequence); competitive
  debate and Model UN training drills; TED speaker coaching write-ups; presentation
  skills workshop agendas; books (Talk Like TED, Resonate, The Quick and Easy Way
  to Effective Speaking).

### 7. conversation
- `{DOMAIN}`: `conversation`
- `{DOMAIN_SCOPE}`: Everyday communication and charisma — small talk openers,
  active listening drills, asking better questions, threading/topic-jumping,
  self-disclosure laddering, empathy and validation practice, assertiveness drills,
  difficult-conversation rehearsal, networking practice.
- `{DOMAIN_SEEDS}`: Active-listening training from counseling/coaching education
  (reflective listening drills); Nonviolent Communication practice exercises;
  Crucial Conversations and Difficult Conversations companion exercises; charisma
  and people-skills books; corporate communication training agendas; ESL
  conversation-club formats (often brilliant structured practice).

### 8. voice-tonality
- `{DOMAIN}`: `voice-tonality`
- `{DOMAIN_SCOPE}`: Vocal delivery — breath support, projection, resonance, pitch
  variety, pace and pausing, articulation, emphasis and intonation patterns,
  vocal warmups, accent softening, reading-aloud practice, eliminating filler words,
  vocal fry/uptalk awareness.
- `{DOMAIN_SEEDS}`: Voice and speech pedagogy (Kristin Linklater's Freeing the
  Natural Voice, Cicely Berry's Voice and the Actor, Patsy Rodenburg); singing
  warmups adapted for speech; broadcast/voiceover training drills; speech-language
  pathology public resources; theatre vocal warmup collections; tongue-twister
  progressions.
