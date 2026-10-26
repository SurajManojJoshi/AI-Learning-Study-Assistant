"""
Simplified UI Components for AI Learning & Study Assistant.
Uses clean, minimal Streamlit-native styling — no over-engineered CSS frameworks.
"""

import streamlit as st
from typing import List, Dict, Any, Optional

# ── Minimal global CSS ───────────────────────────────────────────────────────
_CSS = """
<style>
/* Clean font */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Remove default top padding */
.block-container { padding-top: 1.5rem !important; }

/* Page hero banner */
.page-banner {
    background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
    color: white;
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.6rem;
}
.page-banner h1 { margin: 0 0 0.3rem 0; font-size: 1.7rem; font-weight: 800; }
.page-banner p  { margin: 0; opacity: 0.88; font-size: 0.97rem; }

/* Stat card */
.stat-card {
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    text-align: center;
}
.stat-card .val { font-size: 2rem; font-weight: 800; color: #4F46E5; }
.stat-card .lbl { font-size: 0.8rem; color: #6B7280; margin-top: 2px; }

/* Info box */
.info-box {
    background: #EEF2FF;
    border-left: 4px solid #4F46E5;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.8rem 0;
    font-size: 0.92rem;
    color: #1e1b4b;
}

/* Chat bubbles */
.bubble-user {
    background: #4F46E5;
    color: white;
    border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0 0.5rem auto;
    max-width: 78%;
    width: fit-content;
    font-size: 0.93rem;
    line-height: 1.5;
}
.bubble-ai {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 16px 16px 16px 4px;
    padding: 0.9rem 1.1rem;
    margin: 0.5rem auto 0.5rem 0;
    max-width: 82%;
    width: fit-content;
    font-size: 0.93rem;
    line-height: 1.6;
}
.source-chip {
    display: inline-block;
    background: #F3F4F6;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.75rem;
    color: #374151;
    margin: 2px 3px;
}

/* Quiz question card */
.quiz-card {
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}
.quiz-question { font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 1rem; }

/* Review card */
.review-correct {
    border-left: 4px solid #10B981;
    background: #F0FDF4;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}
.review-wrong {
    border-left: 4px solid #EF4444;
    background: #FEF2F2;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}

/* Pathway stage card */
.stage-card {
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
}
.stage-beginner  { border-left: 5px solid #10B981; background: #F0FDF4; }
.stage-intermediate { border-left: 5px solid #F59E0B; background: #FFFBEB; }
.stage-advanced  { border-left: 5px solid #EF4444; background: #FEF2F2; }

/* Timeline study plan */
.day-card {
    background: #fff;
    border: 1px solid #E5E7EB;
    border-left: 4px solid #4F46E5;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.day-card.done { border-left-color: #10B981; background: #F0FDF4; opacity: 0.9; }
.day-card.weak { border-left-color: #F59E0B; background: #FFFBEB; }

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #9CA3AF;
    border: 2px dashed #E5E7EB;
    border-radius: 12px;
    margin: 1rem 0;
}
.empty-state .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.empty-state .title { font-size: 1.05rem; font-weight: 700; color: #374151; }
.empty-state .desc  { font-size: 0.87rem; margin-top: 0.3rem; }

/* Hide default Streamlit sidebar nav */
div[data-testid="stSidebarNav"] { display: none; }
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


# ── Page banner ───────────────────────────────────────────────────────────────
def page_banner(title: str, subtitle: str):
    st.markdown(
        f'<div class="page-banner"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


# ── Stat card ─────────────────────────────────────────────────────────────────
def stat_card(value: Any, label: str):
    st.markdown(
        f'<div class="stat-card"><div class="val">{value}</div><div class="lbl">{label}</div></div>',
        unsafe_allow_html=True,
    )


# ── Info box ──────────────────────────────────────────────────────────────────
def info_box(text: str):
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)


# ── Empty state ───────────────────────────────────────────────────────────────
def empty_state(icon: str, title: str, desc: str):
    st.markdown(
        f'<div class="empty-state"><div class="icon">{icon}</div>'
        f'<div class="title">{title}</div>'
        f'<div class="desc">{desc}</div></div>',
        unsafe_allow_html=True,
    )


# ── Chat bubbles ──────────────────────────────────────────────────────────────
def chat_user(text: str):
    st.markdown(f'<div class="bubble-user">{text}</div>', unsafe_allow_html=True)


def chat_ai(text: str, sources: Optional[List[Dict]] = None):
    # Render AI text via st.markdown so markdown formatting works
    with st.container():
        st.markdown(
            f'<div class="bubble-ai">',
            unsafe_allow_html=True,
        )
        st.markdown(text)
        if sources:
            chips = " ".join(
                f'<span class="source-chip">📄 {s.get("file_name","Doc")} p.{s.get("page",1)}</span>'
                for s in sources
            )
            st.markdown(
                f'<div style="margin-top:6px;">{chips}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ── Quiz review card ──────────────────────────────────────────────────────────
def question_review_card(item: Dict[str, Any]):
    css = "review-correct" if item.get("is_correct") else "review-wrong"
    badge = "✅ Correct" if item.get("is_correct") else "❌ Wrong"
    correct_line = ""
    if not item.get("is_correct"):
        correct_line = (
            f"<div style='margin:4px 0; font-size:0.88rem;'>"
            f"<strong>Correct:</strong> {item.get('correct_option','')}. {item.get('correct_text','')}"
            f"</div>"
        )
    html = (
        f'<div class="{css}">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
        f'<strong>Q{item.get("id","")}. {item.get("question","")}</strong>'
        f'<span>{badge}</span></div>'
        f'<div style="font-size:0.88rem;">Your answer: {item.get("selected_option","")}. {item.get("selected_text","No answer")}</div>'
        f'{correct_line}'
        f'<div style="font-size:0.83rem;margin-top:5px;color:#374151;">💡 {item.get("explanation","")}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ── Pathway stage card ────────────────────────────────────────────────────────
def pathway_stage_card(stage: Dict[str, Any], completed: bool = False):
    stage_name = stage.get("stage", "Stage")
    css_map = {"Beginner": "stage-beginner", "Intermediate": "stage-intermediate", "Advanced": "stage-advanced"}
    extra_css = css_map.get(stage_name, "")
    check = "✅ " if completed else ""
    topics_html = "".join(f"<li>{t}</li>" for t in stage.get("topics", []))
    hours = stage.get("hours", "")
    html = (
        f'<div class="stage-card {extra_css}">'
        f'<div style="font-weight:700;font-size:1rem;margin-bottom:6px;">{check}{stage_name}'
        f'{"  ·  " + str(hours) + " hrs" if hours else ""}</div>'
        f'<ul style="margin:0;padding-left:1.2rem;font-size:0.88rem;">{topics_html}</ul>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ── Study plan day card ───────────────────────────────────────────────────────
def day_card_header(day_num: int, title: str, done: bool, weak: bool):
    css = "day-card done" if done else ("day-card weak" if weak else "day-card")
    badge = " ✅" if done else (" ⚠️ Focus" if weak else "")
    st.markdown(
        f'<div class="{css}"><strong>Day {day_num}{badge}</strong> — {title}</div>',
        unsafe_allow_html=True,
    )


# ── Document card ─────────────────────────────────────────────────────────────
def doc_card(fname: str, pages: int, chunks: int):
    st.markdown(
        f'<div style="background:#fff;border:1px solid #E5E7EB;border-radius:8px;padding:0.8rem 1rem;'
        f'margin-bottom:0.6rem;display:flex;justify-content:space-between;align-items:center;">'
        f'<div><strong>📘 {fname}</strong>'
        f'<div style="font-size:0.8rem;color:#6B7280;margin-top:2px;">{pages} pages · {chunks} chunks</div></div>'
        f'<span style="background:#D1FAE5;color:#065F46;font-size:0.75rem;font-weight:700;padding:2px 8px;border-radius:12px;">✓ Ready</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Performance summary ───────────────────────────────────────────────────────
def performance_banner(score: int, total: int, pct: float):
    if pct >= 80:
        color, emoji, msg = "#065F46", "🌟", "Excellent!"
        bg = "#D1FAE5"
    elif pct >= 60:
        color, emoji, msg = "#1D4ED8", "👍", "Good work!"
        bg = "#DBEAFE"
    else:
        color, emoji, msg = "#B91C1C", "⚠️", "Needs review"
        bg = "#FEE2E2"
    st.markdown(
        f'<div style="background:{bg};border-radius:12px;padding:1.4rem;text-align:center;margin-bottom:1rem;">'
        f'<div style="font-size:2.4rem;font-weight:900;color:{color};">{score} / {total}</div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:{color};">{emoji} {pct}% — {msg}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── PDF upload stepper ────────────────────────────────────────────────────────
def stepper(active: int):
    steps = ["Upload", "Extract", "Chunk", "Embed", "Index", "Done"]
    items = []
    for i, s in enumerate(steps):
        if i < active:
            items.append(f'<span style="color:#10B981;font-size:0.8rem;">✓ {s}</span>')
        elif i == active:
            items.append(f'<span style="color:#4F46E5;font-weight:700;font-size:0.8rem;">⟳ {s}</span>')
        else:
            items.append(f'<span style="color:#9CA3AF;font-size:0.8rem;">{s}</span>')
    st.markdown(
        '<div style="display:flex;gap:1.2rem;align-items:center;padding:0.6rem 0;">'
        + " → ".join(items)
        + "</div>",
        unsafe_allow_html=True,
    )
