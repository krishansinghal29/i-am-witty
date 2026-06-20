/*
 * Spoken conversation — turn-based audio dialogue with streaming LLM + TTS.
 *
 * Server owns session history; client sends session_id + latest user message.
 * Flow: Start -> AI opens -> listen -> user speaks -> AI streams reply -> repeat.
 */

const $ = (id) => document.getElementById(id);
const orb = $("orb");
const statusEl = $("status");
const logEl = $("log");
const startBtn = $("startBtn");
const doneBtn = $("doneBtn");
const newConvBtn = $("newConvBtn");
const endBtn = $("endBtn");

// --------------------------------------------------------------------------
// Action dock — a one-shot "move" that rides with the next spoken turn.
// Grouped chips live in a bottom sheet; the trigger pill reflects the armed
// move and clears it once consumed.
// --------------------------------------------------------------------------
const ACTION_GROUPS = [
  {
    label: "Body language",
    items: [
      { value: "sit_down", label: "Sit down", icon: "🪑" },
      { value: "hold_gaze", label: "Hold eye contact", icon: "👁️" },
      { value: "lean_in", label: "Lean in", icon: "💫" },
      { value: "step_back", label: "Step back", icon: "👣" },
    ],
  },
  {
    label: "Touch",
    items: [
      { value: "touch_light", label: "Light touch", icon: "🤚" },
      { value: "touch_escalate", label: "Escalate touch", icon: "🔥" },
      { value: "kiss_attempt", label: "Go for the kiss", icon: "💋" },
    ],
  },
  {
    label: "Steer the moment",
    items: [
      { value: "stop_her", label: "Stop her", icon: "🛑" },
      { value: "suggest_isolate", label: "Move aside", icon: "↪️" },
      { value: "suggest_venue_change", label: "New venue", icon: "🍸" },
      { value: "pull", label: "Leave together", icon: "🌙" },
    ],
  },
];

const actionDock = $("actionDock");
const actionTrigger = $("actionTrigger");
const actionTriggerIcon = $("actionTriggerIcon");
const actionTriggerLabel = $("actionTriggerLabel");
const actionTriggerTeaser = $("actionTriggerTeaser");
const actionClear = $("actionClear");
const actionSheet = $("actionSheet");
const actionGroups = $("actionGroups");

// Clickbait teaser — rotating flirty sample moves to entice a tap.
const ACTION_TEASERS = [
  "kiss her…",
  "lean in close…",
  "hold her gaze…",
  "pull her in…",
  "make your move…",
];
let teaserIndex = 0;
let teaserTimer = null;

const ACTION_LOOKUP = Object.fromEntries(
  ACTION_GROUPS.flatMap((g) => g.items).map((i) => [i.value, i])
);

let selectedAction = null;

function buildActionSheet() {
  if (!actionGroups) return;
  actionGroups.innerHTML = "";
  for (const group of ACTION_GROUPS) {
    const section = document.createElement("div");
    section.className = "action-group";
    const heading = document.createElement("p");
    heading.className = "action-group-label";
    heading.textContent = group.label;
    section.appendChild(heading);
    const chips = document.createElement("div");
    chips.className = "action-chips";
    for (const item of group.items) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "action-chip";
      chip.dataset.value = item.value;
      const icon = document.createElement("span");
      icon.className = "action-chip-icon";
      icon.textContent = item.icon;
      const text = document.createElement("span");
      text.textContent = item.label;
      chip.append(icon, text);
      chip.addEventListener("click", () => armAction(item.value));
      chips.appendChild(chip);
    }
    section.appendChild(chips);
    actionGroups.appendChild(section);
  }
}

