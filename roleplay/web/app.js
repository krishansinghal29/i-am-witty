/*
 * Roleplay coach — front-end state machine.
 *
 * Flow:  GREET -> EXPLAIN -> EXAMPLE -> ASK(question) -> COUNTDOWN(30s soft)
 *        -> LISTEN(let them finish) -> [>=2s silence] -> EVALUATE
 *        -> FEEDBACK -> {retry | new | scaffold-down}
 *
 * Latency tricks:
 *   - static coach lines are cached server-side (synthesized once, replayed),
 *   - the next question is generated DURING the explanation and DURING answers,
 *   - the evaluator fires the instant the user's turn ends; the deliberate
 *     >=2s end-of-turn silence (Deepgram utterance_end_ms) covers its latency.
 */

// --------------------------------------------------------------------------
// Static coach script (push-pull). These are spoken every session, so the
// server caches their audio after the first synth -> ~0 latency thereafter.
// --------------------------------------------------------------------------
const LINES = {
  greet: "Hey, good to see you. Let's play a little.",
  explain:
    "Okay — push pull. The whole game is two things at once: a tiny tease, and a little genuine interest. The tease shows you noticed her. The warmth shows you actually like what you see. Both true, both small. That little tension is what makes it stick.",
  example:
    "Here's one. Say she's talking a mile a minute about her dog. You could go: you are clearly a menace... and honestly kind of the best part of my day. See it? The tease, then the real thing.",
  askLead: "Alright, your turn. Here's your scenario.",
  askTail:
    "Give me a push pull on that. I'll wait about thirty seconds, so take your time.",
  nudge: "No rush. Whenever something comes to you.",
  thinking: "Mm, let me think about that one.",
  dropToPush:
    "Let's make this easier. Forget the warm part for a second, and just give me the playful tease about her. Only the push.",
  askPush: "Go ahead, just the tease.",
  nowPull:
    "Nice. Now flip it. Just the genuine part this time. Only the pull, something you actually mean.",
  askPull: "Go ahead, just the warm line.",
  recombine:
    "You've got both pieces now. Let's put them together on a fresh one.",
  again: "Same scenario. Take another swing.",
};

const THINK_WINDOW_MS = 30000; // soft thinking window before they start
const MAX_NUDGES = 2;

// --------------------------------------------------------------------------
// DOM
// --------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
const orb = $("orb");
const statusEl = $("status");
const scenarioCard = $("scenarioCard");
const scenarioText = $("scenarioText");
const transcriptWrap = $("transcriptWrap");
const transcriptLabel = $("transcriptLabel");
const transcriptText = $("transcriptText");
const feedbackWrap = $("feedbackWrap");
const feedbackText = $("feedbackText");
const startBtn = $("startBtn");
const doneBtn = $("doneBtn");
const branchBtns = $("branchBtns");
const retryBtn = $("retryBtn");
const newBtn = $("newBtn");
const resetBtn = $("resetBtn");
const metaEl = $("meta");

function setOrb(state) {
  orb.dataset.state = state;
}
function setStatus(t) {
  statusEl.textContent = t;
}
function showScenario(t) {
  scenarioText.textContent = t;
  scenarioCard.hidden = false;
}
function showTranscript(t, label = "You") {
  transcriptLabel.textContent = label;
  transcriptText.textContent = t || "…";
  transcriptWrap.hidden = false;
}
function showFeedback(t) {
  feedbackText.textContent = t;
  feedbackWrap.hidden = false;
}
function setMeta(ev, mode) {
  metaEl.innerHTML =
    `<span class="pill ${ev.verdict}">${ev.verdict}</span>` +
    `<span class="pill">mode: ${mode}</span>` +
    (ev.struggle ? `<span class="pill missed">struggling</span>` : "");
}

// --------------------------------------------------------------------------
// Audio playback queue (the coach's voice). One <audio>, played sequentially.
// `coachSpeaking` gates the mic so the coach never transcribes itself.
// --------------------------------------------------------------------------
const player = new Audio();
player.preload = "auto";
let coachSpeaking = false;

