import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components  # <-- NEW

APP_NAME = "RelateScore™ Prototype"
MISSION = "RelateScore™ provides private relational clarity that supports growth without judgment or exposure."

DATA_DIR = ".data"
INVITES_PATH = os.path.join(DATA_DIR, "invites.json")


# -----------------------------
# Storage helpers (JSON file)
# -----------------------------
def _ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(INVITES_PATH):
        with open(INVITES_PATH, "w", encoding="utf-8") as f:
            json.dump({"invites": {}}, f, indent=2)


def _load_store() -> Dict[str, Any]:
    _ensure_storage()
    with open(INVITES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_store(store: Dict[str, Any]) -> None:
    _ensure_storage()
    tmp = INVITES_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)
    os.replace(tmp, INVITES_PATH)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# -----------------------------
# Invite & user identity
# -----------------------------
def _rand_code(n: int = 6) -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    import secrets
    return "".join(secrets.choice(alphabet) for _ in range(n))


def get_or_create_user_id() -> str:
    if "user_id" not in st.session_state:
        import secrets
        st.session_state.user_id = secrets.token_hex(8)
    return st.session_state.user_id


# -----------------------------
# Safety / Toxicity filter (prototype heuristic)
# -----------------------------
BANNED_PATTERNS = [
    r"\bkill\b", r"\bdie\b", r"\bworthless\b", r"\bhate you\b", r"\bshut up\b",
    r"\bstupid\b", r"\bidiot\b", r"\bslut\b", r"\bbitch\b", r"\basshole\b",
]


def toxicity_score(text: str) -> float:
    if not text:
        return 0.0
    t = text.lower()
    hits = sum(1 for p in BANNED_PATTERNS if re.search(p, t))
    caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
    return min(1.0, 0.18 * hits + 0.3 * max(0.0, caps_ratio - 0.25))


def enforce_toxicity_gate(texts: List[str], threshold: float = 0.55) -> Tuple[bool, float]:
    score = max(toxicity_score(t) for t in texts)
    return (score <= threshold), score


# -----------------------------
# Scoring logic (prototype)
# -----------------------------
CATEGORIES = ["Communication", "Empathy", "Reliability", "Conflict Navigation", "Connection"]

DEFAULT_WEIGHTS = {
    "Communication": 0.35,
    "Empathy": 0.20,
    "Reliability": 0.20,
    "Conflict Navigation": 0.15,
    "Connection": 0.10,
}

PROMPTS = [
    "In the past week, what did your partner do that helped you feel supported?",
    "What is one moment you felt misunderstood, and what did you need instead?",
    "What is one small change you can make next week to improve the relationship?",
]

EMPATHY_POS = ["understand", "heard", "care", "empath", "support", "validate", "compassion"]
COMM_POS = ["talk", "discuss", "communicat", "listen", "clarify", "share", "ask"]
REL_POS = ["reliable", "consistent", "follow through", "depend", "trust", "kept", "promise"]
CONN_POS = ["close", "love", "affection", "connect", "bond", "together", "intim"]
CONFLICT_SKILL = ["calm", "repair", "apolog", "resolve", "compromise", "boundary", "respect"]
CONFLICT_NEG = ["always", "never", "ignore", "silent", "yell", "fight", "blame"]


def _keyword_score(text: str, keywords: List[str]) -> float:
    t = (text or "").lower()
    return sum(1 for k in keywords if k in t)


def _len_score(text: str) -> float:
    n = len((text or "").strip())
    return min(1.0, n / 500.0)