function renderActionTrigger() {
  if (!actionTrigger) return;
  const item = selectedAction ? ACTION_LOOKUP[selectedAction] : null;
  actionTrigger.classList.toggle("armed", Boolean(item));
  actionTriggerIcon.textContent = item ? item.icon : "✦";
  actionTriggerLabel.textContent = item ? item.label : "Make a move";
  actionClear.hidden = !item;
  // Teaser only entices while idle; cycling pauses once a move is armed.
  if (item) stopTeaser();
  else startTeaser();
  if (actionGroups) {
    for (const chip of actionGroups.querySelectorAll(".action-chip")) {
      chip.classList.toggle("armed", chip.dataset.value === selectedAction);
    }
  }
}

function startTeaser() {
  if (!actionTriggerTeaser || teaserTimer) return;
  teaserTimer = setInterval(() => {
    teaserIndex = (teaserIndex + 1) % ACTION_TEASERS.length;
    actionTriggerTeaser.style.opacity = "0";
    setTimeout(() => {
      actionTriggerTeaser.textContent = ACTION_TEASERS[teaserIndex];
      actionTriggerTeaser.style.opacity = "";
    }, 350);
  }, 2600);
}

function stopTeaser() {
  if (teaserTimer) {
    clearInterval(teaserTimer);
    teaserTimer = null;
  }
}

function openActionSheet() {
  if (!actionSheet) return;
  actionSheet.hidden = false;
  requestAnimationFrame(() => actionSheet.classList.add("show"));
  actionTrigger.setAttribute("aria-expanded", "true");
}

function closeActionSheet() {
  if (!actionSheet || actionSheet.hidden) return;
  actionSheet.classList.remove("show");
  actionTrigger.setAttribute("aria-expanded", "false");
  setTimeout(() => {
    actionSheet.hidden = true;
  }, 260);
}

function armAction(value) {
  selectedAction = value;
  renderActionTrigger();
  closeActionSheet();
}

function clearAction() {
  selectedAction = null;
  renderActionTrigger();
}

// Read the armed move and reset — one-shot per turn.
function consumeAction() {
  const value = selectedAction;
  selectedAction = null;
  renderActionTrigger();
  return value;
}

if (actionTrigger) {
  buildActionSheet();
  renderActionTrigger();
  actionTrigger.addEventListener("click", (event) => {
    if (event.target.closest("#actionClear")) {
      clearAction();
      return;
    }
    if (actionSheet.hidden) openActionSheet();
    else closeActionSheet();
  });
  // Click anywhere outside the panel/trigger closes it — the panel never
  // covers the chat, so the transcript stays fully interactive underneath.
  document.addEventListener("click", (event) => {
    if (actionSheet.hidden) return;
    if (event.target.closest("#actionSheet, #actionTrigger")) return;
    closeActionSheet();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeActionSheet();
  });
}

let config = { utterance_end_ms: 2000, no_speech_end_ms: 6000 };
let session = null;
let chatAbort = null;

const player = new Audio();
player.preload = "auto";

// In-bubble status animations: a live mic waveform while listening, bouncing
// dots while the recorded turn is being transcribed.
const LISTENING_HTML =
  '<span class="wave" role="img" aria-label="Listening"><i></i><i></i><i></i><i></i><i></i></span>';
const TRANSCRIBING_HTML =
  '<span class="dots" role="img" aria-label="Transcribing"><i></i><i></i><i></i></span>';

// --------------------------------------------------------------------------
// UI helpers
// --------------------------------------------------------------------------
function setOrb(state) {
  orb.dataset.state = state;
}
function setStatus(text) {
  statusEl.textContent = text;
}
function showLog() {
  logEl.hidden = false;
}
function clearLog() {
  logEl.innerHTML = "";
}
function addBubble(role, text) {
  const row = document.createElement("div");
  row.className = `bubble-row ${role}`;
  const label = document.createElement("span");
  label.className = "bubble-label";
  label.textContent = role === "user" ? "You" : "AI";
  const body = document.createElement("p");
  body.className = "bubble-text";
  body.textContent = text;
  row.append(label, body);
  logEl.appendChild(row);
  logEl.scrollTop = logEl.scrollHeight;
  return body;
}

