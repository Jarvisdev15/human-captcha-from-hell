from pathlib import Path
import base64
import json
import re

import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# CONFIGURATION AND LOCAL ASSETS
# ============================================================

st.set_page_config(
    page_title="TRIVIA HELL: Pick Your Poison",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = BASE_DIR / "ASSET_DATA"

if not IMAGES_DIR.is_dir():
    IMAGES_DIR = BASE_DIR / "assets_data"

AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".m4a"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

MIME_TYPES = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def scan_files(folder, extensions):
    if not folder.is_dir():
        return []

    return sorted(
        [
            p for p in folder.rglob("*")
            if p.is_file() and p.suffix.lower() in extensions
        ],
        key=lambda p: p.name.lower(),
    )


def to_data_uri(path):
    mime = MIME_TYPES.get(path.suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def normalised_name(path):
    return re.sub(r"[^a-z0-9]", "", path.stem.lower())


audio_files = scan_files(ASSETS_DIR, AUDIO_EXTS)
image_files = scan_files(IMAGES_DIR, IMAGE_EXTS)

# If the image directory is missing or empty, also check assets/.
for path in scan_files(ASSETS_DIR, IMAGE_EXTS):
    if path.resolve() not in {p.resolve() for p in image_files}:
        image_files.append(path)


def find_audio(*keywords):
    return [
        p for p in audio_files
        if any(keyword in normalised_name(p) for keyword in keywords)
    ]


wow_audio = find_audio("animewow", "wow")
sad_audio = find_audio("sadtrombone", "funnysad", "sad")

# Optional intro track.
intro_audio = find_audio(
    "intromusic", "walkthrough", "quizintro",
    "quiztheme", "backgroundmusic"
)

used_audio = {
    p.resolve() for p in wow_audio + sad_audio
}

roast_audio = [
    p for p in audio_files if p.resolve() not in used_audio
]

# Prefer a GIF whose name suggests the intended disapproval reaction.
gif_files = [p for p in image_files if p.suffix.lower() == ".gif"]

preferred_gifs = [
    p for p in gif_files
    if any(
        term in normalised_name(p)
        for term in ("disapproval", "skull", "monsterhouse", "pizza")
    )
]

meme_path = (
    preferred_gifs[0]
    if preferred_gifs
    else gif_files[0] if gif_files else None
)

# Prioritise reaction1 ... reaction8, regardless of image extension.
non_gif_images = [
    p for p in image_files
    if p.suffix.lower() != ".gif"
    and (meme_path is None or p.resolve() != meme_path.resolve())
]


def reaction_order(path):
    name = normalised_name(path)

    match = re.fullmatch(r"reaction(\d+)", name)
    if match:
        return (0, int(match.group(1)), name)

    match = re.fullmatch(r"(?:meme|image|react)(\d+)", name)
    if match:
        return (1, int(match.group(1)), name)

    return (2, name, name)


reaction_paths = sorted(non_gif_images, key=reaction_order)[:8]

ASSETS = {
    "wow": [to_data_uri(p) for p in wow_audio],
    "wrong": [to_data_uri(p) for p in roast_audio],
    "sad": [to_data_uri(p) for p in sad_audio],
    "intro": [to_data_uri(p) for p in intro_audio],
    "meme": to_data_uri(meme_path) if meme_path else "",
    "reactions": [
        {"src": to_data_uri(p), "name": p.stem}
        for p in reaction_paths
    ],
}


# ============================================================
# TRIVIA
# ============================================================

QUESTIONS = [
    {
        "category": "MARVEL",
        "q": "What is the name of Thor's hammer?",
        "options": ["Stormbreaker", "Mjolnir", "Gungnir", "Hofund"],
        "answer": "Mjolnir",
    },
    {
        "category": "DC",
        "q": "Which city is Batman primarily associated with?",
        "options": ["Metropolis", "Central City", "Gotham City", "Star City"],
        "answer": "Gotham City",
    },
    {
        "category": "ANIME",
        "q": "What village does Naruto come from?",
        "options": [
            "Hidden Sand", "Hidden Leaf",
            "Hidden Mist", "Hidden Cloud"
        ],
        "answer": "Hidden Leaf",
    },
    {
        "category": "GAMING",
        "q": "Who is the main protagonist of Red Dead Redemption 2?",
        "options": [
            "John Marston", "Arthur Morgan",
            "Dutch van der Linde", "Micah Bell",
        ],
        "answer": "Arthur Morgan",
    },
    {
        "category": "MARVEL",
        "q": "What is the real name of Black Panther?",
        "options": ["M'Baku", "T'Challa", "N'Jadaka", "T'Chaka"],
        "answer": "T'Challa",
    },
    {
        "category": "ANIME",
        "q": "In Attack on Titan, what is Eren's hometown district?",
        "options": ["Trost", "Shiganshina", "Stohess", "Karanes"],
        "answer": "Shiganshina",
    },
    {
        "category": "GENERAL",
        "q": "Which planet has the most confirmed moons according to recent counts?",
        "options": ["Jupiter", "Saturn", "Uranus", "Neptune"],
        "answer": "Saturn",
    },
    {
        "category": "DC",
        "q": "What is Superman's home planet?",
        "options": ["Thanagar", "Apokolips", "Krypton", "Oa"],
        "answer": "Krypton",
    },
    {
        "category": "GAMING",
        "q": "Which company developed the main Pokémon game series?",
        "options": ["Bandai", "Nintendo", "Game Freak", "Capcom"],
        "answer": "Game Freak",
    },
    {
        "category": "POP CULTURE",
        "q": "Which artist released the album After Hours?",
        "options": ["Drake", "The Weeknd", "Travis Scott", "Post Malone"],
        "answer": "The Weeknd",
    },
]


ASSETS_JSON = json.dumps(ASSETS)
QUESTIONS_JSON = json.dumps(QUESTIONS)


# ============================================================
# EMBEDDED GAME
# ============================================================

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
:root {
  --red: #ff303b;
  --bg: #09090d;
  --panel: #15141c;
  --muted: #aaa7b4;
  --white: #f7f4f5;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  color: var(--white);
  font-family: Inter, system-ui, -apple-system, Segoe UI, sans-serif;
  background:
    radial-gradient(ellipse at 50% -20%, #511018 0%, transparent 55%),
    radial-gradient(ellipse at 100% 100%, #241014 0%, transparent 45%),
    var(--bg);
}

button, input { font: inherit; }
button { cursor: pointer; }

.shell {
  max-width: 1000px;
  margin: auto;
  padding: 24px 22px 40px;
}

.topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.brand {
  color: #ff6971;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 3px;
}

.pill {
  padding: 7px 12px;
  border: 1px solid #3b252b;
  border-radius: 99px;
  color: #d8b8bc;
  font-size: 11px;
  letter-spacing: 1px;
}

.hero {
  text-align: center;
  padding: 16px 0 24px;
}

.eyebrow {
  color: #ff626b;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 4px;
  text-transform: uppercase;
}

h1 {
  margin: 14px 0;
  font-size: clamp(34px, 7vw, 65px);
  line-height: 1.02;
  letter-spacing: -2.5px;
}

h1 span { color: var(--red); }

.subtitle {
  max-width: 600px;
  margin: auto;
  color: var(--muted);
  line-height: 1.65;
}

.panel {
  padding: clamp(18px, 4vw, 34px);
  border: 1px solid #30252b;
  border-radius: 22px;
  background: linear-gradient(145deg, #17171f, #101015);
  box-shadow: 0 20px 70px #0007;
}

.center { text-align: center; }
.muted { color: var(--muted); }
.small { font-size: 12px; }

.primary, .secondary {
  padding: 14px 20px;
  border-radius: 12px;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: transform .15s, filter .15s;
}

.primary {
  border: 0;
  color: white;
  background: var(--red);
  box-shadow: 0 8px 25px #ff303b30;
}

.secondary {
  color: white;
  background: #24232c;
  border: 1px solid #45414b;
}

.primary:hover, .secondary:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.primary:disabled {
  opacity: .4;
  cursor: not-allowed;
  transform: none;
}

.field {
  width: 100%;
  padding: 15px;
  border: 1px solid #45333a;
  border-radius: 12px;
  outline: none;
  color: white;
  background: #09090e;
}

.field:focus { border-color: var(--red); }

.name-row {
  max-width: 460px;
  margin: 24px auto 0;
}

.name-row .primary {
  width: 100%;
  margin-top: 14px;
}

.statrow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.time {
  font-size: 22px;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
}

.time.urgent {
  color: #ff4b54;
  animation: pulse .7s infinite alternate;
}

@keyframes pulse {
  from { opacity: 1; }
  to { opacity: .5; }
}

.progressline {
  height: 5px;
  margin: 10px 0 20px;
  overflow: hidden;
  border-radius: 20px;
  background: #2b2025;
}

.progressfill {
  height: 100%;
  width: 100%;
  background: var(--red);
  transition: width .4s linear;
}

.qmeta {
  color: #ff737a;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 2px;
}

.question {
  margin: 18px 0 25px;
  font-size: clamp(23px, 4vw, 36px);
  line-height: 1.2;
}

.option-area {
  min-height: 370px;
  padding: 8px 0;
  overflow: hidden;
  border-radius: 16px;
  position: relative;
}

.options {
  position: relative;
  width: 100%;
  height: 350px;
  min-height: 350px;
  overflow: hidden;
  border-radius: 14px;
  background: radial-gradient(ellipse at center, #17131a 0%, #0d0c12 75%);
}

.option {
  position: absolute;
  z-index: 2;
  width: calc(50% - 10px);
  min-height: 76px;
  padding: 16px;
  overflow-wrap: anywhere;
  text-align: left;
  border: 1px solid #3d343d;
  border-radius: 14px;
  color: #f6f1f3;
  background: #1a1921;
  font-weight: 750;
  user-select: none;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: left .22s ease, top .22s ease, background .15s, border-color .15s;
}

.option:hover { border-color: #ff656c; }

.option .letter {
  display: inline-flex;
  width: 27px;
  height: 27px;
  margin-right: 8px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #ff7b82;
  background: #33232a;
  font-size: 12px;
}

.option.locked {
  border-color: #ff646b;
  background: #31151b;
}

.option.frozen {
  pointer-events: none;
  opacity: .8;
}

.question-note {
  margin-top: 12px;
  color: #777681;
  font-size: 11px;
}

.challenge-title {
  margin: 10px 0;
  font-size: clamp(25px, 5vw, 42px);
}

.grid9 {
  display: grid;
  grid-template-columns: repeat(3, 82px);
  justify-content: center;
  gap: 10px;
  margin: 24px auto;
}

.tile {
  display: flex;
  width: 82px;
  height: 82px;
  align-items: center;
  justify-content: center;
  border: 1px solid #51424b;
  border-radius: 14px;
  background: #1c1b23;
  font-size: 30px;
}

.tile.selected {
  border: 2px solid #ff404a;
  background: #35141b;
}

.verify-area {
  position: relative;
  height: 175px;
  margin: 22px 0;
  overflow: hidden;
  border: 1px dashed #4a3a42;
  border-radius: 16px;
  background: #0c0c11;
}

.verifybox {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid #ccc;
  border-radius: 7px;
  color: #171717;
  background: #f5f5f5;
  box-shadow: 0 4px 12px #0006;
  font-size: 13px;
  white-space: nowrap;
  user-select: none;
  cursor: pointer;
}

.check-square {
  display: inline-flex;
  width: 23px;
  height: 23px;
  align-items: center;
  justify-content: center;
  border: 2px solid #777;
  background: white;
}

.verifybox.done .check-square {
  border-color: #16803c;
  color: #16803c;
  background: #d8f8df;
}

.resultmark {
  margin: 8px 0;
  font-size: 65px;
}

.score {
  font-size: clamp(50px, 10vw, 90px);
  font-weight: 1000;
  letter-spacing: -4px;
}

.score span { color: var(--red); }

/* Images retain their aspect ratio. The caption sits ABOVE the GIF. */
.revealimg, .reactionimg {
  display: block;
  width: auto;
  height: auto;
  max-width: min(100%, 620px);
  max-height: 440px;
  margin: 16px auto 24px;
  border-radius: 16px;
  object-fit: contain;
}

.reactionimg { max-height: 460px; }

.image-caption {
  margin: 26px 0 12px;
  font-size: clamp(27px, 5vw, 44px);
  line-height: 1.15;
  font-weight: 950;
  color: #fff;
  letter-spacing: -1px;
}

.footerline {
  margin-top: 22px;
  color: #605b66;
  text-align: center;
  font-size: 10px;
  letter-spacing: 2px;
}

@keyframes tileDrift {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  35% { transform: translate(2px, -2px) rotate(.6deg); }
  70% { transform: translate(-2px, 1px) rotate(-.5deg); }
}

.tile { animation: tileDrift 2.4s ease-in-out infinite; }
.tile:nth-child(2n) { animation-delay: -.7s; }
.tile:nth-child(3n) { animation-delay: -1.2s; }
.verifybox { transition: left .18s ease, top .18s ease; }

@media(max-width: 560px) {
  .shell { padding: 16px 12px 28px; }
  .topline { margin-bottom: 14px; }
  .options { height: 410px; min-height: 410px; }
  .option-area { min-height: 430px; }
  .option { width: calc(100% - 12px); min-height: 68px; }
  .grid9 { grid-template-columns: repeat(3, 72px); gap: 8px; }
  .tile { width: 72px; height: 72px; }
}
</style>
</head>

<body>
<div id="app"></div>

<script>
"use strict";

const ASSETS = __ASSETS__;
const QUESTIONS = __QUESTIONS__;
const app = document.getElementById("app");

let playerName = "";
let approvedName = "";
let score = 0;
let questionIndex = 0;
let remaining = 60;

let timerId = null;
let shuffleTimer = null;
let verifyMoveTimer = null;
let captchaTimer = null;
let captchaSeconds = 10;
let realCaptcha = false;
let fakeCaptchaQuestions = new Set();
let soundAudio = null;
let soundStopTimer = null;

let currentPage = "name";
let answerLocked = false;
let selectedAnswer = "";
let verificationClicks = 0;
let pointerSpeed = 0;
let lastPointer = { x: 0, y: 0, t: 0 };
let captchaPending = null;
let activeOptions = [];


function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

function generateCaptchaPlan() {
  // Randomly select 4–6 fake CAPTCHA rounds for each run.
  // All remaining rounds are real. Shuffle the positions.
  // Keep this plan fixed until the game is restarted.
  const fakeCount = 4 + Math.floor(Math.random() * 3);
  const questionNumbers = Array.from(
    { length: QUESTIONS.length },
    (_, index) => index
  );

  shuffleArray(questionNumbers);

  fakeCaptchaQuestions = new Set(
    questionNumbers.slice(0, Math.min(fakeCount, QUESTIONS.length))
  );
}

function stopTimer() {
  if (timerId !== null) clearInterval(timerId);
  timerId = null;
}

function stopShuffle() {
  if (shuffleTimer !== null) clearTimeout(shuffleTimer);
  shuffleTimer = null;
}

function stopSound() {
  if (soundStopTimer !== null) clearTimeout(soundStopTimer);
  soundStopTimer = null;

  if (soundAudio) {
    try {
      soundAudio.pause();
      soundAudio.currentTime = 0;
    } catch (error) {}
  }

  soundAudio = null;
}

function stopAllTimers() {
  stopTimer();
  stopShuffle();

  if (verifyMoveTimer !== null) clearInterval(verifyMoveTimer);
  verifyMoveTimer = null;

  if (captchaTimer !== null) clearInterval(captchaTimer);
  captchaTimer = null;
}

function playSound(kind, maxSeconds = 2) {
  stopSound();

  let choices = ASSETS[kind];
  if (!Array.isArray(choices)) choices = [choices];
  choices = choices.filter(Boolean);

  if (!choices.length) return;

  const source = choices[Math.floor(Math.random() * choices.length)];
  soundAudio = new Audio(source);
  soundAudio.volume = 0.85;

  soundAudio.play().catch(() => {});

  soundStopTimer = setTimeout(stopSound, maxSeconds * 1000);
}

function playIntroMusic() {
  stopSound();

  const choices = (ASSETS.intro || []).filter(Boolean);
  if (!choices.length) return;

  soundAudio = new Audio(
    choices[Math.floor(Math.random() * choices.length)]
  );
  soundAudio.volume = 0.32;
  soundAudio.loop = false;
  soundAudio.play().catch(() => {});

  soundStopTimer = setTimeout(stopSound, 9000);
}

function shell(content) {
  app.innerHTML = `
    <div class="shell">
      <div class="topline">
        <div class="brand">🔥 TRIVIA HELL</div>
        <div class="pill">PICK YOUR POISON</div>
      </div>
      ${content}
      <div class="footerline">
        NO MERCY · NO PAUSE BUTTON · ONLY CHAOS
      </div>
    </div>
  `;
}


// ============================================================
// NAME ENTRY
// ============================================================

function resetGame() {
  stopAllTimers();
  stopSound();

  playerName = "";
  approvedName = "";
  score = 0;
  questionIndex = 0;
  remaining = 60;
  answerLocked = false;
  selectedAnswer = "";
  verificationClicks = 0;
  captchaPending = null;
  captchaSeconds = 10;
  realCaptcha = false;

  // A new hidden real/fake CAPTCHA arrangement for the new run.
  generateCaptchaPlan();

  renderNamePage();
}

function renderNamePage() {
  currentPage = "name";
  stopAllTimers();
  stopSound();

  shell(`
    <section class="hero">
      <div class="eyebrow">THE MULTIVERSE IS NOT READY</div>
      <h1>TRIVIA <span>HELL</span></h1>
      <p class="subtitle">
        Ten questions. One countdown. Four answers that absolutely refuse to cooperate.
      </p>
    </section>

    <section class="panel center">
      <div class="eyebrow">IDENTIFY YOURSELF</div>
      <h2>Enter your name</h2>
      <p class="muted small">Proceed at your own risk.</p>

      <div class="name-row">
        <input id="nameInput" class="field"
          placeholder="Your name..." maxlength="18"
          autocomplete="off" spellcheck="false">
        <button id="startButton" class="primary">ENTER THE HELL</button>
      </div>

      <p id="nameHint" class="muted small" style="margin-top:15px">
        Every character requires approval.
      </p>
    </section>
  `);

  setupNameInput();
}

function setupNameInput() {
  const input = document.getElementById("nameInput");
  const start = document.getElementById("startButton");

  input.value = approvedName;
  start.disabled = !approvedName.trim();

  input.addEventListener("beforeinput", event => {
    if (currentPage !== "name") {
      event.preventDefault();
      return;
    }

    if (event.inputType === "insertText" && event.data) {
      event.preventDefault();

      if (approvedName.length >= 18) return;

      captchaPending = {
        type: "insert",
        character: event.data.slice(0, 1)
      };

      input.blur();
      showTrafficCaptcha(completeNameCaptcha);
    } else if (
      event.inputType === "deleteContentBackward" ||
      event.inputType === "deleteContentForward"
    ) {
      event.preventDefault();

      if (!approvedName.length) return;

      captchaPending = { type: "delete" };
      input.blur();
      showTrafficCaptcha(completeNameCaptcha);
    } else {
      event.preventDefault();
    }
  });

  input.addEventListener("paste", event => event.preventDefault());
  input.addEventListener("drop", event => event.preventDefault());

  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !start.disabled) start.click();
  });

  start.addEventListener("click", () => {
    if (currentPage !== "name" || !approvedName.trim()) return;

    playerName = approvedName.trim();
    startQuestion(0, false);

    // This click is a user gesture, so browsers are more likely to allow audio.
    playIntroMusic();
  });
}

function completeNameCaptcha() {
  if (currentPage !== "nameCaptcha" || !captchaPending) return;

  if (captchaPending.type === "insert") {
    approvedName += captchaPending.character;
  } else if (captchaPending.type === "delete") {
    approvedName = approvedName.slice(0, -1);
  }

  captchaPending = null;
  renderNamePage();

  const input = document.getElementById("nameInput");
  if (input) input.focus();
}

function showTrafficCaptcha(onSuccess) {
  currentPage = "nameCaptcha";
  stopAllTimers();
  stopSound();

  // Every addition/deletion gets a fresh randomly chosen required colour.
  const colours = [
    { name: "RED", value: "red", hex: "#ff3b45" },
    { name: "YELLOW", value: "yellow", hex: "#ffcc3d" },
    { name: "GREEN", value: "green", hex: "#30d878" }
  ];

  const required = colours[Math.floor(Math.random() * colours.length)];

  shell(`
    <section class="panel center">
      <div class="eyebrow">CHARACTER CHANGE DETECTED</div>
      <h2 class="challenge-title">Traffic-light verification</h2>
      <p class="muted">
        The system demands the following colour before it allows this character change.
      </p>

      <div style="font-size:13px;letter-spacing:3px;color:#ff737a;font-weight:900">
        REQUIRED SIGNAL
      </div>

      <div style="font-size:34px;font-weight:1000;margin:12px 0;color:${required.hex}">
        ${required.name}
      </div>

      <div class="traffic" style="gap:16px;margin:22px auto">
        ${colours.map(colour => `
          <button type="button" data-colour="${colour.value}"
            aria-label="Choose ${colour.name}"
            style="width:76px;height:76px;border-radius:50%;border:5px solid #555;
            background:${colour.hex};opacity:.92;box-shadow:0 0 14px ${colour.hex}33">
          </button>
        `).join("")}
      </div>

      <p id="trafficStatus" class="muted small">
        Pick the exact colour requested by the computer.
      </p>
    </section>
  `);

  document.querySelectorAll("[data-colour]").forEach(button => {
    button.addEventListener("click", () => {
      if (currentPage !== "nameCaptcha") return;

      if (button.dataset.colour === required.value) {
        const status = document.getElementById("trafficStatus");

        if (status) {
          status.textContent = "Signal accepted. Character approved.";
        }

        document.querySelectorAll("[data-colour]").forEach(item => {
          item.disabled = true;
          item.style.opacity = item === button ? "1" : ".3";
        });

        setTimeout(() => {
          if (currentPage === "nameCaptcha") onSuccess();
        }, 250);

        return;
      }

      // Wrong signal destroys the entire name.
      approvedName = "";
      playerName = "";
      captchaPending = null;
      stopAllTimers();

      const status = document.getElementById("trafficStatus");

      if (status) {
        status.textContent =
          "WRONG SIGNAL. YOUR ENTIRE NAME HAS BEEN ERASED.";
        status.style.color = "#ff303b";
        status.style.fontWeight = "900";
      }

      document.querySelectorAll("[data-colour]").forEach(item => {
        item.disabled = true;
      });

      setTimeout(() => {
        if (currentPage === "nameCaptcha") renderNamePage();
      }, 1100);
    });
  });
}


// ============================================================
// QUESTION AND TIMER
// ============================================================

function startQuestion(index, addBonus) {
  stopAllTimers();
  stopSound();

  // Correct answers grant +5 seconds, capped at 60 seconds.
  if (addBonus) remaining = Math.min(60, remaining + 5);

  if (remaining <= 0) {
    renderScorePage();
    return;
  }

  questionIndex = index;
  answerLocked = false;
  selectedAnswer = "";
  verificationClicks = 0;
  currentPage = "question";

  renderQuestion();
  startQuestionTimer();
}

function startQuestionTimer() {
  stopTimer();
  updateTimerUI();

  timerId = setInterval(() => {
    if (currentPage !== "question" || answerLocked) return;

    remaining = Math.max(0, remaining - 1);
    updateTimerUI();

    if (remaining <= 0) {
      stopTimer();
      stopShuffle();
      renderScorePage();
    }
  }, 1000);
}

function updateTimerUI() {
  const label = document.getElementById("timeLabel");
  const fill = document.getElementById("timeFill");

  if (label) {
    label.textContent = `${remaining}s`;
    label.classList.toggle("urgent", remaining <= 10);
  }

  if (fill) {
    fill.style.width = `${Math.max(0, remaining / 60 * 100)}%`;
  }
}

function renderQuestion() {
  const question = QUESTIONS[questionIndex];

  activeOptions = question.options.map((text, index) => ({
    text,
    letter: "ABCD"[index]
  }));

  shuffleArray(activeOptions);

  shell(`
    <div class="statrow">
      <div>
        <div class="qmeta">
          ${escapeHtml(question.category)}
          · QUESTION ${questionIndex + 1} / ${QUESTIONS.length}
        </div>

        <div class="muted small" style="margin-top:6px">
          Player: ${escapeHtml(playerName)}
        </div>
      </div>

      <div class="time" id="timeLabel">${remaining}s</div>
    </div>

    <div class="progressline">
      <div id="timeFill" class="progressfill"
        style="width:${remaining / 60 * 100}%"></div>
    </div>

    <section class="panel">
      <div class="eyebrow">MAKE YOUR MOVE</div>
      <div class="question">${escapeHtml(question.q)}</div>

      <div class="option-area">
        <div id="options" class="options">
          ${activeOptions.map(optionHTML).join("")}
        </div>
      </div>

      <div class="question-note">
        The options are unstable. Your decision is final.
      </div>
    </section>
  `);

  bindOptionButtons();
  startOptionShuffle();
}

function optionHTML(option) {
  return `
    <button class="option"
      data-option="${escapeHtml(option.text)}" type="button">
      <span class="letter">${option.letter}</span>
      ${escapeHtml(option.text)}
    </button>
  `;
}

function bindOptionButtons() {
  document.querySelectorAll("[data-option]").forEach(button => {
    button.addEventListener("click", () => {
      if (answerLocked || currentPage !== "question") return;
      lockAnswer(button.dataset.option, button);
    });
  });
}

function startOptionShuffle() {
  stopShuffle();

  const container = document.getElementById("options");
  if (!container) return;

  placeOptions(true);

  function cycle() {
    if (currentPage !== "question" || answerLocked) return;

    placeOptions(false);

    const urgency = 1 - Math.min(remaining, 60) / 60;
    const speedBonus = Math.min(pointerSpeed * 0.25, 160);
    const interval = Math.max(360, 920 - urgency * 420 - speedBonus);

    shuffleTimer = setTimeout(cycle, interval);
  }

  shuffleTimer = setTimeout(cycle, 650);
}

function placeOptions(initial = false) {
  if (currentPage !== "question" || answerLocked) return;

  const container = document.getElementById("options");
  if (!container) return;

  const buttons = [...container.querySelectorAll("[data-option]")];
  const width = container.clientWidth;
  const height = container.clientHeight;
  const mobile = window.matchMedia("(max-width: 560px)").matches;

  buttons.forEach((button, index) => {
    const bw = button.offsetWidth ||
      Math.max(120, width * (mobile ? 0.96 : 0.48));

    const bh = button.offsetHeight || 82;
    const maxX = Math.max(0, width - bw - 4);
    const maxY = Math.max(0, height - bh - 4);

    let x = 0, y = 0, attempts = 0;

    // Random positions across the playfield; avoid exact overlaps when possible.
    do {
      x = Math.random() * maxX;
      y = Math.random() * maxY;
      attempts++;
    } while (
      !initial &&
      attempts < 14 &&
      buttons.some((other, otherIndex) => {
        if (otherIndex >= index || !other.dataset.posx) return false;

        const ox = Number(other.dataset.posx);
        const oy = Number(other.dataset.posy);

        return Math.abs(x - ox) < bw * 0.58 &&
          Math.abs(y - oy) < bh * 0.78;
      })
    );

    button.style.left = `${x}px`;
    button.style.top = `${y}px`;
    button.dataset.posx = String(x);
    button.dataset.posy = String(y);
  });
}

// The answers also dodge when the pointer gets close, not just on a timer.
let lastDodgeAt = 0;

document.addEventListener("pointermove", event => {
  if (currentPage !== "question" || answerLocked) return;

  const now = performance.now();
  if (now - lastDodgeAt < 260) return;

  const buttons = [...document.querySelectorAll("#options [data-option]")];

  const near = buttons.some(button => {
    const rect = button.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;

    return Math.hypot(event.clientX - cx, event.clientY - cy) < 85;
  });

  if (near) {
    lastDodgeAt = now;
    placeOptions(false);
  }
});

function shuffleOptions() {
  placeOptions(false);
}

document.addEventListener("pointermove", event => {
  const now = performance.now();

  if (lastPointer.t) {
    const dx = event.clientX - lastPointer.x;
    const dy = event.clientY - lastPointer.y;
    const elapsed = Math.max(1, now - lastPointer.t);

    pointerSpeed = Math.min(
      450,
      Math.sqrt(dx * dx + dy * dy) / elapsed * 12
    );
  }

  lastPointer = {
    x: event.clientX,
    y: event.clientY,
    t: now
  };
});


// ============================================================
// ANSWER LOCK AND MOVING CHECKBOX
// ============================================================

function lockAnswer(answer, selectedButton) {
  if (answerLocked || currentPage !== "question") return;

  answerLocked = true;
  selectedAnswer = answer;

  // Stop the trivia timer during CAPTCHA.
  stopTimer();
  stopShuffle();

  currentPage = "verification";

  document.querySelectorAll("[data-option]").forEach(button => {
    button.classList.add("frozen");
    button.disabled = true;
  });

  if (selectedButton) selectedButton.classList.add("locked");

  renderMovingVerification();
}

function renderMovingVerification() {
  currentPage = "verification";
  verificationClicks = 0;
  captchaSeconds = 10;

  // The current question number is zero-indexed.
  // If it exists in fakeCaptchaQuestions, it is fake; otherwise it is real.
  realCaptcha = !fakeCaptchaQuestions.has(questionIndex);

  shell(`
    <section class="panel center">
      <div class="eyebrow">HUMAN VERIFICATION REQUIRED</div>
      <h2 class="challenge-title">Catch the checkbox.</h2>
      <p class="muted">
        Complete verification within 10 seconds to continue.
      </p>

      <div class="statrow" style="max-width:440px;margin:18px auto">
        <span class="muted small">CAPTCHA TIME REMAINING</span>
        <span class="time" id="captchaTime">10s</span>
      </div>

      <div class="progressline" style="max-width:440px;margin:0 auto 20px">
        <div id="captchaFill" class="progressfill" style="width:100%"></div>
      </div>

      <div class="verify-area" id="verifyArea">
        <div class="verifybox" id="verifyBox" role="button" tabindex="0">
          <span class="check-square" id="checkSquare"></span>
          <span>I'm not a robot</span>
        </div>
      </div>

      <p id="verifyStatus" class="muted small">
        Click the checkbox to verify.
      </p>
    </section>
  `);

  moveVerifyBox();

  // Identical movement speed prevents the type being revealed by speed.
  startVerifyDrift("verification", 850);

  const box = document.getElementById("verifyBox");

  box.addEventListener("click", verificationClick);

  box.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      verificationClick();
    }
  });

  captchaTimer = setInterval(() => {
    if (currentPage !== "verification") {
      if (captchaTimer !== null) clearInterval(captchaTimer);
      captchaTimer = null;
      return;
    }

    captchaSeconds = Math.max(0, captchaSeconds - 1);

    const label = document.getElementById("captchaTime");
    const fill = document.getElementById("captchaFill");

    if (label) {
      label.textContent = `${captchaSeconds}s`;
      label.classList.toggle("urgent", captchaSeconds <= 3);
    }

    if (fill) fill.style.width = `${captchaSeconds * 10}%`;

    if (captchaSeconds <= 0) {
      if (captchaTimer !== null) clearInterval(captchaTimer);
      captchaTimer = null;

      if (verifyMoveTimer !== null) clearInterval(verifyMoveTimer);
      verifyMoveTimer = null;

      if (realCaptcha) {
        currentPage = "captchaFailed";

        shell(`
          <section class="panel center">
            <div class="eyebrow">HUMAN CHECK FAILED</div>
            <div class="resultmark">⏱️</div>
            <h2 class="challenge-title">You didn't catch it in time.</h2>
            <p class="muted">
              Your run has been reset. Back to Question 1.
            </p>
            <button id="captchaRetry" class="primary">
              RESTART FROM THE BEGINNING
            </button>
          </section>
        `);

        document.getElementById("captchaRetry").addEventListener(
          "click",
          resetGame
        );

        setTimeout(() => {
          if (currentPage === "captchaFailed") resetGame();
        }, 1800);
      } else {
        // Fake checks automatically pass when their 10-second timer expires.
        const status = document.getElementById("verifyStatus");

        if (status) status.textContent = "Verification accepted.";

        setTimeout(revealLockedAnswer, 350);
      }
    }
  }, 1000);
}

function moveVerifyBox() {
  const area = document.getElementById("verifyArea");
  const box = document.getElementById("verifyBox");

  if (!area || !box) return;

  const maxX = Math.max(0, area.clientWidth - box.offsetWidth - 8);
  const maxY = Math.max(0, area.clientHeight - box.offsetHeight - 8);

  box.style.left = `${Math.random() * maxX}px`;
  box.style.top = `${Math.random() * maxY}px`;
}

function startVerifyDrift(expectedPage, intervalMs = 950) {
  if (verifyMoveTimer !== null) clearInterval(verifyMoveTimer);

  verifyMoveTimer = setInterval(() => {
    if (currentPage !== expectedPage) {
      clearInterval(verifyMoveTimer);
      verifyMoveTimer = null;
      return;
    }

    moveVerifyBox();
  }, intervalMs);
}

function verificationClick() {
  if (currentPage !== "verification") return;

  // Fake checks ignore clicks but look and move exactly like real checks.
  if (!realCaptcha) {
    const status = document.getElementById("verifyStatus");

    if (status) status.textContent = "Verification pending.";

    moveVerifyBox();
    return;
  }

  if (verificationClicks >= 1) return;
  verificationClicks++;

  const box = document.getElementById("verifyBox");
  const square = document.getElementById("checkSquare");
  const status = document.getElementById("verifyStatus");

  if (!box || !square || !status) return;

  square.textContent = "✓";
  box.classList.add("done");
  status.textContent = "Caught! Verification accepted.";

  box.style.pointerEvents = "none";

  if (verifyMoveTimer !== null) clearInterval(verifyMoveTimer);
  verifyMoveTimer = null;

  if (captchaTimer !== null) clearInterval(captchaTimer);
  captchaTimer = null;

  setTimeout(revealLockedAnswer, 350);
}

function revealLockedAnswer() {
  if (currentPage !== "verification") return;

  const correct = QUESTIONS[questionIndex].answer === selectedAnswer;

  stopAllTimers();
  stopSound();

  if (correct) {
    score++;
    renderAnswerResult(true);
    playSound("wow", 1.5);
  } else {
    renderAnswerResult(false);
    playSound("wrong", 1.8);
  }
}


// ============================================================
// RESULT AFTER EACH QUESTION
// ============================================================

function renderAnswerResult(correct) {
  currentPage = "answerResult";

  const question = QUESTIONS[questionIndex];

  shell(`
    <section class="panel center">
      <div class="resultmark">${correct ? "✓" : "✕"}</div>

      <div class="eyebrow">
        ${correct ? "CORRECT ANSWER" : "RUN OVER"}
      </div>

      <h2 class="challenge-title">
        ${correct
          ? "You survived that one."
          : "The multiverse is disappointed."}
      </h2>

      <p class="muted">
        Your answer: <strong>${escapeHtml(selectedAnswer)}</strong>
      </p>

      ${!correct ? `
        <p>The correct answer was
          <strong>${escapeHtml(question.answer)}</strong>.
        </p>
      ` : ""}

      <p class="muted">Score: ${score} / ${QUESTIONS.length}</p>

      ${correct
        ? `<button id="nextQuestion" class="primary">
             ${questionIndex === QUESTIONS.length - 1
               ? "VIEW FINAL SCORE"
               : "NEXT QUESTION"}
           </button>`
        : `<button id="retryGame" class="primary">START AGAIN</button>`
      }
    </section>
  `);

  if (correct) {
    document.getElementById("nextQuestion").addEventListener("click", () => {
      if (currentPage !== "answerResult") return;

      if (questionIndex >= QUESTIONS.length - 1) {
        renderScorePage();
      } else {
        startQuestion(questionIndex + 1, true);
      }
    });
  } else {
    document.getElementById("retryGame").addEventListener("click", resetGame);
  }
}


// ============================================================
// SCORE PAGE
// ============================================================

function roastForScore(value) {
  if (value === 10) return "Absolutely unreal. The multiverse fears you.";
  if (value >= 8) return "Suspiciously competent. We're investigating.";
  if (value >= 6) return "Not bad. Your survival instincts are functional.";
  if (value >= 4) return "You have witnessed the questions. Understanding is optional.";
  if (value >= 2) return "The options moved. Your confidence moved faster.";
  return "A historic performance. In the wrong direction.";
}

function renderScorePage() {
  stopAllTimers();
  stopSound();
  currentPage = "score";

  shell(`
    <section class="hero">
      <div class="eyebrow">RUN COMPLETE</div>
      <h1>THE DAMAGE <span>REPORT</span></h1>
    </section>

    <section class="panel center">
      <p class="muted">
        PLAYER: ${escapeHtml(playerName || "UNKNOWN")}
      </p>

      <div class="score">${score}<span>/10</span></div>
      <h2>${escapeHtml(roastForScore(score))}</h2>

      <p class="muted">
        The questions are done. Unfortunately, you are not.
      </p>

      <button id="finalVerify" class="primary">CONTINUE</button>
    </section>
  `);

  if (score === 10) playSound("wow", 2.2);

  document.getElementById("finalVerify").addEventListener("click", () => {
    if (currentPage === "score") renderPrePrizeMeme();
  });
}


// ============================================================
// REACTION MEME BEFORE THE PRIZE REVEAL
// ============================================================

function renderPrePrizeMeme() {
  stopAllTimers();
  stopSound();
  currentPage = "prePrizeMeme";

  const reactions = ASSETS.reactions || [];
  const reaction = reactions.length
    ? reactions[Math.floor(Math.random() * reactions.length)]
    : null;

  const quotes = [
    "Your score has been reviewed by absolutely nobody.",
    "Please remain calm while we pretend this is a reward.",
    "You made it this far. That was your first mistake.",
    "The committee has seen enough. The committee is a toaster."
  ];

  const quote = quotes[Math.floor(Math.random() * quotes.length)];

  shell(`
    <section class="panel center">
      <div class="eyebrow">A QUICK REACTION BEFORE YOUR PRIZE</div>

      <h2 class="challenge-title">
        ${escapeHtml(playerName)}, the system has thoughts.
      </h2>

      ${reaction
        ? `<img class="reactionimg" src="${reaction.src}"
             alt="${escapeHtml(reaction.name)}">`
        : `<div class="resultmark">🫠</div>
           <p class="muted small">
             No reaction photos detected. Check the ASSET_DATA folder.
           </p>`
      }

      <p style="font-size:20px;font-weight:800">
        ${escapeHtml(quote)}
      </p>

      <button id="toFinalVerify" class="primary">
        CONTINUE TO PRIZE
      </button>
    </section>
  `);

  document.getElementById("toFinalVerify").addEventListener("click", () => {
    if (currentPage === "prePrizeMeme") renderFinalVerificationIntro();
  });
}


// ============================================================
// FINAL VERIFICATION
// ============================================================

function renderFinalVerificationIntro() {
  stopAllTimers();
  stopSound();
  currentPage = "finalIntro";

  shell(`
    <section class="panel center">
      <div class="eyebrow">POST-RUN REQUIREMENT</div>
      <h2 class="challenge-title">
        Another final human verification needed
      </h2>
      <p class="muted">One more check before we can finish.</p>
      <button id="finalContinue" class="primary">CONTINUE</button>
    </section>
  `);

  document.getElementById("finalContinue").addEventListener("click", () => {
    if (currentPage === "finalIntro") renderFinalVerification();
  });
}

function renderFinalVerification() {
  currentPage = "finalVerification";
  verificationClicks = 0;

  shell(`
    <section class="panel center">
      <div class="eyebrow">FINAL CHECK</div>
      <h2 class="challenge-title">Confirm your humanity</h2>
      <p class="muted">Two clicks. Surely this is the end.</p>

      <div class="verify-area" id="verifyArea">
        <div class="verifybox" id="verifyBox" role="button" tabindex="0">
          <span class="check-square" id="checkSquare"></span>
          <span>I'm not a robot</span>
        </div>
      </div>

      <p id="verifyStatus" class="muted small">Verification: 0 / 2</p>
    </section>
  `);

  moveVerifyBox();
  startVerifyDrift("finalVerification");

  const box = document.getElementById("verifyBox");

  box.addEventListener("click", finalVerificationClick);

  box.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      finalVerificationClick();
    }
  });
}