const ttsUrl = (text) => `/api/tts?text=${encodeURIComponent(text)}`;
const prefetchTts = (text) => {
  fetch(ttsUrl(text)).catch(() => {});
};

function speak(text) {
  return new Promise((resolve) => {
    coachSpeaking = true;
    setOrb("speaking");
    player.src = ttsUrl(text);
    const done = () => {
      player.onended = null;
      player.onerror = null;
      coachSpeaking = false;
      resolve();
    };
    player.onended = done;
    player.onerror = done; // never block the flow on a TTS hiccup
    player.play().catch(done);
  });
}

// --------------------------------------------------------------------------
// API
// --------------------------------------------------------------------------
async function fetchQuestion(mode) {
  const r = await fetch(`/api/question?mode=${encodeURIComponent(mode)}`);
  return r.json();
}
async function evaluate(scenario, transcript, mode) {
  const r = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ scenario, transcript, mode }),
  });
  return r.json();
}

// --------------------------------------------------------------------------
// Deepgram streaming listener (adapted from the production gateway).
// Adds vad_events + utterance_end_ms so we can detect speech-start and a
// >=2s end-of-turn silence. Emits: onSpeechStarted, onInterim, onUtteranceEnd.
// --------------------------------------------------------------------------
const PCM_WORKLET = `
class PcmWorklet extends AudioWorkletProcessor {
  process(inputs){
    const ch = inputs[0] && inputs[0][0];
    if (ch && ch.length){
      const pcm = new Int16Array(ch.length);
      for (let i=0;i<ch.length;i++){ let s=ch[i]; s=s<-1?-1:s>1?1:s; pcm[i]=s<0?s*0x8000:s*0x7fff; }
      this.port.postMessage(pcm.buffer,[pcm.buffer]);
    }
    return true;
  }
}
registerProcessor('pcm-worklet', PcmWorklet);
`;
let workletUrl = null;
function getWorkletUrl() {
  if (!workletUrl) {
    workletUrl = URL.createObjectURL(
      new Blob([PCM_WORKLET], { type: "application/javascript" }),
    );
  }
  return workletUrl;
}

// >=2s of trailing silence after speech ends the turn (this IS the deliberate
// "wait at least 2 seconds" pause from the design).
const UTTERANCE_END_MS = 2000;

async function startListening({ onSpeechStarted, onInterim, onUtteranceEnd }) {
  const tok = await (await fetch("/api/token", { method: "POST" })).json();
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  await ctx.resume();
  await ctx.audioWorklet.addModule(getWorkletUrl());

  const params = new URLSearchParams({
    model: "nova-3",
    smart_format: "true",
    interim_results: "true",
    encoding: "linear16",
    sample_rate: String(Math.round(ctx.sampleRate)),
    channels: "1",
    language: "en-US",
    vad_events: "true",
    utterance_end_ms: String(UTTERANCE_END_MS),
    endpointing: "300",
  });
  const ws = new WebSocket(
    "wss://api.deepgram.com/v1/listen?" + params.toString(),
    ["bearer", tok.token],
  );

  let finalTranscript = "";
  let bestInterim = "";
  let speaking = false;
  let closed = false;

  const best = () => (finalTranscript || bestInterim).trim();

  ws.onmessage = (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch {
      return;
    }
    const type = (msg.type || "").toLowerCase();

    if (type === "utteranceend") {
      if (speaking) onUtteranceEnd(best());
      return;
    }
    if (type === "speechstarted") {
      if (!speaking) {
        speaking = true;
        onSpeechStarted();
      }
      return;
    }
    if (type && type !== "results") return;

    const seg = msg.channel?.alternatives?.[0]?.transcript?.trim() ?? "";
    if (!seg) return;
    if (!speaking) {
      speaking = true;
      onSpeechStarted();
    }
    if (msg.is_final) {
      finalTranscript = (finalTranscript + " " + seg).trim();
      bestInterim = "";
    } else {
      bestInterim = seg;
    }
    onInterim((finalTranscript + " " + bestInterim).trim());
  };

  // pipe mic PCM -> socket, but stay silent while the coach is speaking.
  const source = ctx.createMediaStreamSource(stream);
  const node = new AudioWorkletNode(ctx, "pcm-worklet");
  node.port.onmessage = (e) => {
    if (!coachSpeaking && ws.readyState === WebSocket.OPEN) {
      ws.send(e.data);
    }
  };
  source.connect(node);
  node.connect(ctx.destination);

  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = () => reject(new Error("deepgram_ws_error"));
  });

  const teardown = () => {
    if (closed) return;
    closed = true;
    node.port.onmessage = null;
    try {
      source.disconnect();
      node.disconnect();
    } catch {}
    try {
      if (ws.readyState === WebSocket.OPEN)
        ws.send(JSON.stringify({ type: "CloseStream" }));
      ws.close();
    } catch {}
    try {
      ctx.close();
    } catch {}
    for (const t of stream.getTracks()) {
      try {
        t.stop();
      } catch {}
    }
  };

  return {
    transcript: best,
    stop: () => {
      teardown();
      return best();
    },
  };
}