// --------------------------------------------------------------------------
// Config + session API
// --------------------------------------------------------------------------
async function loadConfig() {
  const r = await fetch("/api/config");
  config = await r.json();
}
async function createSession() {
  const r = await fetch("/api/session/new", { method: "POST" });
  const data = await r.json();
  return data.session_id;
}

// --------------------------------------------------------------------------
// Streaming chat (SSE over fetch)
// --------------------------------------------------------------------------
async function streamChat({ sessionId, message, action, onToken, signal }) {
  const r = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "content-type": "application/json" },
    // `action` is ignored by the old server (extra field) and consumed by the new one.
    body: JSON.stringify({
      session_id: sessionId,
      message: message ?? null,
      action: action ?? null,
    }),
    signal,
  });
  if (!r.ok) {
    const detail = await r.text();
    throw new Error(detail || `chat_${r.status}`);
  }

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let reply = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const block of parts) {
      const line = block.trim();
      if (!line.startsWith("data:")) continue;
      const payload = JSON.parse(line.slice(5).trim());
      if (payload.type === "token") {
        reply += payload.text;
        onToken(payload.text, reply);
      } else if (payload.type === "done") {
        reply = payload.reply || reply;
      } else if (payload.type === "error") {
        throw new Error(payload.message || "stream_error");
      }
    }
  }
  return reply.trim();
}

// --------------------------------------------------------------------------
// Sentence-chunked TTS with transcript streaming in sync with speech
// Words appear progressively as each sentence's audio plays.
// --------------------------------------------------------------------------
let aiSpeaking = false;

function scrollLog() {
  logEl.scrollTop = logEl.scrollHeight;
}

function partialWords(text, progress) {
  const words = text.split(/\s+/).filter(Boolean);
  if (!words.length || progress <= 0) return "";
  const n = Math.min(
    words.length,
    Math.max(1, Math.floor(progress * words.length)),
  );
  return words.slice(0, n).join(" ");
}

const speech = {
  queue: [],
  running: false,
  revealed: "",
  bubble: null,
  pending: [],

  reset() {
    for (const ctrl of this.pending) {
      try {
        ctrl.abort();
      } catch {}
    }
    this.pending = [];
    this.queue = [];
    this.running = false;
    this.revealed = "";
    this.bubble = null;
    aiSpeaking = false;
    try {
      player.pause();
      player.removeAttribute("src");
    } catch {}
  },

  setDisplay(text) {
    if (this.bubble) {
      this.bubble.textContent = text;
      scrollLog();
    }
  },

  enqueue(sentence) {
    const ctrl = new AbortController();
    this.pending.push(ctrl);
    const audio = fetch("/api/tts/stream", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ text: sentence }),
      signal: ctrl.signal,
    }).then((r) => (r.ok ? r.blob() : null));
    this.queue.push({ text: sentence, audio, ctrl });
    this.pump();
  },

  async pump() {
    if (this.running) return;
    this.running = true;
    aiSpeaking = true;
    setOrb("speaking");

    while (this.queue.length > 0) {
      const item = this.queue.shift();
      try {
        const blob = await item.audio;
        if (!blob) continue;
        const base = this.revealed;
        await playBlobWithStream(blob, item.text, (progress) => {
          const chunk = partialWords(item.text, progress);
          this.setDisplay(base ? `${base} ${chunk}` : chunk);
        });
        this.revealed = base ? `${base} ${item.text}` : item.text;
        this.setDisplay(this.revealed);
      } catch (err) {
        if (err.name === "AbortError") break;
      }
    }

    this.running = false;
    aiSpeaking = false;
    if (this.queue.length > 0) this.pump();
  },

  async drain() {
    while (this.running || this.queue.length > 0) {
      await new Promise((r) => setTimeout(r, 50));
    }
  },
};

function abortAudio() {
  speech.reset();
}

