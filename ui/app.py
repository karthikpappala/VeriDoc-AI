"""
VeriDoc AI — Streamlit Frontend v3
Run: streamlit run ui/app.py
"""

import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="VeriDoc AI",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"          not in st.session_state: st.session_state.messages = []
if "active_doc"        not in st.session_state: st.session_state.active_doc = None
if "active_doc_name"   not in st.session_state: st.session_state.active_doc_name = None
if "last_response"     not in st.session_state: st.session_state.last_response = None
if "admin_mode"        not in st.session_state: st.session_state.admin_mode = False
if "dark_mode"         not in st.session_state: st.session_state.dark_mode = True

DARK = st.session_state.dark_mode

# ── Theme tokens ──────────────────────────────────────────────────────────────
if DARK:
    BG          = "#050d1f"
    BG2         = "#0a1628"
    BG3         = "#0f1e38"
    BORDER      = "rgba(99,102,241,0.15)"
    TEXT        = "#e2e8f0"
    TEXT2       = "#7c8fa8"
    TEXT3       = "#334155"
    CARD_BG     = "rgba(15,23,42,0.8)"
    GRAD_ORB    = "radial-gradient(ellipse 70% 60% at 15% 5%, rgba(99,102,241,0.12) 0%, transparent 55%), radial-gradient(ellipse 50% 40% at 85% 90%, rgba(16,185,129,0.08) 0%, transparent 55%)"
    USER_BG     = "linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.1) 100%)"
    USER_BORDER = "rgba(99,102,241,0.25)"
    AI_BG       = "rgba(15,23,42,0.7)"
    AI_BORDER   = "rgba(255,255,255,0.07)"
    SIDEBAR_BG  = "rgba(8,15,35,0.98)"
else:
    BG          = "#f8faff"
    BG2         = "#eef2ff"
    BG3         = "#e0e7ff"
    BORDER      = "rgba(99,102,241,0.2)"
    TEXT        = "#1e1b4b"
    TEXT2       = "#4338ca"
    TEXT3       = "#6366f1"
    CARD_BG     = "rgba(255,255,255,0.95)"
    GRAD_ORB    = "radial-gradient(ellipse 70% 60% at 15% 5%, rgba(99,102,241,0.08) 0%, transparent 55%), radial-gradient(ellipse 50% 40% at 85% 90%, rgba(16,185,129,0.06) 0%, transparent 55%)"
    USER_BG     = "linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.07) 100%)"
    USER_BORDER = "rgba(99,102,241,0.3)"
    AI_BG       = "rgba(255,255,255,0.95)"
    AI_BORDER   = "rgba(99,102,241,0.15)"
    SIDEBAR_BG  = "rgba(238,242,255,0.98)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 1.5rem 2rem 2rem; max-width: 1300px; }}

.stApp {{
    background: {BG};
    background-image: {GRAD_ORB};
}}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    border-right: 1px solid {BORDER} !important;
}}
section[data-testid="stSidebar"] .block-container {{ padding: 1rem 0.75rem; }}

.logo-wrap {{
    display: flex; align-items: center; gap: 12px;
    padding: 0.8rem 0.5rem 1rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 1rem;
}}
.logo-icon {{
    width: 38px; height: 38px; border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; box-shadow: 0 0 16px rgba(99,102,241,0.4); flex-shrink: 0;
}}
.logo-text {{ font-size: 17px; font-weight: 700; color: {TEXT}; letter-spacing: -0.3px; }}
.logo-sub {{ font-size: 10px; color: {TEXT3}; font-family: 'JetBrains Mono', monospace; margin-top: 1px; }}

.sec-label {{
    font-size: 10px; font-weight: 600; color: {TEXT3};
    text-transform: uppercase; letter-spacing: 0.1em;
    margin: 0.8rem 0 0.4rem 0.25rem;
}}

.stButton button {{
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT2} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important; font-weight: 500 !important;
    transition: all 0.2s !important;
}}
.stButton button:hover {{
    background: rgba(99,102,241,0.18) !important;
    border-color: rgba(99,102,241,0.45) !important;
    color: {'#c7d2fe' if DARK else '#4338ca'} !important;
    box-shadow: 0 0 12px rgba(99,102,241,0.15) !important;
}}

