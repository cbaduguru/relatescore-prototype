import streamlit as st

# --------------------------------------------
# RelateScore Streamlit Prototype (Cloud-ready)
# --------------------------------------------

BRAND = {
    "name": "RelateScore™",
    "mission": "RelateScore™ provides private relational clarity that supports growth without judgment or exposure.",
    "primary": "#2E6AF3",
    "mint": "#A6E3DA",
    "charcoal": "#1A1A1A",
    "soft": "#F5F5F5",
    "danger": "#E54646",
}

st.set_page_config(page_title="RelateScore Prototype", page_icon="💙", layout="centered")

# Lightweight branding + layout polish
st.markdown(
    f"""
    <style>
      :root {{
        --rs-primary: {BRAND["primary"]};
        --rs-mint: {BRAND["mint"]};
        --rs-charcoal: {BRAND["charcoal"]};
        --rs-soft: {BRAND["soft"]};
        --rs-danger: {BRAND["danger"]};
      }}
      .stApp {{
        background: var(--rs-soft);
      }}
      .rs-card {{
        background: #fff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
      }}
      .rs-badge {{
        display: inline-block;
        font-size: 0.8rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: rgba(46,106,243,0.10);
        color: var(--rs-primary);
        border: 1px solid rgba(46,106,243,0.15);
      }}
      .rs-footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: rgba(245,245,245,0.92);
        border-top: 1px solid rgba(0,0,0,0.06);
        padding: 10px 0;
        z-index: 999;
        backdrop-filter: blur(6px);
      }}
      .rs-footer-inner {{
        max-width: 820px;
        margin: 0 auto;
        padding: 0 1rem;
        font-size: 0.85rem;
        color: rgba(26,26,26,0.70);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
      }}
      .rs-footer a {{
        color: var(--rs-primary);
        text-decoration: none;
      }}
      .rs-footer a:hover {{
        text-decoration: underline;
      }}
      /* Ensure content isn't hidden behind footer */
      .block-container {{
        padding-bottom: 4.5rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Session state
# -----------------------
def init_state():
    if "screen" not in st.session_state:
        st.session_state.screen = "onboarding1"
    if "assessment_progress" not in st.session_state:
        st.session_state.assessment_progress = 0
    if "questions" not in st.session_state:
        # Mirrors the pygame version but can be expanded later
        st.session_state.questions = [
            "How often do you communicate openly?",
            "How do you handle conflict?",
            "Rate your empathy level.",
        ]
    if "answers" not in st.session_state:
        st.session_state.answers = [0] * len(st.session_state.questions)  # 0 = unanswered, else 1–5
    if "insights" not in st.session_state:
        st.session_state.insights = [
            "Strength: Open Communication",
            "Blind Spot: Conflict Avoidance",
            "Pattern: Secure Attachment",
        ]
    if "rgi_score" not in st.session_state:
        st.session_state.rgi_score = 75
    if "logo_bytes" not in st.session_state:
        st.session_state.logo_bytes = None

init_state()

# Handy aliases
screen = st.session_state.screen
questions = st.session_state.questions
answers = st.session_state.answers
insights = st.session_state.insights


# -----------------------
# Helpers
# -----------------------
def go_to(name: str):
    st.session_state.screen = name

def reset_assessment():
    st.session_state.assessment_progress = 0
    st.session_state.answers = [0] * len(st.session_state.questions)

def compute_rgi():
    total = sum(st.session_state.answers)
    max_possible = len(st.session_state.answers) * 5 or 1
    st.session_state.rgi_score = int((total / max_possible) * 100)

def card_start():
    st.markdown("<div class='rs-card'>", unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def header(title: str, subtitle: str | None = None):
    cols = st.columns([1, 6])
    with cols[0]:
        if st.session_state.logo_bytes:
            st.image(st.session_state.logo_bytes, use_container_width=True)
        else:
            st.markdown("<div class='rs-badge'>Logo Slot</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<h2 style='margin-bottom:0.2rem;'>{title}</h2>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<p style='color:rgba(26,26,26,0.70); margin-top:0;'>{subtitle}</p>", unsafe_allow_html=True)
    st.divider()

def rq_wheel():
    score = st.session_state.rgi_score
    st.progress(score / 100)
    st.caption(f"Relationship Growth Index (RGI): **{score} / 100**")

def footer():
    st.markdown(
        f"""
        <div class="rs-footer">
          <div class="rs-footer-inner">
            <div><strong>{BRAND["name"]}</strong> — {BRAND["mission"]}</div>
            <div>
              <span>Prototype</span> ·
              <a href="#" onclick="return false;">Privacy</a> ·
              <a href="#" onclick="return false;">Terms</a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------
# Sidebar (logo + nav)
# -----------------------
with st.sidebar:
    st.markdown(f"### {BRAND['name']}")
    st.caption(BRAND["mission"])

    uploaded_logo = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], help="Optional: upload a logo for the header.")
    if uploaded_logo is not None:
        st.session_state.logo_bytes = uploaded_logo.getvalue()

    if st.session_state.logo_bytes:
        st.image(st.session_state.logo_bytes, use_container_width=True)

    st.divider()
    st.markdown("**Quick navigation**")
    nav = st.radio(
        "Go to",
        options=["Onboarding", "Assessment", "Insights", "Dashboard"],
        label_visibility="collapsed",
    )
    if nav == "Onboarding":
        go_to("onboarding1")
    elif nav == "Assessment":
        go_to("assessment_intro")
    elif nav == "Insights":
        go_to("insights_summary")
    elif nav == "Dashboard":
        go_to("dashboard")