function createTtsDrainer(onPhrase) {
  const MAX_PHRASE_WORDS = 10;
  let buf = "";

  const emit = (text) => {
    const t = text.trim();
    if (t.length >= 2) onPhrase(t);
  };

  const drainPhrases = () => {
    while (true) {
      const sentence = buf.match(/^(.*?[.!?])(\s+|$)/s);
      if (sentence) {
        emit(sentence[1]);
        buf = buf.slice(sentence[0].length);
        continue;
      }
      const words = buf.trim().split(/\s+/).filter(Boolean);
      if (words.length >= MAX_PHRASE_WORDS) {
        emit(words.slice(0, MAX_PHRASE_WORDS).join(" "));
        buf = words.slice(MAX_PHRASE_WORDS).join(" ");
        continue;
      }
      break;
    }
  };

  return {
    push(chunk) {
      buf += chunk;
      drainPhrases();
    },
    flush() {
      emit(buf);
      buf = "";
    },
  };
}

function playBlobWithStream(blob, sentence, onProgress) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(blob);
    player.src = url;
    let raf = 0;
    let finished = false;

    const finish = () => {
      if (finished) return;
      finished = true;
      cancelAnimationFrame(raf);
      player.onended = null;
      player.onerror = null;
      player.onloadedmetadata = null;
      URL.revokeObjectURL(url);
      onProgress(1);
      resolve();
    };

    const tick = () => {
      const d = player.duration;
      const t = player.currentTime;
      if (d && Number.isFinite(d) && d > 0) {
        onProgress(Math.min(1, t / d));
      }
      if (!player.paused && !player.ended) {
        raf = requestAnimationFrame(tick);
      }
    };

    player.onloadedmetadata = () => {};
    player.onended = finish;
    player.onerror = finish;
    player
      .play()
      .then(() => {
        raf = requestAnimationFrame(tick);
      })
      .catch(finish);
  });
}

// --------------------------------------------------------------------------
// Dictation — batch recorder
//
// We capture the whole turn as 16-bit PCM, watch the mic level to detect when
// the user has finished (trailing silence), then send one WAV to the server,
// which transcribes it with whichever provider is configured. The full
// sentence appears at once — there is no live word-by-word stream.
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

// Mono 16-bit PCM chunks -> a single WAV blob the server can forward as-is.
function encodeWav(chunks, sampleRate) {
  let total = 0;
  for (const c of chunks) total += c.length;
  const buf = new ArrayBuffer(44 + total * 2);
  const view = new DataView(buf);
  const writeStr = (off, s) => {
    for (let i = 0; i < s.length; i++) view.setUint8(off + i, s.charCodeAt(i));
  };
  writeStr(0, "RIFF");
  view.setUint32(4, 36 + total * 2, true);
  writeStr(8, "WAVE");
  writeStr(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true); // byte rate
  view.setUint16(32, 2, true); // block align
  view.setUint16(34, 16, true); // bits per sample
  writeStr(36, "data");
  view.setUint32(40, total * 2, true);
  let off = 44;
  for (const c of chunks) {
    for (let i = 0; i < c.length; i++, off += 2) view.setInt16(off, c[i], true);
  }
  return new Blob([buf], { type: "audio/wav" });
}

function rms(pcm) {
  let sum = 0;
  for (let i = 0; i < pcm.length; i++) {
    const s = pcm[i] / 0x8000;
    sum += s * s;
  }
  return pcm.length ? Math.sqrt(sum / pcm.length) : 0;
}

// VAD tuning (normalized RMS, 0..1). Two trailing-silence controls (from config):
// once the user has started speaking, utterance_end_ms ends the turn; until they've
// said anything at all, the longer no_speech_end_ms grace applies before we give up.
const SPEECH_RMS = 0.02; // normalized level that counts as "talking"
const MAX_TURN_SECONDS = 60; // hard cap so a stuck mic can't buffer forever

