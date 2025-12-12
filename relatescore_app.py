import streamlit as st

# --------------------------------------------------
# BRANDING
# --------------------------------------------------
BRAND = {
    "name": "RelateScore™",
    "tagline": "Private relational clarity that supports growth without judgment or exposure.",
    "primary": "#2E6AF3",     # ACCENT_BLUE
    "mint": "#A6E3DA",
    "charcoal": "#1A1A1A",
    "soft_gray": "#F5F5F5",
    "error_red": "#E54646",
}

st.set_page_config(
    page_title="RelateScore Prototype",
    page_icon="💙",
    layout="centered",
)

# Minimal CSS skin
st.markdown(
    f"""
    <style>
      :root {{
        --rs-primary: {BRAND["primary"]};
        --rs-mint: {BRAND["mint"]};
        --rs-charcoal: {BRAND["charcoal"]};
        --rs-soft: {BRAND["soft_gray"]};
        --rs-danger: {BRAND["error_red"]};
      }}
      .stApp {{
        background: var(--rs-soft);
      }}
      h1, h2, h3, h4, h5, h6, p, li {{
        color: var(--rs-charcoal);
      }}
      /* Primary buttons */
      .stButton > button {{
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.06);
        padding: 0.55rem 1rem;
      }}
      /* Streamlit primary buttons */
      .stButton > button[kind="primary"] {{
        background: var(--rs-primary);
        border: 1px solid var(--rs-primary);
        color: white;
      }}
      /* Cards */
      .rs-card {{
        background: white;
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
      /* Footer (sticky) */
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
      /* Add padding so content doesn't hide behind sticky footer */
      .block-container {{
        padding-bottom: 4.5rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SESSION STATE SETUP
# --------------------------------------------------
def init_state():
    if "screen" not in st.session_state:
        st.session_state.screen = "onboarding1"
    if "assessment_progress" not in st.session_state:
        st.session_state.assessment_progress = 0
    if "questions" not in st.session_state:
        st.session_state.questions = [
            "How often do you communicate openly?",
            "How do you handle conflict in close relationships?",
            "How accurately do you believe you understand others’ emotions?",
        ]
    if "answers" not in st.session_state:
        st.session_state.answers = [0] * len(st.session_state.questions)  # 1–5 Likert scale; 0 = unanswered
    if "insights" not in st.session_state:
        st.session_state.insights = [
            "Strength: Open Communication",
            "Blind Spot: Conflict Avoidance",
            "Pattern: Secure Attachment Tendencies",
        ]
    if "rgi_score" not in st.session_state:
        st.session_state.rgi_score = 75  # starting placeholder
    if "logo_bytes" not in st.session_state:
        st.session_state.logo_bytes = None


init_state()

# Convenience handles
screen = st.session_state.screen
questions = st.session_state.questions
answers = st.session_state.answers
insights = st.session_state.insights

# --------------------------------------------------
# SIDEBAR: LOGO SLOT + NAV (OPTIONAL)
# --------------------------------------------------
with st.sidebar:
    st.markdown(f"### {BRAND['name']}")
    st.caption(BRAND["tagline"])

    uploaded_logo = st.file_uploader("Logo (PNG/JPG)", type=["png", "jpg", "jpeg"], help="Optional. Upload a logo to display in the header.")
    if uploaded_logo is not None:
        st.session_state.logo_bytes = uploaded_logo.getvalue()

    if st.session_state.logo_bytes:
        st.image(st.session_state.logo_bytes, use_container_width=True)

    st.divider()
    st.markdown("**Quick navigation**")
    nav = st.radio(
        "Go to",
        options=[
            "Onboarding",
            "Assessment",
            "Insights",
            "Dashboard",
        ],
        label_visibility="collapsed",
    )

    if nav == "Onboarding":
        st.session_state.screen = "onboarding1"
    elif nav == "Assessment":
        st.session_state.screen = "assessment_intro"
    elif nav == "Insights":
        st.session_state.screen = "insights_summary"
    elif nav == "Dashboard":
        st.session_state.screen = "dashboard"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def compute_rgi_score():
    total = sum(st.session_state.answers)
    max_possible = len(st.session_state.answers) * 5 or 1
    st.session_state.rgi_score = int((total / max_possible) * 100)


def go_to(next_screen: str):
    st.session_state.screen = next_screen


def reset_assessment():
    st.session_state.assessment_progress = 0
    st.session_state.answers = [0] * len(st.session_state.questions)


def header_block(title: str, subtitle: str | None = None):
    # Logo slot (top of main content)
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


def rs_card_start():
    st.markdown("<div class='rs-card'>", unsafe_allow_html=True)


def rs_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def rq_wheel():
    score = st.session_state.rgi_score
    st.progress(score / 100)
    st.caption(f"Relationship Growth Index (RGI): **{score} / 100**")


def footer():
    st.markdown(
        f"""
        <div class="rs-footer">
          <div class="rs-footer-inner">
            <div>
              <strong>{BRAND["name"]}</strong> — {BRAND["tagline"]}
            </div>
            <div>
              <span>Prototype build</span> ·
              <a href="#" onclick="return false;">Privacy</a> ·
              <a href="#" onclick="return false;">Terms</a>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SCREENS
# --------------------------------------------------
def screen_onboarding1():
    header_block(BRAND["name"], "Your relationships deserve clarity without exposure.")
    rs_card_start()
    st.write(
        "RelateScore gives you a private, science-informed snapshot of your relational patterns. "
        "No sharing, no judgment — just clarity."
    )
    st.info("All insights stay private unless you choose to share them.")
    rs_card_end()

    if st.button("Continue", type="primary"):
        go_to("onboarding2")


def screen_onboarding2():
    header_block("Privacy Commitment", "Insights stay private. Full stop.")
    rs_card_start()
    st.write(
        "• Your answers are used only to generate your personal insights.\n"
        "• No one else can see your dashboard unless you show them.\n"
        "• You can erase your data at any time with **Withdraw & Reset**."
    )
    rs_card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            go_to("onboarding1")
    with c2:
        if st.button("Continue", type="primary"):
            go_to("onboarding3")


def screen_onboarding3():
    header_block("What You’ll Get", "Science-backed clarity, not judgment.")
    rs_card_start()
    st.write(
        "- A quick, structured assessment about how you show up in close relationships.\n"
        "- A private dashboard showing strengths, blind spots, and growth edges.\n"
        "- A Relationship Growth Index (RGI) score you can track over time."
    )
    st.success("This is not a diagnosis. It’s a reflection tool.")
    rs_card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            go_to("onboarding2")
    with c2:
        if st.button("Begin Assessment", type="primary"):
            reset_assessment()
            go_to("assessment_intro")


def screen_assessment_intro():
    header_block("Before We Start", "There are no right or wrong responses.")
    rs_card_start()
    st.write(
        "Answer the next few questions as honestly as you can. "
        "Respond based on how you typically behave right now."
    )
    st.markdown(
        """
        **Scale (1–5)**  
        1 – Almost never  
        2 – Rarely  
        3 – Sometimes  
        4 – Often  
        5 – Almost always  
        """
    )
    rs_card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            go_to("onboarding3")
    with c2:
        if st.button("Start Assessment", type="primary"):
            go_to("question")


def screen_question():
    idx = st.session_state.assessment_progress
    total_q = len(questions)

    if idx >= total_q:
        go_to("completion")
        return

    header_block("RelateScore Assessment", f"Question {idx + 1} of {total_q}")

    rs_card_start()
    st.write(f"**{questions[idx]}**")

    current_answer = answers[idx]
    choice = st.radio(
        "Select the option that best fits you:",
        options=[1, 2, 3, 4, 5],
        index=current_answer - 1 if current_answer in [1, 2, 3, 4, 5] else 2,
        horizontal=True,
    )
    answers[idx] = choice

    st.progress(idx / total_q)
    rs_card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back"):
            if idx == 0:
                go_to("assessment_intro")
            else:
                st.session_state.assessment_progress -= 1
    with c2:
        label = "Next" if idx < total_q - 1 else "Finish"
        if st.button(label, type="primary"):
            if idx < total_q - 1:
                st.session_state.assessment_progress += 1
            else:
                go_to("completion")


def screen_completion():
    header_block("Assessment Complete", "Your responses are ready for analysis.")
    compute_rgi_score()

    rs_card_start()
    st.success("Nice work. Your RGI score has been generated from your responses.")
    rq_wheel()
    st.write(
        "Next, you’ll see a summary of key relational patterns: strengths, blind spots, and growth opportunities."
    )
    rs_card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Retake Assessment"):
            reset_assessment()
            go_to("question")
    with c2:
        if st.button("View Insights", type="primary"):
            go_to("insights_summary")


def screen_insights_summary():
    header_block("Insights Summary", "High-level patterns based on your responses.")
    rs_card_start()
    rq_wheel()
    st.subheader("Your Top Signals")
    for i, insight in enumerate(insights, start=1):
        st.markdown(f"**{i}. {insight}**")
    st.info("These are directional insights, not permanent labels.")
    rs_card_end()

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


def screen_pattern_detail():
    header_block("Pattern Detail", "Example: Open Communication")
    rs_card_start()
    st.write("### What this pattern suggests")
    st.write(
        "You likely value honesty and directness in your relationships. "
        "When things are going well, you can share needs and boundaries without shutting down."
    )
    st.write("### Behaviors often linked to this pattern")
    st.markdown(
        """
        - You check in when something feels off.  
        - You name tension instead of pretending it isn’t there.  
        - You can receive feedback without becoming overly defensive.
        """
    )
    st.write("### Growth Opportunities")
    st.markdown(
        """
        - Ask one more question before offering advice.  
        - Pair honesty with curiosity: “How did that land for you?”  
        - Notice when you might talk instead of listening.
        """
    )
    rs_card_end()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Back to Insights"):
            go_to("insights_summary")
    with c2:
        if st.button("Go to Dashboard", type="primary"):
            go_to("dashboard")


def screen_dashboard():
    header_block("Dashboard", "Your private relational clarity hub.")
    rs_card_start()
    st.write("### Relationship Growth Index")
    rq_wheel()

    st.write("### Current Highlights")
    for insight in insights[:3]:
        st.markdown(f"- **{insight}**")

    st.write("### Daily Reflection Prompt")
    st.markdown(
        "> Think of one interaction in the last 24 hours that mattered.\n"
        "> What did you do that moved it closer to (or farther from) the relationship you want?"
    )
    rs_card_end()

    st.subheader("Data & Consent Controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("View Insights Again"):
            go_to("insights_summary")
    with c2:
        if st.button("Retake Assessment"):
            reset_assessment()
            go_to("assessment_intro")
    with c3:
        if st.button("Withdraw & Reset", type="primary"):
            reset_assessment()
            st.session_state.rgi_score = 0
            go_to("empty_dashboard")


def screen_empty_dashboard():
    header_block("Dashboard Reset", "Your previous responses have been cleared.")
    rs_card_start()
    st.warning(
        "You’ve withdrawn consent and reset your RelateScore data. "
        "No previous answers or scores are retained in this session."
    )
    st.write("When you’re ready, complete the assessment again to generate fresh insights.")
    rs_card_end()

    if st.button("Start New Assessment", type="primary"):
        reset_assessment()
        go_to("assessment_intro")


# --------------------------------------------------
# ROUTER
# --------------------------------------------------
if screen == "onboarding1":
    screen_onboarding1()
elif screen == "onboarding2":
    screen_onboarding2()
elif screen == "onboarding3":
    screen_onboarding3()
elif screen == "assessment_intro":
    screen_assessment_intro()
elif screen == "question":
    screen_question()
elif screen == "completion":
    screen_completion()
elif screen == "insights_summary":
    screen_insights_summary()
elif screen == "pattern_detail":
    screen_pattern_detail()
elif screen == "dashboard":
    screen_dashboard()
elif screen == "empty_dashboard":
    screen_empty_dashboard()
else:
    go_to("onboarding1")
    screen_onboarding1()

# Sticky footer
footer()
