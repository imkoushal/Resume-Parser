"""
app.py - Streamlit UI for the Resume Parser application.

Run with:
    streamlit run app.py
"""

import io
import streamlit as st

from src.resume_parser import ResumeParser
from src.jd_matcher import JDMatcher

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Resume Parser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Theme initialisation
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

is_dark = st.session_state["theme"] == "dark"

# ---------------------------------------------------------------------------
# CSS — theme-aware, injected dynamically
# ---------------------------------------------------------------------------
if is_dark:
    BG          = "#0F172A"
    CARD_BG     = "#1E293B"
    CARD_BORDER = "#334155"
    TEXT        = "#F1F5F9"
    SUBTEXT     = "#94A3B8"
    LABEL       = "#64748B"
    VALUE       = "#E2E8F0"
    HEADER_BG   = "#1E293B"
    HEADER_TEXT = "#F1F5F9"
    HEADER_SUB  = "#94A3B8"
    INPUT_BG    = "#1E293B"
    DIVIDER     = "#334155"
    EDU_BG      = "#0F172A"
    EDU_TEXT    = "#CBD5E1"
    EMPTY_BG    = "#1E293B"
    EMPTY_TEXT  = "#64748B"
    BTN_BG      = "#6366F1"
    BTN_HOVER   = "#4F46E5"
    BTN_TEXT    = "#FFFFFF"
    UPLOAD_BG   = "#1E293B"
    UPLOAD_BORD = "#475569"
    BADGE_FMT_BG = "#1E3A5F"
    BADGE_FMT_TX = "#93C5FD"
    BADGE_FMT_BD = "#3B82F6"