def score_categories(effort_1_5: int, answers: List[str], attachment_flags: Dict[str, bool]) -> Dict[str, float]:
    joined = " ".join(answers or [])
    effort = np.clip((effort_1_5 - 1) / 4, 0, 1)  # 0..1

    comm = 0.35 * _len_score(joined) + 0.35 * np.tanh(_keyword_score(joined, COMM_POS) / 3) + 0.30 * effort
    emp  = 0.35 * _len_score(joined) + 0.35 * np.tanh(_keyword_score(joined, EMPATHY_POS) / 3) + 0.30 * effort
    rel  = 0.25 * _len_score(joined) + 0.45 * np.tanh(_keyword_score(joined, REL_POS) / 3) + 0.30 * effort
    conn = 0.25 * _len_score(joined) + 0.45 * np.tanh(_keyword_score(joined, CONN_POS) / 3) + 0.30 * effort

    conflict_pos = np.tanh(_keyword_score(joined, CONFLICT_SKILL) / 3)
    conflict_neg = np.tanh(_keyword_score(joined, CONFLICT_NEG) / 3)
    conflict = 0.35 * _len_score(joined) + 0.35 * conflict_pos + 0.30 * effort - 0.25 * conflict_neg

    if attachment_flags.get("secure"):
        comm += 0.04; emp += 0.04; rel += 0.04; conn += 0.04; conflict += 0.04
    if attachment_flags.get("anxious"):
        conflict -= 0.04
    if attachment_flags.get("avoidant"):
        conn -= 0.04
        comm -= 0.02

    raw = {
        "Communication": comm,
        "Empathy": emp,
        "Reliability": rel,
        "Conflict Navigation": conflict,
        "Connection": conn,
    }
    return {k: float(np.clip(v, 0, 1) * 100) for k, v in raw.items()}


def rgi_from_categories(cat_scores: Dict[str, float], weights: Dict[str, float]) -> float:
    return float(sum(cat_scores[c] * weights.get(c, 0) for c in CATEGORIES))


def dampened_aggregate(values: List[float]) -> float:
    if not values:
        return 0.0
    v = np.array(values, dtype=float)
    if len(v) < 5:
        return float(v.mean())
    v_sorted = np.sort(v)
    k = int(len(v_sorted) * 0.1)
    v_trim = v_sorted[k:len(v_sorted) - k] if (len(v_sorted) - 2 * k) > 0 else v_sorted
    return float(0.5 * v_trim.mean() + 0.5 * (0.6 * np.median(v) + 0.4 * v.mean()))


def ema(values: List[float], alpha: float) -> float:
    if not values:
        return 0.0
    a = float(np.clip(alpha, 0.01, 0.99))
    s = values[0]
    for x in values[1:]:
        s = a * x + (1 - a) * s
    return float(s)


def compute_dashboard(reflections: List[Dict[str, Any]], ema_alpha: float) -> Dict[str, Any]:
    if not reflections:
        return {
            "rgi_point": 0.0,
            "rgi_trend": 0.0,
            "category_point": {c: 0.0 for c in CATEGORIES},
            "category_trend": {c: 0.0 for c in CATEGORIES},
            "n_reflections": 0
        }

    refl = sorted(reflections, key=lambda r: r.get("ts", ""))
    rgis = [float(r.get("rgi", r.get("rsq", 0.0))) for r in refl]
    cats_by_c = {c: [float(r.get("categories", {}).get(c, 0.0)) for r in refl] for c in CATEGORIES}

    tail_n = 10
    rgi_point = dampened_aggregate(rgis[-tail_n:])
    category_point = {c: dampened_aggregate(vals[-tail_n:]) for c, vals in cats_by_c.items()}

    rgi_trend = ema(rgis, ema_alpha)
    category_trend = {c: ema(vals, ema_alpha) for c, vals in cats_by_c.items()}

    return {
        "rgi_point": rgi_point,
        "rgi_trend": rgi_trend,
        "category_point": category_point,
        "category_trend": category_trend,
        "n_reflections": len(reflections)
    }