// --------------------------------------------------------------------------
// Session controller
// --------------------------------------------------------------------------
let session = null;

function newSession() {
  return {
    mode: "combine", // combine | push | pull
    scenario: "",
    missStreak: 0,
    listener: null,
    thinkTimer: null,
    nudges: 0,
    answered: false,
    speaking: false,
    nextQuestion: null, // prefetched {scenario}
  };
}

function clearThinkTimer() {
  if (session?.thinkTimer) {
    clearTimeout(session.thinkTimer);
    session.thinkTimer = null;
  }
}

async function start() {
  startBtn.hidden = true;
  resetBtn.hidden = false;
  feedbackWrap.hidden = true;
  session = newSession();

  // Warm everything we can up front.
  prefetchTts(LINES.greet);
  prefetchTts(LINES.explain);
  prefetchTts(LINES.example);
  prefetchTts(LINES.askLead);
  prefetchTts(LINES.askTail);

  // Generate the first question WHILE the coach explains (latency hide).
  const qp = fetchQuestion("combine").then((q) => {
    prefetchTts(q.scenario);
    return q;
  });

  setStatus("");
  await speak(LINES.greet);
  await speak(LINES.explain);
  await speak(LINES.example);

  const q = await qp;
  session.scenario = q.scenario;
  await askScenario(false);
}

async function askScenario(isRetry) {
  branchBtns.hidden = true;
  doneBtn.hidden = true;
  feedbackWrap.hidden = true;
  showScenario(session.scenario);

  if (isRetry) {
    await speak(LINES.again);
  } else if (session.mode === "push") {
    await speak(LINES.askPush);
  } else if (session.mode === "pull") {
    await speak(LINES.askPull);
  } else {
    await speak(LINES.askLead);
    await speak(session.scenario);
    await speak(LINES.askTail);
  }

  beginListen();
}

async function beginListen() {
  session.answered = false;
  session.speaking = false;
  session.nudges = 0;
  showTranscript("", "You");
  setOrb("countdown");
  setStatus("Listening… take your time.");
  doneBtn.hidden = false;

  // Prefetch the NEXT question while the user answers this one.
  if (session.mode === "combine") {
    fetchQuestion("combine").then((q) => {
      session.nextQuestion = q;
      prefetchTts(q.scenario);
    });
  }

  try {
    session.listener = await startListening({
      onSpeechStarted: () => {
        if (session.answered) return;
        session.speaking = true;
        clearThinkTimer();
        setOrb("listening");
        setStatus("Listening…");
      },
      onInterim: (t) => showTranscript(t, "You"),
      onUtteranceEnd: (t) => finishTurn(t),
    });
  } catch (err) {
    setStatus("Mic/STT error: " + err.message);
    setOrb("idle");
    return;
  }

  // 30s soft thinking window — only matters until they start speaking.
  armThinkTimer();
}

