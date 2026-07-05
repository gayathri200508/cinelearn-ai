import streamlit as st
from google import genai
import os
import json
import re
import datetime
from urllib.parse import urlencode

# =========================================================
# PAGE CONFIG (wide layout for the 3-column professional look)
# =========================================================
st.set_page_config(page_title="CineGyan 🎬 | AI Learning Platform", page_icon="🎬", layout="wide")

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cinegyan_progress.json")

# =========================================================
# COLOR THEME - Blue / Green / Yellow / Red (professional)
# =========================================================
st.markdown(
    """
    <style>
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        background: linear-gradient(90deg, #2563EB, #10B981);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1rem;
    }
    .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
        background: linear-gradient(90deg, #EF4444, #FACC15);
        color: #1E293B;
    }
    div[data-baseweb="select"] > div {
        border-color: #2563EB !important;
        border-radius: 8px;
    }
    .cg-stat {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        margin-bottom: 12px;
        border: 1px solid #E2E8F0;
        color: #1E293B !important;
    }
    .cg-stat b, .cg-stat span {
        color: #1E293B !important;
    }
    .cg-side-badge {
        background: #F8FAFC;
        border-left: 4px solid #2563EB;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: 0.85rem;
        color: #1E293B !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# LOCAL PROGRESS STORAGE (points / streak / quiz scores)
# Note: on Streamlit Community Cloud the filesystem resets on redeploy,
# so this persists locally but not permanently once deployed.
# =========================================================
DEFAULT_PROGRESS = {"points": 0, "streak_current": 0, "streak_longest": 0, "last_active": None, "quiz_best": {}}

def load_progress():
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = DEFAULT_PROGRESS.copy()
            merged.update(data)
            return merged
    except Exception:
        return DEFAULT_PROGRESS.copy()

def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f)
    except Exception:
        pass

def bump_streak(progress):
    today = datetime.date.today().isoformat()
    if progress.get("last_active") == today:
        return progress  # already counted today
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if progress.get("last_active") == yesterday:
        progress["streak_current"] = progress.get("streak_current", 0) + 1
    else:
        progress["streak_current"] = 1
    progress["streak_longest"] = max(progress.get("streak_longest", 0), progress["streak_current"])
    progress["last_active"] = today
    return progress

def build_google_calendar_url(title, details, hour, minute, recur_daily=True):
    now = datetime.datetime.now()
    start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if start < now:
        start += datetime.timedelta(days=1)
    end = start + datetime.timedelta(minutes=30)
    fmt = "%Y%m%dT%H%M%S"
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start.strftime(fmt)}/{end.strftime(fmt)}",
        "details": details,
    }
    url = "https://calendar.google.com/calendar/render?" + urlencode(params)
    if recur_daily:
        url += "&recur=RRULE:FREQ=DAILY"
    return url

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# =========================================================
# API KEY HANDLING (robust — never crashes the app)
# =========================================================
API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        API_KEY = ""

if not API_KEY:
    API_KEY = st.sidebar.text_input("Enter your Gemini API Key", type="password")
    st.sidebar.caption("Get a free key at aistudio.google.com/apikey")

client = None
client_error = None
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        client_error = str(e)

# =========================================================
# SESSION STATE DEFAULTS
# =========================================================
for key, default in [
    ("logged_in", False),
    ("student_name", ""),
    ("student_roll", ""),
    ("content", ""),
    ("quiz_data", None),
    ("quiz_submitted", False),
    ("last_topic_key", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =========================================================
# HERO HEADER (always visible)
# =========================================================
st.markdown(
    """
    <div style="text-align:center; padding: 10px 0 10px 0;">
        <h1 style="font-size:2.8rem; margin-bottom:0;">
            <span style="color:#2563EB;">Cine</span><span style="color:#10B981;">G</span><span style="color:#FACC15;">y</span><span style="color:#EF4444;">an</span> 🎬
        </h1>
        <p style="font-size:1.05rem; color:#64748B; margin-top:6px;">
            AI-powered learning for engineering, management &amp; professional students —
            any subject, any Indian language, told your way.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SIMPLE NAME-BASED LOGIN (no password — just personalization)
# =========================================================
if not st.session_state.logged_in:
    st.caption("Built for MCA · MBA · MTech · BTech and every serious learner.")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form"):
            st.markdown("#### 👋 Welcome! Tell us a bit about you to start learning")
            name = st.text_input("Your Name", placeholder="e.g. Gayathri")
            roll = st.text_input("Roll No. / ID (optional)", placeholder="e.g. 21A91A0512")
            start = st.form_submit_button("🚀 Start Learning", use_container_width=True)
        if start:
            if name.strip():
                st.session_state.logged_in = True
                st.session_state.student_name = name.strip()
                st.session_state.student_roll = roll.strip()
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")
    st.stop()

# =========================================================
# 3-COLUMN PROFESSIONAL LAYOUT (left: features, center: app, right: stats)
# =========================================================
left_col, center_col, right_col = st.columns([1, 2.4, 1])

# ---------------------------------------------------------
# LEFT COLUMN — engaging feature badges
# ---------------------------------------------------------
with left_col:
    st.markdown("#### ✨ Why CineGyan")
    feature_badges = [
        ("🎬", "Movie-style storytelling"),
        ("🌐", "12 Indian languages"),
        ("🎓", "MCA · MBA · MTech · BTech"),
        ("🧠", "AI-scored quiz contests"),
        ("🔥", "Daily learning streaks"),
        ("📅", "Calendar study reminders"),
    ]
    for icon, label in feature_badges:
        st.markdown(f'<div class="cg-side-badge">{icon} &nbsp; {label}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# RIGHT COLUMN — points, streak, calendar scheduling
# ---------------------------------------------------------
with right_col:
    st.markdown("#### 📊 Your Progress")
    p = st.session_state.progress
    st.markdown(f'<div class="cg-stat">🔥<br><b style="font-size:1.4rem;">{p["streak_current"]}</b><br><span style="font-size:0.75rem;color:#64748B;">Day streak</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cg-stat">🏆<br><b style="font-size:1.4rem;">{p["points"]}</b><br><span style="font-size:0.75rem;color:#64748B;">Total points</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cg-stat">📈<br><b style="font-size:1.4rem;">{p["streak_longest"]}</b><br><span style="font-size:0.75rem;color:#64748B;">Longest streak</span></div>', unsafe_allow_html=True)

    st.markdown("#### 📅 Study Reminder")
    reminder_time = st.time_input("Daily reminder time", value=datetime.time(19, 0))
    recur_daily = st.checkbox("Repeat daily", value=True)
    cal_url = build_google_calendar_url(
        "CineGyan — Daily Learning Session",
        f"Keep your streak alive! Current streak: {p['streak_current']} day(s).",
        reminder_time.hour, reminder_time.minute, recur_daily,
    )
    st.link_button("➕ Add to Google Calendar", cal_url, use_container_width=True)

# ---------------------------------------------------------
# CENTER COLUMN — the actual app
# ---------------------------------------------------------
with center_col:
    colW, colL = st.columns([4, 1])
    with colW:
        st.success(f"Welcome, {st.session_state.student_name}! 🎓 Ready to learn something new?")
    with colL:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.student_name = ""
            st.session_state.student_roll = ""
            st.session_state.content = ""
            st.session_state.quiz_data = None
            st.session_state.quiz_submitted = False
            st.rerun()

    if client_error:
        st.error(f"There's a problem with the API key: {client_error}\n\nDouble-check the key at aistudio.google.com/apikey — it should start with 'AIzaSy'.")

    STREAMS = [
        "General Learning", "BTech / Engineering", "MTech / Advanced Engineering",
        "MCA / Computer Applications", "Computer Science / IT", "MBA / Business Management",
        "Commerce & Finance", "Law", "Medical & Healthcare", "Psychology", "Science",
        "Economics", "Arts & Literature", "Civil Services / Public Administration",
    ]
    stream = st.selectbox("🎓 Academic / Professional Stream", STREAMS)

    TEMPLATES = ["Movie Story", "Case Study", "Student Notes", "Presentation Outline"]
    template = st.selectbox("📋 Learning Template", TEMPLATES)

    c1, c2 = st.columns(2)
    with c1:
        language = st.selectbox(
            "🗣️ Language",
            [
                "English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam",
                "Marathi", "Bengali", "Gujarati", "Punjabi", "Odia", "Urdu",
            ],
        )
    with c2:
        genre = st.selectbox(
            "🎭 Movie Genre / Mood (used for Movie Story template)",
            [
                "Action", "Comedy", "Thriller", "Sci-Fi", "Emotional Drama",
                "Mythology", "Mystery", "Romance", "Adventure", "Motivational",
            ],
        )

    topic = st.text_input("📚 Enter your topic", placeholder="e.g. Data Structures, Marketing Mix, Contract Law, Thermodynamics")

    topic_key = f"{topic.strip().lower()}|{template}"
    best_pct = st.session_state.progress["quiz_best"].get(topic_key)
    if best_pct is not None:
        st.caption(f"📌 Your best quiz score on this topic + template: {best_pct}%")

    generate = st.button("✨ Generate", type="primary", use_container_width=True)

    QUALITY_RULES = """
Writing quality rules (very important):
- Use very simple, everyday words — write for someone learning this topic for the first time.
- Prefer short sentences over long, complicated ones.
- Include at least one small, concrete real-world example inside the content.
- Stay 100% factually accurate — never sacrifice correctness for style.
- Avoid unnecessary jargon; if a technical term is required, explain it in 3-5 simple words right after it.
"""

    TEMPLATE_PROMPTS = {
        "Movie Story": """
You are an AI educational storyteller for {stream} students.
Convert the topic into a cinematic explanation, written entirely in {language}.
""" + QUALITY_RULES + """
Structure (keep these exact section headers, translated into {language}, keep emoji):
🎬 Movie Title
🎭 Characters
🌍 Background / Setting
📖 Story Beginning
🔥 Conflict
⏸ Interval Twist
⚔ Climax
🎓 Learning Summary (2-4 bullet points)

Make it engaging in the {genre} genre/mood. Keep it 350-450 words, end with the Learning Summary.

Topic: {topic}
""",
        "Case Study": """
You are an AI case-study writer for {stream} students. Write entirely in {language}.
""" + QUALITY_RULES + """
Structure (keep these exact section headers, translated into {language}):
📌 Background
❗ Problem Statement
👥 Stakeholders
⚠️ Challenges
🧭 Decision Making / Analysis
💡 Concept Explanation (explain "{topic}" clearly using this case)
🔄 Alternative Solutions
🎓 Lessons Learned
❓ Discussion Questions (2-3)

Keep it practical and 350-450 words.

Topic: {topic}
""",
        "Student Notes": """
You are an AI note-maker for {stream} students preparing for exams. Write entirely in {language}.
""" + QUALITY_RULES + """
Structure (keep these exact section headers, translated into {language}):
📝 Concise Definition
🔑 Key Points (bullet list, 4-6 points)
💡 Example
🗂️ Flashcard (Q&A format, 3 pairs)
⚠️ Common Mistakes / Exam Tips

Keep it crisp and easy to revise quickly.

Topic: {topic}
""",
        "Presentation Outline": """
You are an AI presentation designer for {stream} students. Write entirely in {language}.
""" + QUALITY_RULES + """
Structure as slide-by-slide outline (keep these exact section headers, translated into {language}):
🖼️ Slide 1: Title
📋 Slide 2: Agenda
📖 Slide 3: Concept Introduction
🔍 Slide 4: Deep Dive / How it works
🌍 Slide 5: Real-world Applications
✅ Slide 6: Conclusion & Key Takeaways

Each slide: a title line + 3-4 crisp bullet points, presentation-ready.

Topic: {topic}
""",
    }

    QUIZ_PROMPT = """
Based on the following educational content for a {stream} student, write entirely in {language}.
Create exactly 5 multiple-choice questions testing understanding of the topic "{topic}".

Respond with ONLY valid JSON — no markdown, no backticks, no extra text before or after.
Use exactly this structure:
[
  {{
    "question": "question text here",
    "options": ["option A text", "option B text", "option C text", "option D text"],
    "answer_index": 0
  }}
]
"answer_index" is the 0-based index (0,1,2,3) of the correct option in "options".

Content to base the quiz on:
{content}
"""

    if generate:
        if not API_KEY:
            st.error("Please enter your Gemini API key in the sidebar first.")
        elif client_error:
            st.error("Fix the API key issue above before generating.")
        elif not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner(f"Generating your {template} on {topic}... 🎥"):
                try:
                    prompt = TEMPLATE_PROMPTS[template].format(
                        stream=stream, language=language, genre=genre, topic=topic
                    )
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                    )
                    st.session_state.content = response.text
                    st.session_state.quiz_data = None
                    st.session_state.quiz_submitted = False
                    st.session_state.last_topic_key = topic_key
                    st.session_state.progress = bump_streak(st.session_state.progress)
                    save_progress(st.session_state.progress)
                except Exception as e:
                    st.error(
                        f"Generation failed: {e}\n\n"
                        "Common causes: invalid API key, no internet, or the Gemini API "
                        "quota/rate limit was hit. Try again in a few seconds."
                    )

    if st.session_state.content:
        st.markdown("---")
        st.markdown(st.session_state.content)
        st.markdown("---")

        colA, colB = st.columns(2)
        with colA:
            st.download_button(
                label="⬇️ Download content",
                data=st.session_state.content,
                file_name=f"{topic.replace(' ', '_')}_{template.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with colB:
            make_quiz = st.button("🧠 Start Quiz Contest (5 MCQs)", use_container_width=True)

        if make_quiz:
            with st.spinner("Writing your quiz..."):
                try:
                    qprompt = QUIZ_PROMPT.format(
                        stream=stream, language=language, topic=topic,
                        content=st.session_state.content,
                    )
                    qresponse = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=qprompt,
                    )
                    raw = qresponse.text.strip()
                    raw = re.sub(r"^```(json)?", "", raw).strip()
                    raw = re.sub(r"```$", "", raw).strip()
                    st.session_state.quiz_data = json.loads(raw)
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_points_awarded = False
                except Exception as e:
                    st.error(f"Quiz generation failed: {e}")

        if st.session_state.quiz_data:
            st.markdown("### 🧠 Quiz Contest")
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_data):
                    st.markdown(f"**Q{i+1}. {q['question']}**")
                    st.radio(
                        f"quiz_q_{i}",
                        options=list(range(len(q["options"]))),
                        format_func=lambda idx, opts=q["options"]: opts[idx],
                        key=f"quiz_radio_{i}",
                        label_visibility="collapsed",
                    )
                submit_quiz = st.form_submit_button("✅ Submit Quiz", use_container_width=True)

            if submit_quiz:
                st.session_state.quiz_submitted = True

            if st.session_state.quiz_submitted:
                score = 0
                st.markdown("#### 📊 Results")
                for i, q in enumerate(st.session_state.quiz_data):
                    correct_idx = q["answer_index"]
                    user_idx = st.session_state.get(f"quiz_radio_{i}")
                    is_correct = user_idx == correct_idx
                    if is_correct:
                        score += 1
                        st.markdown(f"✅ Q{i+1}: Correct! ({q['options'][correct_idx]})")
                    else:
                        st.markdown(
                            f"❌ Q{i+1}: Your answer — {q['options'][user_idx]}. "
                            f"Correct answer — **{q['options'][correct_idx]}**"
                        )
                total_q = len(st.session_state.quiz_data)
                pct = round((score / total_q) * 100)
                st.success(f"🏆 {st.session_state.student_name}, you scored {score}/{total_q} ({pct}%)!")

                # Update points, streak, and per-topic best score (once per submit)
                if not st.session_state.get("quiz_points_awarded"):
                    prog = st.session_state.progress
                    prog["points"] = prog.get("points", 0) + score * 10
                    prog = bump_streak(prog)
                    prev_best = prog["quiz_best"].get(st.session_state.last_topic_key, 0)
                    prog["quiz_best"][st.session_state.last_topic_key] = max(prev_best, pct)
                    st.session_state.progress = prog
                    save_progress(prog)
                    st.session_state.quiz_points_awarded = True

        else:
            st.session_state.quiz_points_awarded = False

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;">
        <span style="background:#DBEAFE; color:#2563EB; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:600; margin-right:6px;">MCA</span>
        <span style="background:#D1FAE5; color:#10B981; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:600; margin-right:6px;">MBA</span>
        <span style="background:#FEF9C3; color:#A16207; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:600; margin-right:6px;">MTech</span>
        <span style="background:#FEE2E2; color:#EF4444; padding:3px 10px; border-radius:999px; font-size:0.75rem; font-weight:600;">BTech</span>
    </div>
    <p style="text-align:center; color:#94A3B8; font-size:0.85rem; margin-top:10px;">
        Built for GDG Hackathon · CineGyan · Powered by Gemini AI
    </p>
    """,
    unsafe_allow_html=True,
)