else:
    BG          = "#F1F5F9"
    CARD_BG     = "#FFFFFF"
    CARD_BORDER = "#E2E8F0"
    TEXT        = "#1E293B"
    SUBTEXT     = "#475569"
    LABEL       = "#94A3B8"
    VALUE       = "#1E293B"
    HEADER_BG   = "#1E293B"
    HEADER_TEXT = "#F1F5F9"
    HEADER_SUB  = "#94A3B8"
    INPUT_BG    = "#FFFFFF"
    DIVIDER     = "#E2E8F0"
    EDU_BG      = "#F8FAFC"
    EDU_TEXT    = "#334155"
    EMPTY_BG    = "#F8FAFC"
    EMPTY_TEXT  = "#94A3B8"
    BTN_BG      = "#1E293B"
    BTN_HOVER   = "#334155"
    BTN_TEXT    = "#F1F5F9"
    UPLOAD_BG   = "#FAFAFA"
    UPLOAD_BORD = "#CBD5E1"
    BADGE_FMT_BG = "#EFF6FF"
    BADGE_FMT_TX = "#1D4ED8"
    BADGE_FMT_BD = "#BFDBFE"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* ── Page background ── */
    .stApp {{ background-color: {BG}; }}

    /* ── Hero header ── */
    .hero {{
        background: {HEADER_BG};
        border-radius: 14px;
        padding: 2rem 2.5rem;
        text-align: center;
        margin-bottom: 1.8rem;
    }}
    .hero h1 {{
        margin: 0 0 0.4rem;
        font-size: 2rem;
        font-weight: 700;
        color: {HEADER_TEXT};
        letter-spacing: -0.02em;
    }}
    .hero p {{
        margin: 0;
        font-size: 0.95rem;
        color: {HEADER_SUB};
    }}

    /* ── Section cards ── */
    .card {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }}
    .card-title {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: {LABEL};
        margin-bottom: 0.75rem;
    }}

    /* ── Helper text ── */
    .helper-text {{
        font-size: 0.8rem;
        color: {SUBTEXT};
        margin-top: 0.5rem;
    }}

    /* ── Format badges ── */
    .fmt-badge {{
        display: inline-block;
        padding: 0.18rem 0.6rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        background: {BADGE_FMT_BG};
        color: {BADGE_FMT_TX};
        border: 1px solid {BADGE_FMT_BD};
        margin-right: 0.3rem;
    }}

    /* ── Info grid ── */
    .info-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 0.9rem;
    }}
    .info-label {{
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {LABEL};
        margin-bottom: 0.15rem;
    }}
    .info-value {{
        font-size: 0.93rem;
        font-weight: 500;
        color: {VALUE};
        word-break: break-all;
    }}
    .info-value.empty {{ color: {LABEL}; font-style: italic; }}

    /* ── Skill pills ── */
    .pill-wrap {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
    .pill {{
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
        line-height: 1.4;
    }}
    .pill-blue  {{ background: {'#1E3A5F' if is_dark else '#EFF6FF'}; color: {'#93C5FD' if is_dark else '#1D4ED8'}; border: 1px solid {'#3B82F6' if is_dark else '#BFDBFE'}; }}
    .pill-green {{ background: {'#14532D' if is_dark else '#F0FDF4'}; color: {'#86EFAC' if is_dark else '#15803D'}; border: 1px solid {'#22C55E' if is_dark else '#BBF7D0'}; }}
    .pill-red   {{ background: {'#4C0519' if is_dark else '#FFF1F2'}; color: {'#FDA4AF' if is_dark else '#BE123C'}; border: 1px solid {'#F43F5E' if is_dark else '#FECDD3'}; }}

    /* ── Score ring ── */
    .score-wrap {{
        display: flex;
        align-items: center;
        gap: 1.6rem;
        flex-wrap: wrap;
    }}
    .score-circle {{
        width: 100px; height: 100px;
        border-radius: 50%;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }}
    .score-pct   {{ font-size: 1.6rem; line-height: 1; }}
    .score-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }}
    .score-high  {{ background: {'#14532D' if is_dark else '#F0FDF4'}; color: {'#86EFAC' if is_dark else '#15803D'}; border: 3px solid {'#22C55E' if is_dark else '#4ADE80'}; }}
    .score-mid   {{ background: {'#451A03' if is_dark else '#FFFBEB'}; color: {'#FCD34D' if is_dark else '#B45309'}; border: 3px solid {'#F59E0B' if is_dark else '#FCD34D'}; }}
    .score-low   {{ background: {'#4C0519' if is_dark else '#FFF1F2'}; color: {'#FDA4AF' if is_dark else '#BE123C'}; border: 3px solid {'#F43F5E' if is_dark else '#FB7185'}; }}

    .score-meta {{ flex: 1; min-width: 180px; }}
    .score-meta p {{ margin: 0.25rem 0; font-size: 0.88rem; color: {SUBTEXT}; }}
    .score-meta strong {{ color: {TEXT}; }}

    /* ── Badge (is_match) ── */
    .badge {{
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }}
    .badge-pass {{ background: {'#14532D' if is_dark else '#DCFCE7'}; color: {'#86EFAC' if is_dark else '#166534'}; }}
    .badge-fail {{ background: {'#4C0519' if is_dark else '#FFE4E6'}; color: {'#FDA4AF' if is_dark else '#9F1239'}; }}

    /* ── Divider ── */
    .divider {{ border: none; border-top: 1px solid {DIVIDER}; margin: 1rem 0; }}

    /* ── Education entry ── */
    .edu-entry {{
        padding: 0.5rem 0.75rem;
        border-left: 3px solid #6366F1;
        background: {EDU_BG};
        border-radius: 0 6px 6px 0;
        margin-bottom: 0.5rem;
        font-size: 0.88rem;
        color: {EDU_TEXT};
    }}

    /* ── Streamlit button override ── */
    div.stButton > button {{
        background: {BTN_BG};
        color: {BTN_TEXT};
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.8rem;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        transition: background 0.2s ease;
    }}
    div.stButton > button:hover {{
        background: {BTN_HOVER};
        color: {BTN_TEXT};
    }}

    /* ── Upload area ── */
    [data-testid="stFileUploader"] {{
        border: 1.5px dashed {UPLOAD_BORD};
        border-radius: 10px;
        padding: 0.5rem;
        background: {UPLOAD_BG};
    }}

    /* ── Text area ── */
    .stTextArea textarea {{
        background: {INPUT_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {CARD_BORDER} !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
    }}

    /* ── Expander ── */
    .streamlit-expanderHeader {{
        background: {CARD_BG} !important;
        color: {TEXT} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    .streamlit-expanderContent {{
        background: {CARD_BG} !important;
        border: 1px solid {CARD_BORDER} !important;
        border-radius: 0 0 8px 8px !important;
    }}

    /* ── Spinner text ── */
    .stSpinner > div {{ color: {TEXT} !important; }}

    /* ── General text color ── */
    .stMarkdown, p, li, label {{ color: {TEXT}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pill(text: str, kind: str = "blue") -> str:
    return f'<span class="pill pill-{kind}">{text}</span>'


def _pills_html(items: list, kind: str = "blue") -> str:
    if not items:
        return f"<span style='color:{LABEL};font-size:0.85rem;'>None detected</span>"
    return '<div class="pill-wrap">' + "".join(_pill(s, kind) for s in items) + "</div>"


def _score_class(score: float) -> str:
    if score >= 70:
        return "score-high"
    if score >= 40:
        return "score-mid"
    return "score-low"


def _info_value(val) -> str:
    if val is None or val == "":
        return '<span class="info-value empty">—</span>'
    return f'<span class="info-value">{val}</span>'


@st.cache_resource
def _get_parser():
    return ResumeParser()


@st.cache_resource
def _get_matcher():
    return JDMatcher()


# ---------------------------------------------------------------------------
# Top bar: Theme toggle (top-right)
# ---------------------------------------------------------------------------
_, toggle_col = st.columns([6, 1])
with toggle_col:
    toggle_label = "🌞 Light" if is_dark else "🌙 Dark"
    if st.button(toggle_label, key="theme_toggle"):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()

# ---------------------------------------------------------------------------
# Hero Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <h1>📄 Resume Parser</h1>
        <p>Extract structured information from resumes and match against job descriptions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------------
left_col, right_col = st.columns([1, 2], gap="large")

# ── LEFT: Inputs ─────────────────────────────────────────────────────────────
with left_col:

    # Upload card
    st.markdown(f'<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📎 Upload Resume</div>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="fmt-badge">PDF</span><span class="fmt-badge">DOCX</span>',
        unsafe_allow_html=True,
    )
    resume_file = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx"],
        key="resume_upload",
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div class="helper-text">📁 Drag & drop or browse — PDF and DOCX supported</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # JD card
    st.markdown(f'<div class="card" style="border-left: 3px solid #6366F1;">', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-title">📋 Job Description <span style="font-weight:400;text-transform:none;letter-spacing:0;">(Optional)</span></div>',
        unsafe_allow_html=True,
    )
    jd_text = st.text_area(
        "Job description",
        height=220,
        placeholder="Paste the full job description here to enable JD matching…",
        label_visibility="collapsed",
        key="jd_input",
    )
    st.markdown(
        '<div class="helper-text">💡 Paste a job description to enable JD matching</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    analyze_btn = st.button("🔍  Analyze Resume", disabled=(resume_file is None))

# ── RIGHT: Results ────────────────────────────────────────────────────────────
with right_col:

    if not resume_file:
        # Empty state placeholder
        st.markdown(
            f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:380px;
                        background:{CARD_BG};border:1px dashed {CARD_BORDER};
                        border-radius:14px;color:{EMPTY_TEXT};text-align:center;">
                <div style="font-size:3.5rem;margin-bottom:1rem;">📄</div>
                <div style="font-size:1.05rem;font-weight:600;color:{SUBTEXT};">Upload a resume to get started</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;color:{LABEL};">
                    Supports PDF and DOCX formats
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif analyze_btn or st.session_state.get("analyzed"):
        st.session_state["analyzed"] = True

        with st.spinner("Parsing resume…"):
            try:
                parser = _get_parser()
                matcher = _get_matcher()

                # Read file bytes and wrap in BytesIO with a .name attribute
                file_bytes = resume_file.read()
                buf = io.BytesIO(file_bytes)
                buf.name = resume_file.name

                # Extract text & parse
                from src.text_extractor import TextExtractor
                extractor = TextExtractor()
                raw_text = extractor.extract(buf)
                result = parser.parse_text(raw_text)

                # ── Section 1: Extracted Information ──────────────────────
                with st.expander("👤 Extracted Information", expanded=True):
                    st.markdown(
                        f"""
                        <div class="info-grid">
                            <div>
                                <div class="info-label">Name</div>
                                {_info_value(result.get("name"))}
                            </div>
                            <div>
                                <div class="info-label">Email</div>
                                {_info_value(result.get("email"))}
                            </div>
                            <div>
                                <div class="info-label">Phone</div>
                                {_info_value(result.get("phone"))}
                            </div>
                            <div>
                                <div class="info-label">Experience</div>
                                {_info_value(
                                    f'{result.get("years_of_experience", 0)} yr(s)'
                                    if result.get("years_of_experience") else None
                                )}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Education
                    edu_entries = result.get("education", [])
                    if edu_entries:
                        st.markdown('<hr class="divider">', unsafe_allow_html=True)
                        st.markdown('<div class="card-title" style="margin-top:0.6rem;">🎓 Education</div>', unsafe_allow_html=True)
                        for edu in edu_entries:
                            year_str = f" · {edu['year']}" if edu.get("year") else ""
                            st.markdown(
                                f'<div class="edu-entry">{edu["degree"]}{year_str}</div>',
                                unsafe_allow_html=True,
                            )

                # ── Section 2: Skills ──────────────────────────────────────
                skills = result.get("skills", [])
                with st.expander(f"🛠️ Skills Detected ({len(skills)})", expanded=True):
                    st.markdown(_pills_html(skills, "blue"), unsafe_allow_html=True)

                # ── Section 3: JD Match (only if JD provided) ─────────────
                if jd_text.strip():
                    result["_raw_text"] = raw_text
                    match_result = matcher.match(result, jd_text)

                    score          = match_result["match_score"]
                    skill_score    = match_result["skill_score"]
                    semantic_score = match_result["semantic_score"]
                    matched        = match_result["matched_skills"]
                    missing        = match_result["missing_skills"]
                    is_match       = match_result["is_match"]
                    badge_html = (
                        '<span class="badge badge-pass">✓ Good Match</span>'
                        if is_match
                        else '<span class="badge badge-fail">✗ Below Threshold</span>'
                    )

                    with st.expander("📊 JD Match Analysis", expanded=True):
                        st.markdown(
                            f"""
                            <div class="score-wrap">
                                <div class="score-circle {_score_class(score)}">
                                    <span class="score-pct">{score:.0f}%</span>
                                    <span class="score-label">Match</span>
                                </div>
                                <div class="score-meta">
                                    <p>Overall verdict: {badge_html}</p>
                                    <p>Skill overlap score: <strong>{skill_score:.1f}%</strong></p>
                                    <p>Semantic similarity: <strong>{semantic_score:.1f}%</strong></p>
                                    <p>Matched skills: <strong>{len(matched)}</strong> &nbsp;·&nbsp;
                                       Missing skills: <strong>{len(missing)}</strong></p>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.markdown('<hr class="divider">', unsafe_allow_html=True)

                        m_col, g_col = st.columns(2)
                        with m_col:
                            st.markdown('<div class="card-title" style="margin-bottom:0.5rem;">✅ Matched Skills</div>', unsafe_allow_html=True)
                            st.markdown(_pills_html(matched, "green"), unsafe_allow_html=True)
                        with g_col:
                            st.markdown('<div class="card-title" style="margin-bottom:0.5rem;">❌ Missing Skills</div>', unsafe_allow_html=True)
                            st.markdown(_pills_html(missing, "red"), unsafe_allow_html=True)

                else:
                    st.markdown(
                        f"""
                        <div style="border:1.5px dashed {CARD_BORDER};background:{CARD_BG};
                                    border-radius:12px;text-align:center;
                                    color:{EMPTY_TEXT};padding:1.4rem;margin-top:0.5rem;">
                            <div style="font-size:1.6rem;margin-bottom:0.4rem;">📋</div>
                            <div style="font-size:0.88rem;">
                                Paste a job description on the left to see match analysis.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            except Exception as exc:
                st.error(f"**Error during parsing:** {exc}")
                st.exception(exc)

    else:
        # File uploaded but button not yet clicked
        st.markdown(
            f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:320px;
                        background:{CARD_BG};border:1px solid {CARD_BORDER};
                        border-radius:14px;color:{EMPTY_TEXT};text-align:center;">
                <div style="font-size:2.8rem;margin-bottom:0.8rem;">✅</div>
                <div style="font-size:1rem;font-weight:500;color:{SUBTEXT};">
                    <strong style="color:{TEXT};">{resume_file.name}</strong> ready
                </div>
                <div style="font-size:0.85rem;margin-top:0.4rem;color:{LABEL};">
                    Click <strong style="color:{TEXT};">Analyze Resume</strong> to continue.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