function armThinkTimer() {
  clearThinkTimer();
  session.thinkTimer = setTimeout(onThinkTimeout, THINK_WINDOW_MS);
}

async function onThinkTimeout() {
  if (session.speaking || session.answered) return;
  if (session.nudges >= MAX_NUDGES) return;
  session.nudges += 1;
  await speak(LINES.nudge);
  if (!session.speaking && !session.answered) armThinkTimer();
}

async function finishTurn(transcript) {
  if (session.answered) return;
  session.answered = true;
  clearThinkTimer();
  doneBtn.hidden = true;

  const text = (transcript || "").trim();
  // Fire the evaluator immediately (in parallel with closing the mic).
  setOrb("evaluating");
  setStatus("");
  const evalP = text
    ? evaluate(session.scenario, text, session.mode)
    : Promise.resolve({
        verdict: "missed",
        spoken_feedback: "I didn't quite catch that — want to try once more?",
        struggle: true,
        suggest: "retry",
      });

  if (session.listener) session.listener.stop();
  showTranscript(text || "(silence)", "You");

  const ev = await evalP;
  setMeta(ev, session.mode);
  showFeedback(ev.spoken_feedback);
  await speak(ev.spoken_feedback);
  handleBranch(ev);
}

async function handleBranch(ev) {
  const missed = ev.verdict === "missed" || ev.struggle;
  session.missStreak = missed ? session.missStreak + 1 : 0;

  // Scaffold DOWN when struggling on the full thing.
  if (
    session.mode === "combine" &&
    (ev.suggest === "drop_to_push" || session.missStreak >= 2)
  ) {
    session.mode = "push";
    session.missStreak = 0;
    await speak(LINES.dropToPush);
    return askScenario(false); // same scenario, push only
  }
  // Climb back up: push -> pull -> combine.
  if (session.mode === "push" && ev.verdict !== "missed") {
    session.mode = "pull";
    await speak(LINES.nowPull);
    return askScenario(false);
  }
  if (session.mode === "pull" && ev.verdict !== "missed") {
    session.mode = "combine";
    await speak(LINES.recombine);
    return nextScenario();
  }

  // Normal: let them choose.
  setOrb("idle");
  setStatus("Try that one again, or take a fresh sentence?");
  branchBtns.hidden = false;
}

async function nextScenario() {
  branchBtns.hidden = true;
  setOrb("speaking");
  let q = session.nextQuestion;
  session.nextQuestion = null;
  if (!q) q = await fetchQuestion(session.mode);
  session.scenario = q.scenario;
  await askScenario(false);
}

// --------------------------------------------------------------------------
// Buttons
// --------------------------------------------------------------------------
startBtn.addEventListener("click", () => start());
doneBtn.addEventListener("click", () => {
  // Manual end-of-turn (covers cases where Deepgram's silence detect lags).
  if (session && !session.answered) {
    session.speaking = true;
    finishTurn(session.listener ? session.listener.transcript() : "");
  }
});
retryBtn.addEventListener("click", () => {
  branchBtns.hidden = true;
  askScenario(true);
});
newBtn.addEventListener("click", () => nextScenario());
resetBtn.addEventListener("click", () => {
  clearThinkTimer();
  if (session?.listener) session.listener.stop();
  session = null;
  branchBtns.hidden = true;
  doneBtn.hidden = true;
  resetBtn.hidden = true;
  scenarioCard.hidden = true;
  transcriptWrap.hidden = true;
  feedbackWrap.hidden = true;
  metaEl.textContent = "";
  setOrb("idle");
  setStatus("Tap start when you're ready.");
  startBtn.hidden = false;
});