function finalVerificationClick() {
  if (currentPage !== "finalVerification" || verificationClicks >= 2) return;

  verificationClicks++;

  const box = document.getElementById("verifyBox");
  const square = document.getElementById("checkSquare");
  const status = document.getElementById("verifyStatus");

  if (!box || !square || !status) return;

  square.textContent = "✓";
  box.classList.add("done");
  status.textContent = `Verification: ${verificationClicks} / 2`;

  if (verificationClicks === 1) {
    setTimeout(() => {
      if (currentPage !== "finalVerification") return;

      box.classList.remove("done");
      square.textContent = "";
      moveVerifyBox();
    }, 180);

    return;
  }

  box.style.pointerEvents = "none";

  if (verifyMoveTimer !== null) clearInterval(verifyMoveTimer);
  verifyMoveTimer = null;

  setTimeout(() => {
    if (currentPage === "finalVerification") renderPrizePage();
  }, 450);
}


// ============================================================
// PRIZE PRANK AND DISAPPROVAL GIF
// ============================================================

function renderPrizePage() {
  currentPage = "prize";
  stopSound();

  shell(`
    <section class="panel center">
      <div class="eyebrow">VERIFICATION COMPLETE</div>
      <h2 class="challenge-title">Your reward awaits.</h2>

      <p class="muted">
        You have earned the right to discover what comes next.
      </p>

      <button id="revealPrize" class="primary">REVEAL MY PRIZE</button>
    </section>
  `);

  document.getElementById("revealPrize").addEventListener("click", () => {
    if (currentPage === "prize") renderPrankPage();
  });
}

