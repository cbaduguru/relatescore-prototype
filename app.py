
# app_rqwheel_color_index.py
# RelateScore™ — RQ Wheel with category-indexed colors and score-scaled intensity

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="RelateScore™", page_icon="✅", layout="centered")

CATEGORIES = [
    "Emotional Awareness",
    "Communication Style",
    "Conflict Tendencies",
    "Attachment Patterns",
    "Empathy & Responsiveness",
    "Self-Insight",
    "Trust & Boundaries",
    "Stability & Consistency"
]

CATEGORY_COLORS = {
    "Emotional Awareness": "#4A90E2",
    "Communication Style": "#7ED321",
    "Conflict Tendencies": "#FF6B6B",
    "Attachment Patterns": "#A29BFE",
    "Empathy & Responsiveness": "#FFD700",
    "Self-Insight": "#5A67D8",
    "Trust & Boundaries": "#20C997",
    "Stability & Consistency": "#A1887F",
}

def draw_rq_wheel(scores):
    values = np.array([scores[c] for c in CATEGORIES])
    angles = np.linspace(0, 2 * np.pi, len(CATEGORIES), endpoint=False)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#FAF7F2")
    ax.set_facecolor("#FAF7F2")

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles)
    ax.set_xticklabels(CATEGORIES, fontsize=10, fontweight="bold")
    ax.set_yticklabels([])
    ax.grid(color="#C9A96E", linewidth=0.6, alpha=0.6)

    for i, cat in enumerate(CATEGORIES):
        start = angles[i]
        end = angles[(i + 1) % len(CATEGORIES)]
        score = scores[cat]
        alpha = 0.25 + (0.55 * (score / 100))

        ax.fill([start, end, end, start], [0, 0, score, score],
                color=CATEGORY_COLORS[cat], alpha=alpha)

        ax.plot([start, end], [score, score],
                color=CATEGORY_COLORS[cat], linewidth=2)

    return fig

def dashboard_page():
    st.header("Dashboard")

    scores = {
        "Emotional Awareness": 78,
        "Communication Style": 72,
        "Conflict Tendencies": 65,
        "Attachment Patterns": 70,
        "Empathy & Responsiveness": 82,
        "Self-Insight": 75,
        "Trust & Boundaries": 68,
        "Stability & Consistency": 74,
    }

    fig = draw_rq_wheel(scores)
    st.pyplot(fig)

dashboard_page()
