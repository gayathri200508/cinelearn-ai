# 🎬 CineGyan — GDG Hackathon MVP

*Gyan (knowledge) meets Cinema.* Pick your academic stream, pick a learning template (Movie Story, Case Study, Student Notes, or Presentation Outline), enter any topic, get an AI-generated lesson in your language — plus an auto-generated 5-question quiz. Built with Streamlit + Gemini API.

## 📁 Files in this project
- `app.py` — the actual Streamlit app
- `requirements.txt` — dependencies (`streamlit`, `google-genai`)
- `run_cinegyan.bat` — **double-click this to install + set your API key + run**, no typing commands needed
- `push_to_github.bat` — double-click this to push everything to GitHub (asks for your repo URL)
- `.gitignore` — makes sure your API key never gets pushed to GitHub
- `.streamlit/config.toml` — app theme/colors
- `.streamlit/secrets.toml.example` — example of what your (private) key file should look like

## ⚡ Fastest way to run it (Windows, no terminal typing)
1. Put all these files in one folder
2. Double-click `run_cinegyan.bat`
3. First time only: paste your Gemini API key when it asks (get one free at https://aistudio.google.com/apikey)
4. Browser opens automatically at http://localhost:8501

## 🐙 Push to GitHub (for the hackathon submission)
1. Go to github.com → New repository → name it `cinegyan` → **do NOT** check "Add README" → Create
2. Copy the repo URL it shows you
3. Double-click `push_to_github.bat` → paste that URL when asked
4. Done — your code is on GitHub, and your API key was NOT uploaded (that's correct and intentional)

## ☁️ Deploy so judges can open a live link
1. Go to https://share.streamlit.io → sign in → "New app"
2. Pick your `cinegyan` GitHub repo, main file `app.py`
3. Click "Advanced settings" → under Secrets paste:
```toml
GEMINI_API_KEY = "your-real-key-here"
```
4. Click Deploy — you get a public URL like `https://cinegyan.streamlit.app` to share with judges

## Manual setup (if you prefer typing commands yourself)
1. Get a free Gemini API key: https://aistudio.google.com/apikey
2. `pip install -r requirements.txt`
3. Create `.streamlit/secrets.toml` with: `GEMINI_API_KEY = "your-key"`
4. `streamlit run app.py` (not `python app.py`)

## Pitch (60 seconds)

> "India has millions of students who find subjective topics — history, civics, science theory, case laws — hard to engage with, especially outside English. CineGyan lets a student pick their stream — medical, engineering, law, business, whatever — and their preferred learning style: a movie-style story, a case study, exam notes, or a presentation outline. Gemini generates it live, in their own language, and can even quiz them on it right after. It's personalized, multilingual education, generated on demand."

Then **demo live**: pick a topic a judge suggests, pick a regional language, hit Generate.

## Why judges should care (say this if asked "what's innovative")
- Not just one format — 4 learning templates (story, case study, notes, slides) from the same engine
- Personalized by academic stream (medical, law, engineering, business, etc.) — not one-size-fits-all
- Native regional language support, not just English
- Closes the loop with an auto-generated quiz — content **and** assessment from one topic
- Small, focused scope — actually finished and demoable, not a slideware idea

## If you have extra time (nice-to-haves, in priority order)
1. Cache repeated topic+language+genre combos (saves API calls during demo)
2. A short quiz (3 MCQs) generated from the same story, in a second Gemini call
3. Voice narration via `gTTS` (free, simple) — only if setup is smooth
4. Movie poster via an image model — skip unless you have >2 hrs spare

## Common issues

**Running locally:**
- **403 / API key errors**: key not enabled for Gemini API, or pasted with extra whitespace. Get a fresh one at aistudio.google.com/apikey — it must start with `AIzaSy`.
- **"No secrets found"**: you edited `secrets.toml` while the app was already running. Stop it (Ctrl+C) and run `streamlit run app.py` again — Streamlit only reads secrets at startup.
- **Model not found**: use `gemini-2.5-flash` (already set in app.py) — older `gemini-1.5-flash` / `google-generativeai` package are shut down. This app uses the new `google-genai` package.
- **Blank output**: usually a very short/ambiguous topic — try a more specific topic.

**Deploying on Streamlit Community Cloud:**
- **"ModuleNotFoundError"**: your `requirements.txt` wasn't picked up, or has a typo. Make sure it's in the repo root and contains exactly `streamlit` and `google-genai` on separate lines.
- **"No secrets found" on the live app**: you forgot to add `GEMINI_API_KEY` under App settings → Secrets on share.streamlit.io — this is separate from your local `secrets.toml` and must be added again there.
- **App builds but errors on Generate**: almost always the deployed Secrets key is missing, misspelled, or wrapped in the wrong quotes. It must look exactly like: `GEMINI_API_KEY = "AIzaSy..."`
- **App is asleep / takes 30s to load**: normal on the free tier after inactivity — just wait, it wakes up. Open it once before your demo to "warm it up."