async function startListening({ onSpeechStarted, onTranscribing, onTurnEnd }) {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  await ctx.resume();
  await ctx.audioWorklet.addModule(getWorkletUrl());

  const utteranceEndMs = config.utterance_end_ms || 2000;
  const noSpeechEndMs = config.no_speech_end_ms || 6000;
  const sampleRate = Math.round(ctx.sampleRate);
  const maxSamples = sampleRate * MAX_TURN_SECONDS;
  const source = ctx.createMediaStreamSource(stream);
  const node = new AudioWorkletNode(ctx, "pcm-worklet");

  const chunks = []; // every captured PCM chunk for this turn
  let samples = 0;
  let started = false; // has the mic crossed the speech threshold yet?
  let lastVoiceTs = 0;
  const listenStartTs = performance.now(); // when the mic opened (silence ref before any speech)
  let finalized = false;
  let closed = false;
  let abort = null;
  let poll = null;

  const teardown = () => {
    if (closed) return;
    closed = true;
    if (poll) clearInterval(poll);
    node.port.onmessage = null;
    try {
      source.disconnect();
      node.disconnect();
    } catch {}
    for (const t of stream.getTracks()) {
      try {
        t.stop();
      } catch {}
    }
    try {
      ctx.close();
    } catch {}
  };

  node.port.onmessage = (e) => {
    if (aiSpeaking || finalized) return;
    const pcm = new Int16Array(e.data);
    chunks.push(pcm);
    samples += pcm.length;
    if (rms(pcm) >= SPEECH_RMS) {
      if (!started) {
        started = true;
        onSpeechStarted();
      }
      lastVoiceTs = performance.now();
    }
    if (samples >= maxSamples) finalize();
  };

  source.connect(node);
  node.connect(ctx.destination);

  // The recorded turn -> server -> transcript. Runs at most once.
  // `manual` (the "I'm done" button) transcribes whatever we captured even if
  // the mic never crossed the speech threshold; auto-end only fires after speech.
  const finalize = async (manual = false) => {
    if (finalized) return;
    finalized = true;
    if (poll) clearInterval(poll);
    const captured = chunks.slice();
    teardown();

    if (!captured.length || (!started && !manual)) {
      onTurnEnd("");
      return;
    }
    onTranscribing?.();
    abort = new AbortController();
    try {
      const wav = encodeWav(captured, sampleRate);
      const r = await fetch("/api/transcribe", {
        method: "POST",
        headers: { "content-type": "audio/wav" },
        body: wav,
        signal: abort.signal,
      });
      if (!r.ok) throw new Error((await r.text()) || `transcribe_${r.status}`);
      const data = await r.json();
      onTurnEnd((data.transcript || "").trim());
    } catch (err) {
      if (err.name === "AbortError") return;
      console.error("transcription failed", err);
      onTurnEnd("");
    }
  };

  // End the turn once the mic has been quiet long enough. The grace period is
  // longer before any speech (no_speech_end_ms) than the trailing-silence after
  // the user has started talking (utterance_end_ms).
  poll = setInterval(() => {
    if (finalized) return;
    const silenceMs = performance.now() - (started ? lastVoiceTs : listenStartTs);
    if (silenceMs >= (started ? utteranceEndMs : noSpeechEndMs)) finalize();
  }, 100);

  return {
    finish: () => finalize(true), // manual "I'm done"
    stop: () => {
      // Abandon the turn entirely (new conversation / end session).
      finalized = true;
      if (abort) {
        try {
          abort.abort();
        } catch {}
      }
      teardown();
    },
  };
}

// --------------------------------------------------------------------------
// Session controller
// --------------------------------------------------------------------------
function newLocalSession(sessionId) {
  return {
    sessionId,
    listener: null,
    turnDone: false,
    liveBubble: null,
    liveUserBubble: null,
  };
}

function abortChat() {
  if (chatAbort) chatAbort.abort();
  chatAbort = null;
}

function setSessionControls(active) {
  startBtn.hidden = active;
  doneBtn.hidden = !active;
  newConvBtn.hidden = !active;
  endBtn.hidden = !active;
  if (actionDock) actionDock.hidden = !active;
  if (!active) {
    closeActionSheet();
    clearAction();
  }
}