function renderPrankPage() {
  currentPage = "prank";
  stopSound();

  shell(`
    <section class="panel center">
      <div class="eyebrow">PRIZE REVEALED</div>

      <h2 class="challenge-title">
        Sorry, you will have to start again.
      </h2>

      <p class="muted">
        Thanks for your patience. We have decided not to use it.
      </p>

      <h2 class="image-caption">this u right now?</h2>

      ${ASSETS.meme
        ? `<img class="revealimg" src="${ASSETS.meme}"
             alt="Disapproving reaction GIF">`
        : `<div class="resultmark">💀</div>
           <p class="muted small">
             No GIF found. Put skull_disapproval.gif inside ASSET_DATA.
           </p>`
      }

      <button id="postCredit" class="primary">NEXT TO CONTINUE</button>
    </section>
  `);

  playSound("sad", 2.5);

  document.getElementById("postCredit").addEventListener("click", () => {
    if (currentPage === "prank") renderPostCredit();
  });
}


// ============================================================
// POST-CREDIT REACTION IMAGE
// ============================================================

function renderPostCredit() {
  currentPage = "postCredit";
  stopSound();

  const reactions = ASSETS.reactions || [];
  const reaction = reactions.length
    ? reactions[Math.floor(Math.random() * reactions.length)]
    : null;

  const quotes = [
    "You passed the vibe check. The system rejected the result.",
    "Your patience has been noted and immediately ignored.",
    "Error 404: reward not found.",
    "You were this close. Unfortunately, this close is not close enough.",
    "Achievement unlocked: wasted a perfectly good minute.",
    "The real prize was the suffering you collected along the way.",
    "Congratulations. You have been promoted to professional button-clicker.",
    "The system says you look like you need another attempt."
  ];

  const quote = quotes[Math.floor(Math.random() * quotes.length)];

  shell(`
    <section class="panel center">
      <div class="eyebrow">POST-CREDIT SCENE</div>

      <h2 class="challenge-title">Oh, you thought we were done?</h2>

      ${reaction
        ? `<img class="reactionimg" src="${reaction.src}"
             alt="${escapeHtml(reaction.name)}">`
        : `<div class="resultmark">🫠</div>
           <p class="muted small">
             No reaction images found. Add reaction1.jpg through reaction8.jpg
             to ASSET_DATA.
           </p>`
      }

      <p style="font-size:20px;font-weight:800">
        ${escapeHtml(quote)}
      </p>

      <button id="startAgain" class="primary">START AGAIN</button>
    </section>
  `);

  document.getElementById("startAgain").addEventListener("click", resetGame);
}


// ============================================================
// BOOT
// ============================================================

generateCaptchaPlan();
renderNamePage();
</script>
</body>
</html>
"""

GAME_HTML = GAME_HTML.replace("__ASSETS__", ASSETS_JSON)
GAME_HTML = GAME_HTML.replace("__QUESTIONS__", QUESTIONS_JSON)

components.html(
    GAME_HTML,
    height=1400,
    scrolling=True,
)