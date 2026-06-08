"""
VeriDoc AI — Streamlit Frontend
Run: streamlit run ui/app.py
"""

import streamlit as st
import requests
import json
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="VeriDoc AI",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 2rem; max-width: 1200px; }

/* Background */
.stApp {
    background: #0a0e1a;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(56, 100, 255, 0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0, 210, 190, 0.06) 0%, transparent 60%);
}

/* Header */
.veridoc-header {
    display: flex; align-items: center; gap: 16px;
    padding: 1.5rem 0 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2rem;
}
.veridoc-logo {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #3864ff, #00d2be);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
}
.veridoc-title { font-size: 22px; font-weight: 600; color: #f0f4ff; letter-spacing: -0.3px; }
.veridoc-sub { font-size: 12px; color: #5a6a8a; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }

/* Upload area */
.upload-zone {
    border: 1.5px dashed rgba(56, 100, 255, 0.35);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    background: rgba(56, 100, 255, 0.04);
    margin-bottom: 1.5rem;
    transition: border-color 0.2s;
}

/* Doc card */
.doc-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.15s;
}
.doc-card:hover { background: rgba(56,100,255,0.08); border-color: rgba(56,100,255,0.3); }
.doc-card.active { background: rgba(56,100,255,0.12); border-color: rgba(56,100,255,0.5); }
.doc-name { font-size: 13px; font-weight: 500; color: #c8d4f0; }
.doc-meta { font-size: 11px; color: #4a5a7a; margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

/* Chat */
.chat-container { display: flex; flex-direction: column; gap: 16px; }

.msg-user {
    background: rgba(56,100,255,0.12);
    border: 1px solid rgba(56,100,255,0.2);
    border-radius: 14px 14px 4px 14px;
    padding: 12px 16px;
    margin-left: 20%;
    color: #c8d4f0;
    font-size: 14px;
    line-height: 1.6;
}

.msg-ai {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px 14px 14px 14px;
    padding: 14px 18px;
    margin-right: 10%;
    color: #d0daf0;
    font-size: 14px;
    line-height: 1.7;
}

.msg-label {
    font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
    color: #3864ff;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    font-weight: 500;
}

/* Citation card */
.citation-card {
    background: rgba(0,210,190,0.05);
    border: 1px solid rgba(0,210,190,0.15);
    border-left: 3px solid #00d2be;
    border-radius: 0 8px 8px 0;
    padding: 8px 12px;
    margin: 6px 0;
    font-size: 12px;
    color: #7a9ab0;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.5;
}
.citation-header {
    color: #00d2be;
    font-weight: 500;
    margin-bottom: 4px;
    font-size: 11px;
}
.citation-text { color: #6a8a9a; }

/* Score badges */
.score-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.score-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
}
.score-green { background: rgba(0,200,100,0.1); color: #00c864; border: 1px solid rgba(0,200,100,0.2); }
.score-yellow { background: rgba(255,180,0,0.1); color: #ffb400; border: 1px solid rgba(255,180,0,0.2); }
.score-red { background: rgba(255,60,60,0.1); color: #ff3c3c; border: 1px solid rgba(255,60,60,0.2); }
.score-blue { background: rgba(56,100,255,0.1); color: #6890ff; border: 1px solid rgba(56,100,255,0.2); }

/* Input */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #c8d4f0 !important;
    font-family: 'Sora', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(56,100,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(56,100,255,0.1) !important;
}

/* Button */
.stButton button {
    background: linear-gradient(135deg, #3864ff, #2a50d0) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.15s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

/* Metrics */
.metric-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.metric-val { font-size: 24px; font-weight: 600; color: #c8d4f0; font-family: 'JetBrains Mono', monospace; }
.metric-lbl { font-size: 11px; color: #4a5a7a; margin-top: 4px; }

/* Spinner */
.stSpinner { color: #3864ff !important; }

/* Selectbox */
.stSelectbox select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #c8d4f0 !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Section labels */
.section-label {
    font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
    color: #3a4a6a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 10px;
    font-weight: 500;
}

/* Risk pill */
.risk-low { color: #00c864; }
.risk-medium { color: #ffb400; }
.risk-high { color: #ff3c3c; }

/* Admin panel */
.admin-row {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
}
.admin-rank { color: #3864ff; width: 20px; flex-shrink: 0; }
.admin-score { color: #00d2be; width: 50px; flex-shrink: 0; }
.admin-page { color: #5a6a8a; width: 50px; flex-shrink: 0; }
.admin-text { color: #5a7a8a; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_doc" not in st.session_state:
    st.session_state.active_doc = None
if "active_doc_name" not in st.session_state:
    st.session_state.active_doc_name = None
if "last_response" not in st.session_state:
    st.session_state.last_response = None
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def api_get(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=10)
        return r.json() if r.ok else None
    except Exception:
        return None

def api_post(path, **kwargs):
    try:
        r = requests.post(f"{API_BASE}{path}", timeout=60, **kwargs)
        return r.json() if r.ok else None
    except Exception:
        return None

def risk_html(risk: str) -> str:
    icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}
    return f'{icons.get(risk,"⚪")} {risk.upper()}'

def score_class(val: float) -> str:
    if val >= 0.7: return "score-green"
    if val >= 0.4: return "score-yellow"
    return "score-red"

def render_score_badges(evaluation: dict):
    faith = evaluation.get("faithfulness", 0)
    conf  = evaluation.get("confidence", 0)
    risk  = evaluation.get("hallucination_risk", "unknown")
    sim   = evaluation.get("top_similarity", 0)

    badges = f"""
    <div class="score-row">
        <span class="score-badge {score_class(faith)}">Faith {faith:.2f}</span>
        <span class="score-badge {score_class(conf)}">Conf {conf:.2f}</span>
        <span class="score-badge score-blue">Sim {sim:.2f}</span>
        <span class="score-badge {'score-green' if risk=='low' else 'score-yellow' if risk=='medium' else 'score-red'}">
            {risk_html(risk)}
        </span>
    </div>"""
    st.markdown(badges, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="veridoc-header">
        <div class="veridoc-logo">📜</div>
        <div>
            <div class="veridoc-title">VeriDoc AI</div>
            <div class="veridoc-sub">RAG · Citations · Eval</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="section-label">Upload Document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload PDF", type=["pdf"], label_visibility="collapsed"
    )

    if uploaded:
        with st.spinner("Parsing & indexing..."):
            result = api_post(
                "/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), "application/pdf")},
            )
        if result:
            st.success(f"✓ Indexed: {uploaded.name}")
            st.session_state.active_doc = result["doc_id"]
            st.session_state.active_doc_name = uploaded.name
            st.session_state.messages = []
        else:
            st.error("Upload failed. Is the API running?")

    st.markdown("<br>", unsafe_allow_html=True)

    # Document list
    st.markdown('<div class="section-label">Documents</div>', unsafe_allow_html=True)
    docs_data = api_get("/documents")
    if docs_data and docs_data.get("documents"):
        for doc in docs_data["documents"]:
            is_active = doc["doc_id"] == st.session_state.active_doc
            card_class = "doc-card active" if is_active else "doc-card"
            if st.button(
                f"{'▶ ' if is_active else ''}{doc['filename']}",
                key=f"doc_{doc['doc_id']}",
                use_container_width=True,
            ):
                st.session_state.active_doc = doc["doc_id"]
                st.session_state.active_doc_name = doc["filename"]
                st.session_state.messages = []
                st.rerun()
            st.markdown(
                f'<div style="font-size:11px;color:#3a4a6a;margin:-6px 0 6px 4px;font-family:JetBrains Mono,monospace;">'
                f'{doc["total_pages"]}p · {doc["total_chunks"]} chunks</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="font-size:12px;color:#3a4a6a;padding:8px 0;">No documents yet.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Settings
    st.markdown('<div class="section-label">Settings</div>', unsafe_allow_html=True)
    language = st.selectbox(
        "Response language",
        ["en", "hi", "te", "ta"],
        format_func=lambda x: {"en":"English","hi":"Hindi","te":"Telugu","ta":"Tamil"}[x],
        label_visibility="collapsed",
    )
    top_k = st.slider("Chunks to retrieve", 2, 8, 5)
    run_eval = st.toggle("Run RAGAS evaluation", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.session_state.admin_mode = st.toggle("Admin view", value=st.session_state.admin_mode)


# ── Main area ─────────────────────────────────────────────────────────────────

if not st.session_state.active_doc:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;">
        <div style="font-size:48px;margin-bottom:1rem;">📜</div>
        <div style="font-size:28px;font-weight:600;color:#c8d4f0;margin-bottom:0.5rem;">VeriDoc AI</div>
        <div style="font-size:15px;color:#4a5a7a;margin-bottom:2rem;">
            Multilingual RAG assistant for legal, government & college documents
        </div>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
            <span style="background:rgba(56,100,255,0.1);border:1px solid rgba(56,100,255,0.2);
                border-radius:20px;padding:6px 14px;font-size:12px;color:#6890ff;">
                📎 PDF Upload
            </span>
            <span style="background:rgba(0,210,190,0.1);border:1px solid rgba(0,210,190,0.2);
                border-radius:20px;padding:6px 14px;font-size:12px;color:#00d2be;">
                🔍 Semantic Search
            </span>
            <span style="background:rgba(255,180,0,0.1);border:1px solid rgba(255,180,0,0.2);
                border-radius:20px;padding:6px 14px;font-size:12px;color:#ffb400;">
                📊 RAGAS Evaluation
            </span>
            <span style="background:rgba(180,100,255,0.1);border:1px solid rgba(180,100,255,0.2);
                border-radius:20px;padding:6px 14px;font-size:12px;color:#c878ff;">
                🌐 Multilingual
            </span>
        </div>
        <div style="margin-top:3rem;font-size:13px;color:#3a4a6a;">
            ← Upload a PDF in the sidebar to get started
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Active document — split into chat + admin
    if st.session_state.admin_mode:
        chat_col, admin_col = st.columns([3, 2])
    else:
        chat_col = st.container()
        admin_col = None

    with chat_col:
        # Document header
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;">
            <div style="width:8px;height:8px;border-radius:50%;background:#00c864;flex-shrink:0;"></div>
            <div style="font-size:13px;color:#7a9ab0;font-family:'JetBrains Mono',monospace;">
                {st.session_state.active_doc_name}
            </div>
            <div style="font-size:11px;color:#2a3a5a;font-family:'JetBrains Mono',monospace;">
                · {st.session_state.active_doc[:8]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-user">
                    <div class="msg-label">You</div>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-ai">
                    <div class="msg-label">VeriDoc AI</div>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)

                # Citations
                if msg.get("citations"):
                    with st.expander(f"📎 {len(msg['citations'])} source citations", expanded=False):
                        for c in msg["citations"]:
                            st.markdown(f"""
                            <div class="citation-card">
                                <div class="citation-header">
                                    Page {c['page']} · {c['source_file']} · score {c['similarity_score']:.3f}
                                </div>
                                <div class="citation-text">{c['text'][:250]}...</div>
                            </div>
                            """, unsafe_allow_html=True)

                # Evaluation scores
                if msg.get("evaluation"):
                    render_score_badges(msg["evaluation"])

        # Input
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            question = st.text_input(
                "Ask a question",
                placeholder="e.g. Who is eligible for this scheme?",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Ask →", use_container_width=False)

        if submitted and question.strip():
            # Add user message
            st.session_state.messages.append({"role": "user", "content": question})

            with st.spinner("Searching document..."):
                result = api_post(
                    "/query",
                    json={
                        "doc_id": st.session_state.active_doc,
                        "question": question,
                        "k": top_k,
                        "language": language,
                        "run_eval": run_eval,
                    },
                )

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
                    "content": "⚠️ Could not get a response. Please check the API is running.",
                    "citations": [],
                    "evaluation": None,
                })

            st.rerun()

    # Admin panel
    if st.session_state.admin_mode and admin_col and st.session_state.last_response:
        with admin_col:
            resp = st.session_state.last_response

            st.markdown('<div class="section-label">Admin · Retrieved Chunks</div>', unsafe_allow_html=True)

            # Chunk table
            st.markdown("""
            <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.06);border-radius:10px;overflow:hidden;">
            <div class="admin-row" style="color:#2a3a5a;border-bottom:1px solid rgba(255,255,255,0.08);">
                <span class="admin-rank">#</span>
                <span class="admin-score">Score</span>
                <span class="admin-page">Page</span>
                <span class="admin-text">Preview</span>
            </div>
            """, unsafe_allow_html=True)

            for c in resp.get("citations", []):
                preview = c["text"][:60].replace("\n", " ")
                st.markdown(f"""
                <div class="admin-row">
                    <span class="admin-rank">{c['rank']}</span>
                    <span class="admin-score">{c['similarity_score']:.3f}</span>
                    <span class="admin-page">p.{c['page']}</span>
                    <span class="admin-text">{preview}…</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Eval metrics
            if resp.get("evaluation"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">RAGAS Evaluation</div>', unsafe_allow_html=True)

                ev = resp["evaluation"]
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-val">{ev['faithfulness']:.2f}</div>
                        <div class="metric-lbl">Faithfulness</div>
                    </div>""", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-val">{ev['answer_relevancy']:.2f}</div>
                        <div class="metric-lbl">Relevancy</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                m3, m4 = st.columns(2)
                with m3:
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-val">{ev['confidence']:.2f}</div>
                        <div class="metric-lbl">Confidence</div>
                    </div>""", unsafe_allow_html=True)
                with m4:
                    risk = ev['hallucination_risk']
                    risk_color = {"low":"#00c864","medium":"#ffb400","high":"#ff3c3c"}.get(risk,"#888")
                    st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-val" style="color:{risk_color};font-size:16px;">
                            {'🟢' if risk=='low' else '🟡' if risk=='medium' else '🔴'} {risk.upper()}
                        </div>
                        <div class="metric-lbl">Hallucination Risk</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">Raw Response</div>', unsafe_allow_html=True)
                st.json(resp)