# -----------------------------
# Branding / CSS
# -----------------------------
def inject_branding():
    st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide")
    st.markdown(
        """
        <style>
        :root{
          --rs-primary:#2C2A4A;
          --rs-soft:#F4F6FB;
          --rs-muted:#475569;
          --rs-border:#E2E8F0;
          --rs-card:#FFFFFF;
        }
        @media (prefers-color-scheme: dark){
          :root{
            --rs-soft:#0B1220;
            --rs-muted:#9CA3AF;
            --rs-border:#1F2937;
            --rs-card:#0F172A;
          }
        }
        .rs-shell{background:var(--rs-soft); padding:18px 18px 6px 18px; border-radius:18px; border:1px solid var(--rs-border);}
        .rs-title{font-size:28px; font-weight:700; color:var(--rs-primary); margin-bottom:6px;}
        .rs-sub{color:var(--rs-muted); margin-top:0px; margin-bottom:0px;}
        .rs-card{background:var(--rs-card); padding:16px; border-radius:18px; border:1px solid var(--rs-border);}
        .rs-footer{color:var(--rs-muted); font-size:12px; padding-top:20px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def footer():
    st.markdown(
        f"<div class='rs-footer'>{MISSION}<br/>Prototype for demonstration only — no clinical, legal, or safety guarantees.</div>",
        unsafe_allow_html=True
    )


# -----------------------------
# Ring (self-contained HTML for components.html)
# -----------------------------
def _interp_hex(c1: str, c2: str, t: float) -> str:
    t = float(np.clip(t, 0, 1))
    c1 = c1.lstrip("#"); c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def rgi_color_growth_band(v: float) -> str:
    v = float(np.clip(v, 0, 100))
    low  = ("#64748B", 0)
    mid  = ("#3B82F6", 55)
    high = ("#6366F1", 100)
    if v <= mid[1]:
        t = (v - low[1]) / (mid[1] - low[1] + 1e-9)
        return _interp_hex(low[0], mid[0], t)
    t = (v - mid[1]) / (high[1] - mid[1] + 1e-9)
    return _interp_hex(mid[0], high[0], t)


def ring_html(rgi_value: float) -> str:
    v = float(np.clip(rgi_value, 0, 100))
    size = 240
    stroke = 18
    radius = (size - stroke) / 2
    cx = cy = size / 2
    circumference = 2 * np.pi * radius
    progress = (v / 100.0) * circumference
    dash_from = circumference
    dash_to = max(0.0, circumference - progress)

    ring_color = rgi_color_growth_band(v)
    tooltip = (
        f"RGI (Relationship Growth Index): {int(v)}/100. "
        "A private, time-weighted growth signal based on structured reflection."
    )

    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      :root {{
        --bg-ring: rgba(59,130,246,0.20);
        --text: #0F172A;
        --subtext: #475569;
      }}
      @media (prefers-color-scheme: dark) {{
        :root {{
          --bg-ring: rgba(59,130,246,0.25);
          --text: #E5E7EB;
          --subtext: #9CA3AF;
        }}
      }}
      body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: sans-serif;
      }}
      .wrap {{
        width: {size}px;
        height: {size}px;
        position: relative;
        margin: 0 auto;
      }}
      @keyframes fill {{
        from {{ stroke-dashoffset: {dash_from:.2f}; }}
        to   {{ stroke-dashoffset: {dash_to:.2f}; }}
      }}
      .anim {{
        animation: fill 1.15s ease-out forwards;
      }}
      .center {{
        position:absolute;
        inset:0;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        pointer-events:none;
        text-align:center;
      }}
      .label {{
        font-size: 30px;
        font-weight: 800;
        color: {ring_color};
        line-height: 1;
      }}
      .value {{
        font-size: 72px;
        font-weight: 900;
        color: var(--text);
        line-height: 1;
        margin-top: 6px;
      }}
      .sub {{
        font-size: 14px;
        color: var(--subtext);
        margin-top: 6px;
      }}
    </style>
  </head>
  <body>
    <div class="wrap">
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="position:absolute;top:0;left:0;">
        <title>{tooltip}</title>
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="var(--bg-ring)" stroke-width="{stroke}"/>
        <circle cx="{cx}" cy="{cy}" r="{radius}"
          fill="none"
          stroke="{ring_color}"
          stroke-width="{stroke}"
          stroke-linecap="round"
          stroke-dasharray="{circumference:.2f}"
          stroke-dashoffset="{dash_from:.2f}"
          transform="rotate(-90 {cx} {cy})"
          class="anim"
        />
      </svg>
      <div class="center">
        <div class="label">RGI</div>
        <div class="value">{int(v)}</div>
        <div class="sub">Relationship Growth Index</div>
      </div>
    </div>
  </body>
</html>
"""


# -----------------------------
# Views
# -----------------------------
def view_home(store: Dict[str, Any]):
    st.markdown("<div class='rs-shell'>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.75, 0.25], vertical_alignment="center")
    with col1:
        st.markdown(f"<div class='rs-title'>{APP_NAME}</div>", unsafe_allow_html=True)
        st.markdown("<p class='rs-sub'>Private, structured reflection with a lightweight scorecard.</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
        st.markdown("**Logo slot**")
        st.caption("Replace with your brand asset later.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
        st.subheader("Start a new reflection thread")
        initiator = st.text_input("Your name (or alias)", value=st.session_state.get("name", ""))
        partner = st.text_input("Partner name (or alias)", value=st.session_state.get("partner_name", ""))
        st.session_state["name"] = initiator
        st.session_state["partner_name"] = partner

        if st.button("Create invite", type="primary"):
            code = _rand_code()
            user_id = get_or_create_user_id()
            store["invites"][code] = {
                "code": code,
                "created_at": _now_iso(),
                "initiator_name": initiator.strip() or "Initiator",
                "partner_name": partner.strip() or "Partner",
                "consents": {user_id: True},
                "withdrawn": False,
                "reflections": [],
                "toxicity_events": 0,
            }
            _save_store(store)
            st.success("Invite created.")
            st.info(f"Share this code with your partner: **{code}**")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
        st.subheader("Join with an invite code")
        code = st.text_input("Invite code", value=st.session_state.get("code", "")).strip().upper()
        st.session_state["code"] = code
        if st.button("Join"):
            if code in store["invites"] and not store["invites"][code].get("withdrawn"):
                st.success("Invite found. Continue to Consent & Reflect in the sidebar.")
                st.session_state["active_code"] = code
            else:
                st.error("Invite code not found (or has been withdrawn).")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    footer()


def view_consent(store: Dict[str, Any], code: str):
    inv = store["invites"].get(code)
    if not inv or inv.get("withdrawn"):
        st.error("This invite is not available.")
        return

    st.markdown("<div class='rs-shell'>", unsafe_allow_html=True)
    st.markdown(f"<div class='rs-title'>Thread: {code}</div>", unsafe_allow_html=True)

    user_id = get_or_create_user_id()
    st.divider()

    st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
    st.subheader("Consent checkpoint (dual consent required)")
    current = inv.get("consents", {})
    you_consented = bool(current.get(user_id, False))
    consent = st.checkbox("I consent to participate in this thread", value=you_consented)

    if st.button("Save consent", type="primary"):
        inv["consents"][user_id] = bool(consent)
        store["invites"][code] = inv
        _save_store(store)
        st.success("Consent saved.")

    dual = len([k for k, v in inv.get("consents", {}).items() if v]) >= 2
    if dual:
        st.success("Dual consent obtained. You may proceed to Reflection.")
    else:
        st.warning("Waiting on dual consent.")

    st.divider()
    st.subheader("Withdraw consent (clears data)")
    if st.button("Withdraw and clear thread", type="secondary"):
        inv["withdrawn"] = True
        inv["reflections"] = []
        store["invites"][code] = inv
        _save_store(store)
        st.success("Thread withdrawn and cleared.")
        st.session_state.pop("active_code", None)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    footer()


def view_reflection(store: Dict[str, Any], code: str):
    inv = store["invites"].get(code)
    if not inv or inv.get("withdrawn"):
        st.error("This invite is not available.")
        return

    user_id = get_or_create_user_id()
    dual = len([k for k, v in inv.get("consents", {}).items() if v]) >= 2
    if not dual:
        st.warning("Dual consent is not yet obtained. Please complete Consent first.")
        return

    st.markdown("<div class='rs-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='rs-title'>Reflection</div>", unsafe_allow_html=True)
    st.divider()

    left, right = st.columns([0.62, 0.38], gap="large")
    with left:
        st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
        effort = st.slider("Self-rating: effort & intent to improve (1–5)", 1, 5, 3)

        answers = []
        for i, p in enumerate(PROMPTS, start=1):
            answers.append(st.text_area(f"Prompt {i}", placeholder=p, height=110, key=f"ans_{i}"))

        c1, c2, c3 = st.columns(3)
        with c1: anxious = st.checkbox("Anxious", value=False)
        with c2: avoidant = st.checkbox("Avoidant", value=False)
        with c3: secure = st.checkbox("Secure", value=False)

        attachments = {"anxious": anxious, "avoidant": avoidant, "secure": secure}

        toxicity_ok, tox_score = enforce_toxicity_gate([*answers], threshold=0.55)
        if not toxicity_ok:
            st.error(f"Input blocked by the toxicity gate (score {tox_score:.2f}). Please revise.")
        else:
            if st.button("Submit reflection", type="primary"):
                cat_scores = score_categories(effort, answers, attachments)
                rgi = rgi_from_categories(cat_scores, DEFAULT_WEIGHTS)
                inv["reflections"].append({
                    "ts": _now_iso(),
                    "user_id": user_id,
                    "effort": int(effort),
                    "answers": answers,
                    "attachments": attachments,
                    "categories": cat_scores,
                    "rgi": rgi,
                })
                store["invites"][code] = inv
                _save_store(store)
                st.success("Reflection saved.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
        ema_alpha = st.slider("Time-weighting alpha (EMA)", 0.30, 0.80, 0.50, 0.05)
        st.session_state["ema_alpha"] = ema_alpha
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    footer()


def view_dashboard(store: Dict[str, Any], code: str):
    inv = store["invites"].get(code)
    if not inv or inv.get("withdrawn"):
        st.error("This invite is not available.")
        return

    dual = len([k for k, v in inv.get("consents", {}).items() if v]) >= 2
    if not dual:
        st.warning("Dual consent is not yet obtained. Please complete Consent first.")
        return

    ema_alpha = float(st.session_state.get("ema_alpha", 0.50))
    refl = inv.get("reflections", [])
    dashboard = compute_dashboard(refl, ema_alpha)

    rgi_point = float(np.clip(dashboard["rgi_point"], 0, 100))
    rgi_trend = float(np.clip(dashboard["rgi_trend"], 0, 100))

    st.markdown("<div class='rs-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='rs-title'>Private Output</div>", unsafe_allow_html=True)
    st.markdown("<p class='rs-sub'>RGI (Relationship Growth Index), insights, and a lightweight red-flag dashboard.</p>", unsafe_allow_html=True)
    st.divider()

    hero_left, hero_right = st.columns([0.40, 0.60], gap="large", vertical_alignment="center")

    with hero_left:
        # ✅ RELIABLE RENDER: components.html will not print HTML as text
        components.html(ring_html(rgi_point), height=260)

    with hero_right:
        st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
        st.subheader("What this means")
        st.write("RGI is a private, time-weighted growth signal (0–100) based on structured reflection.")
        m1, m2 = st.columns(2)
        m1.metric("EMA trend", f"{rgi_trend:0.1f}")
        m2.metric("Reflections", f"{dashboard['n_reflections']}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("<div class='rs-card'>", unsafe_allow_html=True)
    st.subheader("Category scorecard (0–100)")
    df = pd.DataFrame({
        "Category": CATEGORIES,
        "Point": [dashboard["category_point"][c] for c in CATEGORIES],
        "Trend": [dashboard["category_trend"][c] for c in CATEGORIES],
        "Weight": [DEFAULT_WEIGHTS[c] for c in CATEGORIES],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    footer()


# -----------------------------
# Router
# -----------------------------
def main():
    inject_branding()
    store = _load_store()
    code = st.session_state.get("active_code") or st.session_state.get("code") or ""

    st.sidebar.title("RelateScore™")
    page = st.sidebar.radio("Go to", ["Home", "Consent", "Reflection", "Dashboard"], index=0)

    if page == "Home":
        view_home(store)
        return

    if not code:
        st.sidebar.info("Join or create an invite code on Home first.")
        view_home(store)
        return

    st.sidebar.markdown(f"**Active code:** `{code}`")

    if page == "Consent":
        view_consent(store, code)
    elif page == "Reflection":
        view_reflection(store, code)
    elif page == "Dashboard":
        view_dashboard(store, code)


if __name__ == "__main__":
    main()