[data-testid="stFileUploader"] {{
    background: {'rgba(99,102,241,0.05)' if DARK else 'rgba(99,102,241,0.03)'} !important;
    border: 1.5px dashed rgba(99,102,241,0.3) !important;
    border-radius: 14px !important;
}}

.stTextInput input {{
    background: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    color: {TEXT} !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}}
.stTextInput input:focus {{
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}}
.stTextInput input::placeholder {{ color: {TEXT3} !important; }}

[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important; border-radius: 10px !important;
    color: white !important; font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.35) !important;
    transition: all 0.2s !important;
}}
[data-testid="stFormSubmitButton"] button:hover {{
    box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
}}

.msg-user {{
    background: {USER_BG};
    border: 1px solid {USER_BORDER};
    border-radius: 16px 16px 4px 16px;
    padding: 14px 18px; margin: 8px 0 8px 15%;
    color: {TEXT}; font-size: 14px; line-height: 1.65;
    box-shadow: 0 4px 20px rgba(99,102,241,0.1);
}}
.msg-user-label {{
    font-size: 10px; font-weight: 600; color: #818cf8;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 6px; font-family: 'JetBrains Mono', monospace;
}}
.msg-ai {{
    background: {AI_BG};
    border: 1px solid {AI_BORDER};
    border-radius: 4px 16px 16px 16px;
    padding: 16px 20px; margin: 8px 10% 8px 0;
    color: {TEXT}; font-size: 14px; line-height: 1.75;
    box-shadow: 0 4px 24px rgba(0,0,0,{'0.2' if DARK else '0.06'});
    position: relative;
}}
.msg-ai::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #6366f1, #10b981, transparent);
    border-radius: 4px 16px 0 0;
}}
.msg-ai-label {{
    font-size: 10px; font-weight: 600; color: #10b981;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 8px; font-family: 'JetBrains Mono', monospace;
}}