async function playAssistantTurn({ message } = {}) {
  abortChat();
  abortAudio();
  chatAbort = new AbortController();

  setOrb("thinking");
  setStatus("");

  const bubble = addBubble("assistant", "");
  session.liveBubble = bubble;
  speech.bubble = bubble;
  speech.revealed = "";
  const drainer = createTtsDrainer((phrase) => speech.enqueue(phrase));

  // One-shot: the selected action rides with this turn, then resets.
  const action = consumeAction();
  const chatDone = streamChat({
    sessionId: session.sessionId,
    message,
    action,
    signal: chatAbort.signal,
    onToken(chunk) {
      drainer.push(chunk);
    },
  });

  const reply = await chatDone;
  drainer.flush();

  // Keep bubble wired until all queued audio finishes — never dump full text early.
  await speech.drain();

  if (reply && bubble.textContent !== reply) {
    bubble.textContent = reply;
  }

  session.liveBubble = null;
  speech.bubble = null;
}

async function beginListen() {
  if (!session) return;
  session.turnDone = false;
  session.liveUserBubble = addBubble("user", "");
  session.liveUserBubble.innerHTML = LISTENING_HTML;
  setOrb("listening");
  setStatus("Listening…");

  try {
    session.listener = await startListening({
      onSpeechStarted: () => {
        if (session.turnDone) return;
        setOrb("listening");
        setStatus("Listening…");
      },
      onTranscribing: () => {
        if (session.turnDone) return;
        setOrb("thinking");
        setStatus("Transcribing…");
        if (session.liveUserBubble) {
          session.liveUserBubble.innerHTML = TRANSCRIBING_HTML;
        }
      },
      onTurnEnd: (t) => finishUserTurn(t),
    });
  } catch (err) {
    setStatus("Mic error: " + err.message);
    setOrb("idle");
  }
}

async function finishUserTurn(transcript) {
  if (!session || session.turnDone) return;
  session.turnDone = true;
  doneBtn.hidden = true;

  const text = (transcript || "").trim();
  if (session.listener) session.listener.stop();
  session.listener = null;

  if (session.liveUserBubble) {
    session.liveUserBubble.textContent = text || "(silence)";
  }

  if (!text) {
    if (session.liveUserBubble) {
      session.liveUserBubble.closest(".bubble-row")?.remove();
      session.liveUserBubble = null;
    }
    doneBtn.hidden = false;
    setStatus("Didn't catch that — try again.");
    return beginListen();
  }

  await playAssistantTurn({ message: text });
  doneBtn.hidden = false;
  return beginListen();
}

async function startConversation() {
  await loadConfig();
  showLog();
  clearLog();
  setSessionControls(true);

  const sessionId = await createSession();
  session = newLocalSession(sessionId);

  await playAssistantTurn();
  doneBtn.hidden = false;
  return beginListen();
}

async function tryNewConversation() {
  if (!session) return;
  abortChat();
  abortAudio();
  if (session.listener) session.listener.stop();
  session.listener = null;

  clearLog();
  const sessionId = await createSession();
  session = newLocalSession(sessionId);

  await playAssistantTurn();
  doneBtn.hidden = false;
  return beginListen();
}

function endSession() {
  abortChat();
  abortAudio();
  if (session?.listener) session.listener.stop();
  // Drop the in-progress "listening" bubble so its waveform stops animating.
  session?.liveUserBubble?.closest(".bubble-row")?.remove();
  session = null;
  setSessionControls(false);
  setOrb("idle");
  setStatus("Tap start when you're ready.");
}

// --------------------------------------------------------------------------
// Buttons
// --------------------------------------------------------------------------
startBtn.addEventListener("click", () => startConversation());
newConvBtn.addEventListener("click", () => tryNewConversation());
endBtn.addEventListener("click", () => endSession());
doneBtn.addEventListener("click", () => {
  if (session && !session.turnDone && session.listener) {
    doneBtn.hidden = true;
    setStatus("Transcribing…");
    session.listener.finish();
  }
});

loadConfig().catch(() => {});