# -----------------------
# Screens (mirrors pygame flow)
# -----------------------
def onboarding1():
    header(BRAND["name"], "Your relationships deserve clarity without exposure.")
    card_start()
    st.write("Insights stay private. No sharing. No judgment.")
    st.info("All insights stay private unless you choose to share them.")
    card_end()

    if st.button("Continue", type="primary"):
        go_to("onboarding2")

def onboarding2():
    header("Privacy Commitment", "Only you can see your results.")
    card_start()
    st.write(
        "• Your answers are used only to generate your personal insights.\n"
        "• No partner/friend/third party can see your dashboard unless you show them.\n"
        "• You can erase your session data at any time."
    )
    card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            go_to("onboarding1")
    with c2:
        if st.button("Continue", type="primary"):
            go_to("onboarding3")

def onboarding3():
    header("Science-backed clarity", "Identify strengths, blind spots, and growth opportunities.")
    card_start()
    st.write(
        "You’ll take a short assessment and receive a private dashboard view.\n\n"
        "This is a prototype experience meant to demonstrate flow and UI."
    )
    card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            go_to("onboarding2")
    with c2:
        if st.button("Begin Assessment", type="primary"):
            reset_assessment()
            go_to("assessment_intro")

def assessment_intro():
    header("Assessment Intro", "Answer with honesty — there are no right or wrong responses.")
    card_start()
    st.write("Use the 1–5 scale (1 = low/rarely, 5 = high/often).")
    card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            go_to("onboarding3")
    with c2:
        if st.button("Start", type="primary"):
            go_to("question")

def question():
    idx = st.session_state.assessment_progress
    total = len(questions)

    if idx >= total:
        go_to("completion")
        return

    header("RelateScore Assessment", f"Progress: {idx + 1}/{total}")
    card_start()
    st.write(f"**{questions[idx]}**")

    current = answers[idx]
    choice = st.radio(
        "Select a response:",
        options=[1, 2, 3, 4, 5],
        index=current - 1 if current in [1,2,3,4,5] else 2,
        horizontal=True,
    )
    answers[idx] = choice

    st.progress(idx / total)
    card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            if idx == 0:
                go_to("assessment_intro")
            else:
                st.session_state.assessment_progress -= 1
    with c2:
        label = "Next" if idx < total - 1 else "Finish"
        if st.button(label, type="primary"):
            if idx < total - 1:
                st.session_state.assessment_progress += 1
            else:
                go_to("completion")

def completion():
    header("Completion", "Great job — your responses are ready for analysis.")
    compute_rgi()

    card_start()
    st.success("Assessment complete. Your score is ready.")
    rq_wheel()
    card_end()

    if st.button("View Insights", type="primary"):
        go_to("insights_summary")

def insights_summary():
    header("Insights Summary", "Your strengths, blind spots, and patterns.")
    card_start()
    rq_wheel()
    st.subheader("Top Insights")
    for i, insight in enumerate(insights, start=1):
        st.markdown(f"**{i}. {insight}**")
    card_end()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Back"):
            go_to("completion")
    with c2:
        if st.button("View Detail"):
            go_to("pattern_detail")
    with c3:
        if st.button("Go to Dashboard", type="primary"):
            go_to("dashboard")

def pattern_detail():
    header("Pattern Detail", "Example: Open Communication")
    card_start()
    st.write("Behaviors: Frequent check-ins, honest feedback.")
    st.write("Suggestions: Continue building on this strength.")
    card_end()

    if st.button("Back to Insights"):
        go_to("insights_summary")

def dashboard():
    header("Dashboard", "Private relational clarity hub.")
    card_start()
    rq_wheel()
    st.write("**Top Insights:**")
    for insight in insights[:3]:
        st.markdown(f"- {insight}")
    st.write("**Daily Reflection:** Take a moment to reflect...")
    card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Retake Assessment"):
            reset_assessment()
            go_to("assessment_intro")
    with c2:
        if st.button("Withdraw Consent (Reset)", type="primary"):
            reset_assessment()
            st.session_state.rgi_score = 0
            go_to("empty_dashboard")

def empty_dashboard():
    header("Empty Dashboard", "Complete your first assessment to unlock insights.")
    card_start()
    st.info("Your prior session data has been cleared.")
    card_end()

    if st.button("Start Assessment", type="primary"):
        go_to("assessment_intro")


# -----------------------
# Router
# -----------------------
if screen == "onboarding1":
    onboarding1()
elif screen == "onboarding2":
    onboarding2()
elif screen == "onboarding3":
    onboarding3()
elif screen == "assessment_intro":
    assessment_intro()
elif screen == "question":
    question()
elif screen == "completion":
    completion()
elif screen == "insights_summary":
    insights_summary()
elif screen == "pattern_detail":
    pattern_detail()
elif screen == "dashboard":
    dashboard()
elif screen == "empty_dashboard":
    empty_dashboard()
else:
    go_to("onboarding1")
    onboarding1()

footer()