.citation-wrap {{
    margin: 6px 0;
    background: {'rgba(16,185,129,0.05)' if DARK else 'rgba(16,185,129,0.04)'};
    border: 1px solid rgba(16,185,129,0.15);
    border-left: 3px solid #10b981;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
}}
.citation-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
.citation-rank {{
    width: 20px; height: 20px; border-radius: 50%;
    background: rgba(16,185,129,0.2); color: #10b981;
    font-size: 10px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace; flex-shrink: 0;
}}
.citation-meta {{ font-size: 11px; color: #10b981; font-family: 'JetBrains Mono', monospace; font-weight: 500; }}
.citation-score {{ margin-left: auto; font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #f59e0b; font-weight: 600; }}
.citation-text {{ font-size: 12px; color: {'#4a6080' if DARK else '#6b7280'}; line-height: 1.5; }}

.badges-row {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; padding-top: 10px; border-top: 1px solid {BORDER}; }}
.badge {{ padding: 4px 10px; border-radius: 20px; font-size: 11px; font-family: 'JetBrains Mono', monospace; font-weight: 600; }}
.badge-green {{ background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }}
.badge-yellow {{ background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }}
.badge-red {{ background: rgba(244,63,94,0.12); color: #f43f5e; border: 1px solid rgba(244,63,94,0.25); }}
.badge-cyan {{ background: rgba(6,182,212,0.12); color: #22d3ee; border: 1px solid rgba(6,182,212,0.25); }}

.admin-header {{
    font-size: 10px; font-weight: 600; color: {TEXT3};
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 8px 14px; background: {'rgba(0,0,0,0.3)' if DARK else 'rgba(99,102,241,0.06)'};
    border-radius: 8px 8px 0 0;
    display: grid; grid-template-columns: 24px 60px 44px 1fr;
    gap: 8px; font-family: 'JetBrains Mono', monospace;
}}
.admin-row {{
    padding: 9px 14px;
    display: grid; grid-template-columns: 24px 60px 44px 1fr;
    gap: 8px; font-size: 12px;
    border-bottom: 1px solid {'rgba(255,255,255,0.03)' if DARK else 'rgba(99,102,241,0.06)'};
    font-family: 'JetBrains Mono', monospace;
}}
.admin-rank {{ color: #6366f1; font-weight: 600; }}
.admin-page-val {{ color: {TEXT3}; }}
.admin-text-val {{ color: {TEXT3}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

.metric-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px; padding: 12px 14px; text-align: center; margin-bottom: 8px;
}}
.metric-val {{ font-size: 22px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }}
.metric-lbl {{ font-size: 10px; color: {TEXT3}; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.06em; }}

/* Upload zone on main page */
.upload-main {{
    background: {'rgba(99,102,241,0.05)' if DARK else 'rgba(99,102,241,0.03)'};
    border: 2px dashed rgba(99,102,241,0.3);
    border-radius: 20px; padding: 2.5rem 2rem;
    text-align: center; margin: 1.5rem auto;
    max-width: 560px;
    transition: border-color 0.2s;
}}
.upload-main:hover {{ border-color: rgba(99,102,241,0.55); }}

.doc-indicator {{
    width: 9px; height: 9px; border-radius: 50%;
    background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.6);
    flex-shrink: 0; animation: pulse 2s infinite; display:inline-block;
}}
@keyframes pulse {{
    0%,100% {{ box-shadow: 0 0 8px rgba(16,185,129,0.6); }}
    50% {{ box-shadow: 0 0 16px rgba(16,185,129,0.9); }}
}}

.main-header {{
    display: flex; align-items: center; gap: 12px;
    padding: 0 0 1.2rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 1.5rem;
}}
.streamlit-expanderHeader {{
    background: {'rgba(10,18,40,0.6)' if DARK else 'rgba(238,242,255,0.8)'} !important;
    border: 1px solid rgba(16,185,129,0.15) !important;
    border-radius: 8px !important;
    color: #10b981 !important; font-size: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
}}
hr {{ border-color: {BORDER} !important; }}

.feature-pill {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 500; margin: 4px;
}}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=10)
        return r.json() if r.ok else None
    except: return None

def api_post(path, **kwargs):
    try:
        r = requests.post(f"{API_BASE}{path}", timeout=90, **kwargs)
        return r.json() if r.ok else None
    except: return None

def score_color(v):
    if v >= 0.7: return "#10b981"
    if v >= 0.4: return "#f59e0b"
    return "#f43f5e"

def score_badge_class(v):
    if v >= 0.7: return "badge-green"
    if v >= 0.4: return "badge-yellow"
    return "badge-red"

def render_badges(ev):
    f = ev.get("faithfulness", 0)
    c = ev.get("confidence", 0)
    r = ev.get("hallucination_risk", "unknown")
    s = ev.get("top_similarity", 0)
    risk_icon = {"low":"🟢","medium":"🟡","high":"🔴"}.get(r,"⚪")
    st.markdown(f"""
    <div class="badges-row">
        <span class="badge {score_badge_class(f)}">⬡ Faith {f:.2f}</span>
        <span class="badge {score_badge_class(c)}">◎ Conf {c:.2f}</span>
        <span class="badge badge-cyan">◈ Sim {s:.2f}</span>
        <span class="badge {'badge-green' if r=='low' else 'badge-yellow' if r=='medium' else 'badge-red'}">{risk_icon} {r.upper()}</span>
    </div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="logo-wrap">
        <div class="logo-icon">📜</div>
        <div>
            <div class="logo-text">VeriDoc AI</div>
            <div class="logo-sub">RAG · CITE · EVALUATE</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Dark/Light toggle
    st.markdown('<div class="sec-label">Appearance</div>', unsafe_allow_html=True)
    mode_label = "🌙 Dark mode" if DARK else "☀️ Light mode"
    if st.toggle(mode_label, value=DARK, key="dark_toggle"):
        st.session_state.dark_mode = True
    else:
        st.session_state.dark_mode = False
    if st.session_state.dark_mode != DARK:
        st.rerun()

    # Documents list
    st.markdown('<div class="sec-label">Documents</div>', unsafe_allow_html=True)
    docs_data = api_get("/documents")
    if docs_data and docs_data.get("documents"):
        for doc in docs_data["documents"]:
            is_active = doc["doc_id"] == st.session_state.active_doc
            label = f"{'▶  ' if is_active else ''}{doc['filename']}"
            if st.button(label, key=f"doc_{doc['doc_id']}", use_container_width=True):
                st.session_state.active_doc = doc["doc_id"]
                st.session_state.active_doc_name = doc["filename"]
                st.session_state.messages = []
                st.rerun()
            st.markdown(
                f'<div style="font-size:11px;color:{TEXT3};margin:-4px 0 6px 4px;font-family:JetBrains Mono,monospace;">'
                f'{doc["total_pages"]}p · {doc["total_chunks"]} chunks</div>',
                unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:12px;color:{TEXT3};padding:6px 2px;">No documents yet.</div>', unsafe_allow_html=True)

    # Settings
    st.markdown('<div class="sec-label" style="margin-top:1rem;">Query Settings</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["en","hi","te","ta"],
        format_func=lambda x: {"en":"🇬🇧 English","hi":"🇮🇳 Hindi","te":"🇮🇳 Telugu","ta":"🇮🇳 Tamil"}[x],
        label_visibility="collapsed")
    top_k = st.slider("Chunks to retrieve", 2, 8, 5)
    run_eval = st.toggle("RAGAS evaluation", value=True)
    st.session_state.admin_mode = st.toggle("Admin view", value=st.session_state.admin_mode)

# ── Main ──────────────────────────────────────────────────────────────────────
if not st.session_state.active_doc:
    # Landing — upload in center
    st.markdown(f"""
    <div style="text-align:center; padding: 3rem 1rem 1rem;">
        <div style="font-size:50px; margin-bottom:1rem; filter:drop-shadow(0 0 20px rgba(99,102,241,0.5));">📜</div>
        <div style="font-size:30px; font-weight:700; color:{TEXT}; letter-spacing:-0.5px; margin-bottom:0.5rem;">
            Ask anything about your
            <span style="background:linear-gradient(135deg,#6366f1,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                documents
            </span>
        </div>
        <div style="font-size:14px; color:{TEXT2}; margin-bottom:2rem; line-height:1.7;">
            Upload government schemes, legal notices, college circulars, or policy PDFs.<br>
            Get cited answers with hallucination scores — in English, Hindi, Telugu or Tamil.
        </div>
        <div style="margin-bottom:2rem;">
            <span class="feature-pill" style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);color:#818cf8;">📎 PDF Upload</span>
            <span class="feature-pill" style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);color:#34d399;">🔍 Vector Search</span>
            <span class="feature-pill" style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);color:#fbbf24;">📊 RAGAS Eval</span>
            <span class="feature-pill" style="background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);color:#a78bfa;">✦ Citations</span>
            <span class="feature-pill" style="background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.2);color:#22d3ee;">🌐 Multilingual</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Upload zone in center of main page
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<div style="font-size:13px;font-weight:600;color:{TEXT2};text-align:center;margin-bottom:0.5rem;">Upload your PDF to get started</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            with st.spinner("Parsing & indexing document..."):
                result = api_post("/upload", files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")})
            if result:
                st.success(f"✓ Indexed: {uploaded.name}")
                st.session_state.active_doc = result["doc_id"]
                st.session_state.active_doc_name = uploaded.name
                st.session_state.messages = []
                st.rerun()
            else:
                st.error("Upload failed — is the API server running?")

        st.markdown(f'<div style="text-align:center;font-size:12px;color:{TEXT3};margin-top:0.5rem;">or select an existing document from the sidebar</div>', unsafe_allow_html=True)

else:
    # ── Active document view ──────────────────────────────────────────────────
    if st.session_state.admin_mode:
        chat_col, admin_col = st.columns([3, 2])
    else:
        chat_col = st.container()
        admin_col = None

    with chat_col:
        st.markdown(f"""
        <div class="main-header">
            <div class="doc-indicator"></div>
            <div style="font-size:13px;color:{TEXT2};font-family:'JetBrains Mono',monospace;">{st.session_state.active_doc_name}</div>
            <div style="font-size:11px;color:{TEXT3};font-family:'JetBrains Mono',monospace;">· {st.session_state.active_doc[:8]}</div>
            <div style="margin-left:auto;">
        """, unsafe_allow_html=True)

        # Upload new doc button inline
        with st.expander("+ Upload new document", expanded=False):
            new_upload = st.file_uploader("New PDF", type=["pdf"], label_visibility="collapsed", key="new_upload")
            if new_upload:
                with st.spinner("Indexing..."):
                    result = api_post("/upload", files={"file": (new_upload.name, new_upload.getvalue(), "application/pdf")})
                if result:
                    st.success(f"✓ {new_upload.name}")
                    st.session_state.active_doc = result["doc_id"]
                    st.session_state.active_doc_name = new_upload.name
                    st.session_state.messages = []
                    st.rerun()

        # Empty state
        if not st.session_state.messages:
            st.markdown(f"""
            <div style="text-align:center;padding:3rem 1rem 1rem;">
                <div style="font-size:30px;margin-bottom:0.75rem;">💬</div>
                <div style="font-size:15px;color:{TEXT2};margin-bottom:0.5rem;">Document ready</div>
                <div style="font-size:13px;color:{TEXT3};">Ask a question below to get a cited answer</div>
            </div>""", unsafe_allow_html=True)

        # Chat messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-user">
                    <div class="msg-user-label">You</div>
                    {msg["content"]}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-ai">
                    <div class="msg-ai-label">◆ VeriDoc AI</div>
                    {msg["content"]}
                </div>""", unsafe_allow_html=True)

                if msg.get("citations"):
                    with st.expander(f"📎 {len(msg['citations'])} source citations", expanded=False):
                        for c in msg["citations"]:
                            st.markdown(f"""
                            <div class="citation-wrap">
                                <div class="citation-header">
                                    <div class="citation-rank">{c['rank']}</div>
                                    <div class="citation-meta">Page {c['page']} · {c['source_file']}</div>
                                    <div class="citation-score">{c['similarity_score']:.3f}</div>
                                </div>
                                <div class="citation-text">{c['text'][:280]}...</div>
                            </div>""", unsafe_allow_html=True)

                if msg.get("evaluation"):
                    render_badges(msg["evaluation"])

        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                question = st.text_input("q", placeholder="Ask a question about this document...", label_visibility="collapsed")
            with col2:
                submitted = st.form_submit_button("Ask →", use_container_width=True)

        if submitted and question.strip():
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Searching document..."):
                result = api_post("/query", json={
                    "doc_id": st.session_state.active_doc,
                    "question": question,
                    "k": top_k,
                    "language": language,
                    "run_eval": run_eval,
                })
            if result:
                st.session_state.last_response = result
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "citations": result.get("citations", []),
                    "evaluation": result.get("evaluation"),
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⚠️ No response — check the API server is running.",
                    "citations": [], "evaluation": None,
                })
            st.rerun()

    # ── Admin panel ───────────────────────────────────────────────────────────
    if st.session_state.admin_mode and admin_col and st.session_state.last_response:
        with admin_col:
            resp = st.session_state.last_response
            st.markdown(f'<div class="sec-label">Retrieved Chunks</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:{CARD_BG};border:1px solid {BORDER};border-radius:10px;overflow:hidden;">
            <div class="admin-header"><span>#</span><span>Score</span><span>Page</span><span>Preview</span></div>
            """, unsafe_allow_html=True)
            for c in resp.get("citations", []):
                sc = score_color(c["similarity_score"])
                preview = c["text"][:55].replace("\n", " ")
                st.markdown(f"""
                <div class="admin-row">
                    <span class="admin-rank">{c['rank']}</span>
                    <span style="color:{sc};font-weight:600;font-family:'JetBrains Mono',monospace;">{c['similarity_score']:.3f}</span>
                    <span class="admin-page-val">p.{c['page']}</span>
                    <span class="admin-text-val">{preview}…</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if resp.get("evaluation"):
                ev = resp["evaluation"]
                st.markdown(f'<div class="sec-label" style="margin-top:1rem;">RAGAS Metrics</div>', unsafe_allow_html=True)
                metrics = [
                    ("Faithfulness", ev.get("faithfulness", 0)),
                    ("Relevancy",    ev.get("answer_relevancy", 0)),
                    ("Confidence",   ev.get("confidence", 0)),
                ]
                cols = st.columns(2)
                for i, (label, val) in enumerate(metrics):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-val" style="color:{score_color(val)};">{val:.2f}</div>
                            <div class="metric-lbl">{label}</div>
                        </div>""", unsafe_allow_html=True)

                risk = ev.get("hallucination_risk", "unknown")
                risk_color = {"low":"#10b981","medium":"#f59e0b","high":"#f43f5e"}.get(risk,"#64748b")
                risk_icon  = {"low":"🟢","medium":"🟡","high":"🔴"}.get(risk,"⚪")
                with cols[1]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-val" style="color:{risk_color};font-size:14px;">{risk_icon} {risk.upper()}</div>
                        <div class="metric-lbl">Hallucination Risk</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f'<div class="sec-label" style="margin-top:1rem;">Raw JSON</div>', unsafe_allow_html=True)
                st.json(resp, expanded=False)
