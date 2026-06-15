# Toastmasters Pathways — Corpus Dossier

## What the corpus is

Toastmasters International is the world's largest public-speaking practice
organization. Since ~2018 its core curriculum is the **Pathways Learning
Experience**, a structured, openly-documented set of speech-and-leadership
"projects." It replaced (but did not erase) the legacy **Competent Communication
(CC) manual** — the famous 10-speech sequence many clubs still reference. On top of
the project curriculum, every weekly club meeting runs a fixed set of **functionary
roles** (Table Topics, Grammarian, Ah-Counter, Timer, Evaluator, etc.) that are
themselves recurring, repeatable practice exercises.

This is a true open corpus: every project has an official one-page **Project
Description** (purpose + overview + deliverable), and the full catalog is published
in club resources and reprinted on dozens of district websites.

## How it's organized

**Pathways structure (3 layers):**

1. **11 Paths** — Dynamic Leadership, Engaging Humor, Motivational Strategies,
   Persuasive Influence, Presentation Mastery, Visionary Communication, Effective
   Coaching, Innovative Planning, Leadership Development, Strategic Relationships,
   Team Collaboration. (Six are "fully imported" into the current Base Camp; all 11
   share the same project pool.)
2. **5 Levels per path** (Level 1 Mastering Fundamentals → Level 5 Demonstrating
   Expertise). Level 1 is **identical across all paths** (Ice Breaker, Writing a
   Speech with Purpose, Intro to Vocal Variety & Body Language, Evaluation &
   Feedback). Higher levels mix a few path-specific **core/required** projects with
   member-chosen **electives** drawn from a shared pool.
3. **~66 distinct projects total** in the catalog: the 4 shared Level-1 cores, the
   path-signature cores (e.g. Negotiate the Best Outcome, Engage Your Audience with
   Humor, Develop Your Vision, Team Building), and a large shared elective pool
   (Connect with Storytelling, Create a Podcast, Persuasive Speaking, Moderate a
   Panel Discussion, etc.), plus required closers (Intro to Toastmasters Mentoring,
   Reflect on Your Path) and the Distinguished Toastmaster capstone.

Because the same project appears as a "core" in one path and an "elective" in
another, the right unit of extraction is the **distinct project**, not path×level
slots (which would balloon to ~150+ duplicated entries). That is how this file is
built.

**Two adjacent layers also captured:**
- **Classic Competent Communication manual** — the legacy 10-speech progression (CC1
  Ice Breaker → CC10 Inspire Your Audience). Many of these map onto Pathways
  equivalents but the manual is a distinct, still-used artifact, so the 10 are
  captured separately (prefixed `CC1`-`CC10`).
- **Recurring meeting roles** — Table Topics (the canonical impromptu drill),
  Topicsmaster, Grammarian, Ah-Counter, Timer, Speech Evaluator, General Evaluator,
  Toastmaster of the Day. These are not "projects" but are repeatable
  practice-by-doing exercises every member rotates through.

## What I captured vs. total size

- **83 exercises captured**, all `confirmed`:
  - **42 distinct Pathways projects** with what the member actually does (the
    practically-relevant, member-facing project pool — Level 1 cores, all path
    signature cores, and the high-value electives). This effectively covers the
    ~43-project target. A handful of pure-administrative items in the 66-item full
    catalog (e.g. Prepare to Mentor as a forms-only step) were included; a few
    near-duplicate evaluation variants were folded into their main project.
  - **1 Distinguished Toastmaster** capstone project.
  - **10 classic Competent Communication manual** projects (CC1-CC10).
  - **8 recurring meeting-role** exercises.
- **Total corpus size:** ~66 unique Pathways project descriptions in the official
  catalog + 10 CC manual speeches + ~8-12 standard meeting roles ≈ **85-90 distinct
  named exercises**. There are also legacy "Advanced Communication Series" manuals
  (Storytelling, Humorously Speaking, Interpretive Reading, Speaking to Inform,
  Persuasive Speaking, etc. — ~15 manuals × ~5 projects) that are out of scope here
  but represent a large additional vein if deeper oratory/storytelling coverage is
  wanted later.

## Evidence quality

High. The richest source is the official **Pathways paths-and-projects catalog
PDF** (toastmasters60 mirror of Toastmasters International's own project-description
sheets), which gave verbatim Purpose + Overview + deliverable (speech length) for
every project. The CC manual 10-speech objectives and the meeting-role duties come
from official Toastmasters pages and club mirrors. Everything is marked `confirmed`;
nothing relied on inference. The only minor lossiness is that the toastmasters.org
"Navigator" and Base Camp pages are JS-gated / member-gated, so descriptions were
sourced from the public catalog PDF and district mirrors instead — but these
reprint the same official text.

## Richest sub-sections (for i-am-witty mapping)

- **Impromptu / quick-wit:** Table Topics (the single most-cited impromptu drill in
  all of public speaking), Topicsmaster, The Power of Humor in an Impromptu Speech,
  Question-and-Answer Session, Managing a Difficult Audience.
- **Humor (oratory):** Know Your Sense of Humor → Engage Your Audience with Humor →
  Power of Humor in an Impromptu Speech → Deliver Your Message with Humor — a clean,
  graduated humor ladder, unusual among speaking programs.
- **Storytelling:** Connect with Storytelling, Using Descriptive Language, Deliver
  Social Speeches, Inspire Your Audience, CC4 How to Say It, CC10 Inspire.
- **Voice/tonality:** Intro to Vocal Variety & Body Language, Understanding Vocal
  Variety, CC6 Vocal Variety, Ah-Counter (filler-word awareness), Create a Podcast.
- **Conversation / social:** Make Connections Through Networking, Prepare for an
  Interview, Understanding Emotional Intelligence, Understanding Conflict
  Resolution, Reaching Consensus.

## Coverage gaps

- Legacy **Advanced Communication Series** manuals (~15 specialty manuals) not
  enumerated — a large untapped vein for storytelling/humor/interpretive-reading
  exercises.
- A few **forms-only / administrative** catalog items (Prepare to Mentor) are thin
  as standalone "exercises."
- Path×level *sequencing* (which project sits at which level in which path) is
  documented in the dossier prose but intentionally not duplicated per-line in the
  JSONL, since the exercise content is identical regardless of where it appears.
