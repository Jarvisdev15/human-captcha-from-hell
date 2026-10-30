# 🔥 TRIVIA HELL: Pick Your Poison

### A Human CAPTCHA from Hell

*What if proving you're human online became an absolutely miserable experience?*

**Built for What The Hack?! 2.0**

**Team:** TheOnlyBot | **Developer:** Yuvraj Bhatia (solo)

👉 **[Play it live](https://human-captcha-from-hell-reu9bvtj54cepsvjyucmsc.streamlit.app/)**

*Turn your sound on. Click anywhere on the page first so your browser allows audio.*

---

## The idea

Trivia Hell looks like a normal quiz. It isn't. Every step is guarded by a **human-verification CAPTCHA** designed to waste your time, test your patience and make you question why you kept going.

The answers won't stay still, the checkboxes run away, and at the end the prize is not a prize.

## Trivia Hell: Pick Your Poison

- 10 questions on Marvel, DC, anime, gaming and pop culture
- A 60-second countdown, with a few seconds back for each correct answer
- **Moving answer options** that jump around the screen and dodge your cursor
- Difficulty that adapts: answer fast and the options move faster
- One wrong answer ends your run

## The Human CAPTCHAs from Hell

| CAPTCHA | The torture |
|---|---|
| 🚦 **Traffic-light name entry** | Every letter you type or delete needs its own traffic-light CAPTCHA. Pick the wrong colour and your **whole name is erased**. |
| ☑️ **Catch the checkbox** | After every answer, an "I'm not a robot" box drifts around the screen with a 10-second timer. Miss it on a real check and your run resets to Question 1. |
| 🎭 **Real vs fake checks** | Some checkboxes are fake: they ignore your clicks and only pass when the timer ends. They look and move exactly like the real ones. |
| ✅ **The "final" verification** | After the quiz you need *another* human check: two clicks on a moving checkbox. "Surely this is the end." |
| ⏳ **Fake prize reveal** | A loading bar sticks at 99%, then reveals a disapproving GIF and a sad trombone. |

## Chaos that escalates

- The interface starts clean and professional, then the panels tilt a little more with every question
- A random reaction image appears once, right before the prize
- Different sound effects for correct answers, wrong answers and the final prank

## How it was built

I built this project **solo**, using **Claude** (Anthropic) and **ChatGPT** (OpenAI) as AI coding assistants.

- **My part:** the concept, the theme, the humour and the game flow, plus choosing the questions and picking the images and sounds. I also tested the game, fixed the asset problems, set up the repository and deployed it.
- **AI's part:** helped write and debug the Python and JavaScript, tidy the UI, and prepare the README and pitch material.

Every feature was run and tested by me before submission.

## Run it locally

You need Python 3.9 or newer.

**Windows (PowerShell):**
```powershell
git clone https://github.com/Jarvisdev15/human-captcha-from-hell.git
cd human-captcha-from-hell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**macOS / Linux:**
```bash
git clone https://github.com/Jarvisdev15/human-captcha-from-hell.git
cd human-captcha-from-hell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Project structure

```
human-captcha-from-hell/
├── app.py              Streamlit app with the embedded HTML/CSS/JS game
├── requirements.txt    Python dependencies (Streamlit 1.66.1)
├── README.md
├── ASSET_DATA/         Reaction images (reaction1.jpg ... reaction8.jpg)
└── assets/             Sound effects and the disapproval GIF
```

## Built with

- **Python** and **Streamlit** for the app and hosting
- **HTML, CSS and JavaScript**, embedded in the Streamlit page, for the game logic, animations and moving elements
- **Streamlit Community Cloud** for deployment
- **Claude** and **ChatGPT** as AI coding assistants

## Notes

- Images and audio are embedded in the page as base64, so the first load can take a moment.
- Browsers block audio until you interact with the page, so sounds start after your first click.
- If the app has gone to sleep, click **"Yes, get this app back up!"** and wait a few seconds.

## Credits

Designed and built solo by **Yuvraj Bhatia** (team **TheOnlyBot**) for **What The Hack?! 2.0**, with AI assistance from Claude and ChatGPT.

Memes, GIFs and sound effects belong to their original creators and are used here only for a non-commercial hackathon project.

*No mercy. No pause button. Only chaos.*
