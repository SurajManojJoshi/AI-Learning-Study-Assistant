"""
AI Learning & Study Assistant
Pages:
  🏠 Dashboard        — overview + quick document Q&A
  📚 Study Materials  — upload & manage PDFs
  🤖 AI Tutor         — full chat with RAG or general Gemini
  📝 Quiz             — AI-generated MCQ quiz
  📅 Study Plan       — day-by-day exam schedule
  🗺️ Learning Pathways — structured topic roadmaps
"""

import time
from datetime import date, timedelta
import streamlit as st

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

import config
import rag
import quiz
import memory
import study_plan
import learning_pathways as lp
import ui_components as ui

ui.inject_css()

# ─────────────────────────────────────────────────────────────────────────────
PAGES = [
    "🏠 Dashboard",
    "📚 Study Materials",
    "🤖 AI Tutor",
    "📝 Quiz",
    "📅 Study Plan",
    "🗺️ Learning Pathways",
    "▶️ YouTube Notes",
    "📖 Wikipedia Q&A",
]

_defaults = {
    "page":          "🏠 Dashboard",
    "nav_sel":       "🏠 Dashboard",
    "tutor_history": [],
    "prefill":       "",
    "current_quiz":  None,
    "quiz_answers":  {},
    "quiz_results":  None,
    "quiz_topic":    "",
    "quiz_idx":      0,
    "quiz_run":      0,
    "study_plan":    None,
    "done_days":     set(),
    "pathway_result": None,
    "pathway_topic": "",
    # learning pathways tabs
    "roadmap_text":    "",
    "roadmap_topic":   "",
    "lesson_topic_active": "",
    "lesson_stages":        [],
    "lesson_pathway_text":  "",
    "lesson_current_subtopic": None,
    "lesson_content":       "",
    "yt_channels":     [],
    "yt_ch_searched":  "",
    "websites":        [],
    "web_searched":    "",
    "wiki_data":       {},
    "wiki_answer":     "",
    "wiki_q_asked":    "",
    "yt_notes_result": None,
    # dashboard quick-ask
    "dash_answer":   "",
    "dash_sources":  [],
    "dash_question": "",
    # study materials Q&A
    "sm_last_q":   "",
    "sm_last_ans": "",
    "sm_last_src": [],
    "sm_pending_q": "",
    "sm_just_uploaded": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go(page: str):
    st.session_state.page = page
    st.session_state.nav_sel = page
    st.rerun()


def on_nav():
    st.session_state.page = st.session_state.nav_sel


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 StudyAssistant")
    st.caption("AI-powered learning companion")
    st.divider()

    st.radio(
        "Navigate",
        PAGES,
        key="nav_sel",
        on_change=on_nav,
        label_visibility="collapsed",
    )

    st.divider()
    _vs = rag.get_vector_store_status()
    st.markdown(
        f"**Index:** {'🟢 Ready' if _vs['is_ready'] else '🔴 Empty'}  \n"
        f"📄 {len(_vs['indexed_files'])} file(s) · {_vs['total_chunks']} chunks"
    )
    if not config.is_gemini_configured():
        st.warning("⚠️ No Gemini API key")


# ══════════════════════════════════════════════════════════════════════════════
# 🏠  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "🏠 Dashboard":

    st.title("🎓 AI Study Assistant")
    st.caption("Your personal AI-powered learning companion.")

    # ── API key notice ─────────────────────────────────────────────────────────
    if not config.is_gemini_configured():
        st.warning(
            "⚠️ **Gemini API key not set.** "
            "Open `.env` and add `GEMINI_API_KEY=your_key` then restart the app."
        )

    # ── 4 stat tiles ──────────────────────────────────────────────────────────
    vs    = rag.get_vector_store_status()
    prog  = memory.get_progress_summary()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📚 PDFs indexed",   len(vs["indexed_files"]))
    with c2:
        st.metric("💬 Questions asked", prog.get("total_questions_asked", 0))
    with c3:
        st.metric("📝 Quizzes taken",   prog.get("total_quizzes_taken", 0))
    with c4:
        st.metric("🎯 Avg quiz score",  f"{prog.get('average_quiz_score', 0.0)}%")

    st.divider()

    # ── Navigation buttons ─────────────────────────────────────────────────────
    st.subheader("What do you want to do?")
    b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
    with b1:
        if st.button("📚 Materials", use_container_width=True):
            go("📚 Study Materials")
    with b2:
        if st.button("🤖 AI Tutor", use_container_width=True):
            go("🤖 AI Tutor")
    with b3:
        if st.button("📝 Quiz", use_container_width=True):
            go("📝 Quiz")
    with b4:
        if st.button("📅 Study Plan", use_container_width=True):
            go("📅 Study Plan")
    with b5:
        if st.button("🗺️ Pathways", use_container_width=True):
            go("🗺️ Learning Pathways")
    with b6:
        if st.button("▶️ YT Notes", use_container_width=True):
            go("▶️ YouTube Notes")
    with b7:
        if st.button("📖 Wikipedia", use_container_width=True):
            go("📖 Wikipedia Q&A")

    st.divider()

    # ── QUICK DOCUMENT Q&A  (main dashboard feature) ───────────────────────────
    st.subheader("📄 Quick Document Q&A")
    st.caption(
        "Ask any question about your uploaded PDFs right here. "
        "For a full conversation, use the **🤖 AI Tutor** page."
    )

    if not vs["is_ready"]:
        st.info("📁 No study materials indexed yet. Go to **📚 Study Materials** to upload a PDF first.")
    else:
        # Preset question chips
        pc1, pc2, pc3, pc4 = st.columns(4)
        quick_q = None
        with pc1:
            if st.button("📌 Summarize material", key="dq1", use_container_width=True):
                quick_q = "Summarize the main topics covered in the uploaded material."
        with pc2:
            if st.button("💡 Key definitions", key="dq2", use_container_width=True):
                quick_q = "List the key definitions and important terms from the material."
        with pc3:
            if st.button("🎯 Exam points", key="dq3", use_container_width=True):
                quick_q = "What are the most important points I should study for an exam?"
        with pc4:
            if st.button("🔍 Give examples", key="dq4", use_container_width=True):
                quick_q = "Give me practical examples explained in the material."

        # Text input
        typed_q = st.text_input(
            "Or type your own question:",
            placeholder="e.g. What is the OSI model? How does TCP/IP work?",
            key="dash_q_input",
        )

        ask_q = quick_q or (typed_q.strip() if typed_q.strip() else "")

        if ask_q and st.button("🔎 Get Answer", type="primary"):
            if not config.is_gemini_configured():
                st.error("❌ Gemini API key not configured.")
            else:
                with st.spinner("Searching your documents and generating answer…"):
                    try:
                        result = rag.answer_question(ask_q)
                        st.session_state.dash_answer   = result.get("answer", "")
                        st.session_state.dash_sources  = result.get("sources", [])
                        st.session_state.dash_question = ask_q
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Show answer
        if st.session_state.dash_answer:
            st.markdown(f"**Q: {st.session_state.dash_question}**")
            st.markdown(st.session_state.dash_answer)

            if st.session_state.dash_sources:
                with st.expander("📎 Sources from your documents", expanded=False):
                    for s in st.session_state.dash_sources:
                        st.caption(
                            f"📄 **{s.get('file_name','Doc')}** · "
                            f"Page {s.get('page', 1)} · "
                            f"Score {s.get('score', 0):.3f}"
                        )
                        st.markdown(f"> {s.get('snippet', '')[:300]}…")

            col_clear, col_tutor = st.columns(2)
            with col_clear:
                if st.button("🗑️ Clear answer", use_container_width=True):
                    st.session_state.dash_answer   = ""
                    st.session_state.dash_sources  = []
                    st.session_state.dash_question = ""
                    st.rerun()
            with col_tutor:
                if st.button("🤖 Continue in AI Tutor", use_container_width=True):
                    st.session_state.prefill = st.session_state.dash_question
                    go("🤖 AI Tutor")

    st.divider()

    # ── Document summary list ──────────────────────────────────────────────────
    st.subheader("📚 Your Indexed Documents")
    docs = rag.get_indexed_files_details()
    if docs:
        for d in docs:
            st.markdown(
                f"- 📘 **{d['file_name']}** — "
                f"{d['total_pages']} pages · {d['total_chunks']} chunks · ✅ Ready"
            )
    else:
        st.caption("No documents indexed. Upload a PDF in Study Materials.")

    st.divider()

    # ── Recent questions & weak topics ────────────────────────────────────────
    l, r = st.columns(2)
    with l:
        st.subheader("🕒 Recent Questions")
        recent = prog.get("recent_questions", [])
        if recent:
            for item in recent[:5]:
                q_text = item["question"]
                short  = q_text[:75] + "…" if len(q_text) > 75 else q_text
                st.markdown(
                    f"- **{short}**  \n"
                    f"  <small style='color:gray;'>{item.get('topic','General')} · "
                    f"{item.get('timestamp','')}</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No questions asked yet.")

    with r:
        st.subheader("⚠️ Weak Topics")
        weak = prog.get("weak_topics", [])
        if weak:
            for wt in weak[:6]:
                st.markdown(f"- 🔴 {wt}")
            st.caption("Take a quiz to work on these.")
        else:
            st.success("🎉 No weak topics detected yet.")


# ══════════════════════════════════════════════════════════════════════════════
# 📚  STUDY MATERIALS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📚 Study Materials":
    ui.page_banner(
        "📚 Study Materials",
        "Upload your PDFs, then ask questions directly from them.",
    )

    # ── STEP 1: Upload ─────────────────────────────────────────────────────────
    st.subheader("Step 1 — Upload a PDF")
    col_up, col_lib = st.columns([1.6, 1])

    with col_up:
        uploaded = st.file_uploader(
            "Select PDF files (notes, textbooks, slides)",
            type=["pdf"],
            accept_multiple_files=True,
            key="sm_uploader",
        )

        if uploaded:
            st.info(f"📁 {len(uploaded)} file(s) ready to index.")
            if st.button("🚀 Process & Index", type="primary", use_container_width=True, key="sm_process"):
                results = []
                for uf in uploaded:
                    save_path = config.UPLOADS_DIR / uf.name
                    try:
                        with open(save_path, "wb") as f:
                            f.write(uf.getbuffer())
                        with st.spinner(f"Indexing {uf.name}…"):
                            result = rag.process_and_index_pdf(save_path, uf.name)
                        results.append({
                            "name": uf.name,
                            "ok": True,
                            "pages": result["total_pages"],
                            "chunks": result["total_chunks"],
                        })
                    except ValueError as ve:
                        results.append({"name": uf.name, "ok": False, "error": str(ve)})
                    except Exception as ex:
                        results.append({"name": uf.name, "ok": False, "error": str(ex)})

                # Show summary of all results
                for r in results:
                    if r["ok"]:
                        st.success(f"✅ {r['name']} — {r['pages']} pages, {r['chunks']} chunks indexed")
                    else:
                        st.error(f"❌ {r['name']}: {r['error']}")

                # Refresh the page so the library updates
                ok_count = sum(1 for r in results if r["ok"])
                if ok_count > 0:
                    st.session_state["sm_just_uploaded"] = True
                    time.sleep(1.5)  # let user see the success message
                    st.rerun()
        else:
            st.caption("👆 Drag and drop or browse for a PDF above.")

    with col_lib:
        st.subheader("Indexed Documents")
        docs = rag.get_indexed_files_details()
        if docs:
            for d in docs:
                ui.doc_card(d["file_name"], d["total_pages"], d["total_chunks"])
            if st.button("🗑️ Clear All", use_container_width=True, key="sm_clear_idx"):
                rag.clear_vector_store()
                st.success("All indexed data cleared.")
                st.rerun()
        else:
            st.caption("No documents indexed yet.")

    st.divider()

    # ── STEP 2: Ask questions from the document ────────────────────────────────
    st.subheader("Step 2 — Ask Questions About Your Documents")

    vs_status = rag.get_vector_store_status()
    if not vs_status["is_ready"]:
        st.warning("📂 Upload and index a PDF first (Step 1) to enable document Q&A.")
    else:
        st.caption(
            f"📄 Searching across **{len(vs_status['indexed_files'])}** document(s) · "
            f"**{vs_status['total_chunks']}** indexed chunks"
        )

        # Quick preset chips — store in session state so they survive the rerun
        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1:
            if st.button("📋 Summarize", key="sm_sum", use_container_width=True):
                st.session_state["sm_pending_q"] = "Summarize the main topics and key points from the uploaded document."
        with qc2:
            if st.button("📖 Key terms", key="sm_kw", use_container_width=True):
                st.session_state["sm_pending_q"] = "List and define the most important terms and concepts from the document."
        with qc3:
            if st.button("🎯 Exam tips", key="sm_ex", use_container_width=True):
                st.session_state["sm_pending_q"] = "What are the most important points I should know for an exam on this material?"
        with qc4:
            if st.button("🔍 Examples", key="sm_eg", use_container_width=True):
                st.session_state["sm_pending_q"] = "Give me practical examples that are explained in the document."

        # Free text question — if user types, it overrides any preset
        doc_q = st.text_input(
            "Type your question:",
            placeholder="e.g.  What is normalization?  Explain the TCP handshake.",
            key="sm_question",
        )

        # Determine which question is active
        # Priority: typed text > preset from session state
        active_q = doc_q.strip() or st.session_state.get("sm_pending_q", "")

        # Always show the Get Answer button when docs are ready
        if st.button("🔎 Get Answer", type="primary", use_container_width=True, key="sm_ask"):
            q_to_ask = doc_q.strip() or st.session_state.get("sm_pending_q", "")
            if not q_to_ask:
                st.warning("Please type a question or click a preset above.")
            elif not config.is_gemini_configured():
                st.error("❌ Gemini API key not configured. Add it to `.env`.")
            else:
                with st.spinner("Reading your documents and generating answer…"):
                    try:
                        res = rag.answer_question(q_to_ask)
                        st.session_state["sm_last_q"]   = q_to_ask
                        st.session_state["sm_last_ans"]  = res.get("answer", "No answer received.")
                        st.session_state["sm_last_src"]  = res.get("sources", [])
                    except Exception as e:
                        st.error(f"Error: {e}")
                # Clear the pending preset so it doesn't get reused
                st.session_state["sm_pending_q"] = ""
                st.rerun()

        # Display the last answer
        if st.session_state.get("sm_last_ans"):
            st.markdown("---")
            st.markdown(f"**Question:** {st.session_state['sm_last_q']}")
            st.markdown("**Answer:**")
            st.markdown(st.session_state["sm_last_ans"])

            srcs = st.session_state.get("sm_last_src", [])
            if srcs:
                with st.expander(f"📎 Sources ({len(srcs)} chunks used)", expanded=False):
                    for s in srcs:
                        st.markdown(
                            f"**{s.get('file_name','Doc')}** · "
                            f"Page {s.get('page',1)} · "
                            f"Relevance {s.get('score',0):.2f}"
                        )
                        st.caption(s.get("snippet", "")[:280] + "…")
                        st.divider()

            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ Clear answer", key="sm_clr", use_container_width=True):
                    st.session_state["sm_last_q"]   = ""
                    st.session_state["sm_last_ans"]  = ""
                    st.session_state["sm_last_src"]  = []
                    st.session_state["sm_pending_q"] = ""
                    st.rerun()
            with c2:
                if st.button("🤖 Continue in AI Tutor", key="sm_tutor", use_container_width=True):
                    st.session_state.prefill = st.session_state["sm_last_q"]
                    go("🤖 AI Tutor")


# ══════════════════════════════════════════════════════════════════════════════
# 🤖  AI TUTOR
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "🤖 AI Tutor":
    ui.page_banner(
        "🤖 AI Tutor",
        "Ask anything about your study materials or any topic. Full conversation history.",
    )

    if st.button("🧹 Clear chat"):
        st.session_state.tutor_history = []
        st.session_state.prefill = ""
        st.rerun()

    # Suggested chips
    st.caption("Quick prompts:")
    ch1, ch2, ch3, ch4 = st.columns(4)
    chip = None
    with ch1:
        if st.button("📌 Topic overview", use_container_width=True, key="chip1"):
            chip = "Give me an overview of the main topics in the uploaded material."
    with ch2:
        if st.button("💡 Explain simply", use_container_width=True, key="chip2"):
            chip = "Explain the key concepts in very simple terms with analogies."
    with ch3:
        if st.button("🔍 Practical example", use_container_width=True, key="chip3"):
            chip = "Give me a real-world practical example of the main concept."
    with ch4:
        if st.button("🎯 Exam tips", use_container_width=True, key="chip4"):
            chip = "What are the most important points I should memorize for an exam?"

    st.divider()

    # Chat history display
    if not st.session_state.tutor_history:
        ui.empty_state(
            "🤖", "Start a conversation",
            "Type a question below or click a quick prompt above."
        )

    for msg in st.session_state.tutor_history:
        if msg["role"] == "user":
            ui.chat_user(msg["content"])
        else:
            ui.chat_ai(msg["content"], msg.get("sources"))
            if msg.get("sources"):
                with st.expander("📎 Source chunks", expanded=False):
                    for s in msg["sources"]:
                        st.caption(
                            f"**{s.get('file_name','Doc')}** · "
                            f"Page {s.get('page',1)} · Score {s.get('score',0):.3f}"
                        )
                        st.markdown(f"> {s.get('snippet','')[:250]}…")

    # Input
    user_input = st.chat_input("Ask your AI Tutor…")
    prompt = chip or user_input or st.session_state.prefill

    if prompt and st.session_state.prefill:
        st.session_state.prefill = ""

    if prompt:
        if not config.is_gemini_configured():
            st.error("❌ Gemini API key not configured. Add it to `.env`.")
            st.stop()

        st.session_state.tutor_history.append({"role": "user", "content": prompt})

        with st.spinner("AI Tutor thinking…"):
            try:
                res = rag.answer_question(prompt)
                st.session_state.tutor_history.append({
                    "role":    "assistant",
                    "content": res.get("answer", ""),
                    "sources": res.get("sources", []),
                })
            except Exception as e:
                st.error(f"AI error: {e}")

        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 📝  QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📝 Quiz":
    ui.page_banner(
        "📝 AI Quiz",
        "Test your knowledge with AI-generated multiple choice questions.",
    )

    mem_data     = memory.load_memory()
    indexed_names = rag.get_indexed_file_names()
    available    = list(set(mem_data.get("topics_studied", []) + indexed_names))
    if not available:
        available = ["Cloud Computing", "Computer Networks", "Database Systems", "Python Programming"]

    # Quiz settings
    with st.expander(
        "⚙️ Quiz Settings",
        expanded=(st.session_state.current_quiz is None and st.session_state.quiz_results is None),
    ):
        # ── Quiz source mode ──────────────────────────────────────────────────
        quiz_mode = st.radio(
            "Generate quiz from:",
            ["📚 My indexed PDFs", "✏️ Topic name", "📝 Paste my own notes/text"],
            horizontal=True,
        )

        s1, s2 = st.columns([3, 1])
        with s2:
            num_q = st.selectbox("Questions", [5, 10])
            diff  = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)

        with s1:
            if quiz_mode == "📚 My indexed PDFs":
                # pull topic from indexed files
                if available:
                    sel_topic = st.selectbox("Select document / topic", available)
                    active_topic = sel_topic
                    ctx_str_override = None   # will search RAG normally
                else:
                    st.warning("No documents indexed yet. Upload a PDF in Study Materials first.")
                    active_topic     = ""
                    ctx_str_override = None

            elif quiz_mode == "✏️ Topic name":
                active_topic = st.text_input(
                    "Topic name",
                    placeholder="e.g. Python OOP, TCP/IP, Normalization, Photosynthesis",
                )
                ctx_str_override = None   # will search RAG for context if available

            else:  # Paste notes
                active_topic = st.text_input(
                    "Topic label (used as quiz title)",
                    placeholder="e.g. Chapter 3 – Networking",
                )
                pasted_text = st.text_area(
                    "Paste your notes or any text here:",
                    height=180,
                    placeholder="Paste lecture notes, paragraphs, a Wikipedia excerpt… "
                                "The AI will generate questions directly from this text.",
                )
                # store pasted text so gen block can use it
                ctx_str_override = pasted_text.strip() if pasted_text.strip() else None

        gen_btn = st.button("⚡ Generate Quiz", type="primary", use_container_width=True)

    if gen_btn:
        if not active_topic.strip():
            st.warning("Please enter a topic name or select a document.")
        elif not config.is_gemini_configured():
            st.error("Gemini API key not configured.")
        else:
            with st.spinner(f"Generating {num_q} questions on **{active_topic}**…"):
                try:
                    # Determine context string
                    if quiz_mode == "📝 Paste my own notes/text":
                        ctx_str = ctx_str_override or ""
                    else:
                        ctx_chunks = rag.search_study_material(active_topic, top_k=4)
                        ctx_str = "\n\n".join(c["text"] for c in ctx_chunks) if ctx_chunks else ""

                    questions = quiz.generate_quiz_questions(
                        topic=active_topic,
                        num_questions=num_q,
                        difficulty=diff,
                        context=ctx_str,
                    )
                    st.session_state.current_quiz  = questions
                    st.session_state.quiz_answers  = {}
                    st.session_state.quiz_results  = None
                    st.session_state.quiz_topic    = active_topic
                    st.session_state.quiz_idx      = 0
                    st.session_state.quiz_run     += 1
                    st.rerun()
                except Exception as ex:
                    st.error(f"Quiz generation error: {ex}")

    # Results
    if st.session_state.quiz_results:
        res = st.session_state.quiz_results
        ui.performance_banner(res["score"], res["total"], res["percentage"])

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔄 Retry", use_container_width=True):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_results = None
                st.session_state.quiz_idx     = 0
                st.rerun()
        with b2:
            if res.get("weak_areas"):
                if st.button(
                    f"🤖 Tutor: explain '{res['weak_areas'][0][:22]}…'",
                    type="primary", use_container_width=True,
                ):
                    st.session_state.prefill = (
                        f"I struggled with this topic in a quiz: {res['weak_areas'][0]}. "
                        "Please explain it clearly with examples."
                    )
                    go("🤖 AI Tutor")
            else:
                if st.button("📅 Create Study Plan", type="primary", use_container_width=True):
                    go("📅 Study Plan")

        st.subheader("📋 Question Review")
        for item in res["details"]:
            ui.question_review_card(item)

    # Active quiz
    elif st.session_state.current_quiz:
        qs    = st.session_state.current_quiz
        total = len(qs)
        idx   = st.session_state.quiz_idx
        q     = qs[idx]

        st.caption(f"Question {idx + 1} of {total}  ·  {q.get('subtopic', st.session_state.quiz_topic)}")
        st.progress((idx + 1) / total)
        st.markdown(f"**{q['id']}. {q['question']}**")

        opts    = [f"{k}. {v}" for k, v in q["options"].items()]
        prev    = st.session_state.quiz_answers.get(q["id"])
        sel_idx = None
        if prev:
            for i, o in enumerate(opts):
                if o.startswith(prev):
                    sel_idx = i
                    break

        choice = st.radio(
            "Choose an answer:",
            opts,
            index=sel_idx,
            key=f"q_{st.session_state.quiz_run}_{q['id']}",
            label_visibility="collapsed",
        )
        if choice:
            st.session_state.quiz_answers[q["id"]] = choice[0]

        st.divider()
        nav1, nav_mid, nav2 = st.columns([1, 2, 1])

        with nav1:
            if idx > 0:
                if st.button("⬅ Prev", use_container_width=True):
                    st.session_state.quiz_idx -= 1
                    st.rerun()

        with nav_mid:
            pcols = st.columns(total)
            for pi in range(total):
                ans_flag = qs[pi]["id"] in st.session_state.quiz_answers
                lbl = f"{pi+1}{'✓' if ans_flag else ''}"
                with pcols[pi]:
                    if st.button(
                        lbl,
                        key=f"pill_{pi}",
                        type="primary" if pi == idx else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state.quiz_idx = pi
                        st.rerun()

        with nav2:
            if idx < total - 1:
                if st.button("Next ➡", type="primary", use_container_width=True):
                    st.session_state.quiz_idx += 1
                    st.rerun()
            else:
                if st.button("📊 Submit Quiz", type="primary", use_container_width=True):
                    with st.spinner("Grading…"):
                        results = quiz.calculate_quiz_score(
                            questions=st.session_state.current_quiz,
                            user_answers=st.session_state.quiz_answers,
                            topic=st.session_state.quiz_topic,
                        )
                        st.session_state.quiz_results = results
                    st.rerun()

    else:
        ui.empty_state("📝", "No quiz yet", "Configure settings above and click Generate Quiz.")


# ══════════════════════════════════════════════════════════════════════════════
# 📅  STUDY PLAN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📅 Study Plan":
    ui.page_banner(
        "📅 Study Plan",
        "Generate a personalized day-by-day exam preparation schedule.",
    )

    mem_data    = memory.load_memory()
    default_sub = mem_data["topics_studied"][-1] if mem_data["topics_studied"] else "Cloud Computing"

    f1, f2 = st.columns(2)
    with f1:
        subject  = st.text_input("Subject / Topic", value=default_sub)
        exam_dt  = st.date_input(
            "Exam Date",
            value=date.today() + timedelta(days=14),
            min_value=date.today(),
        )
        daily_h  = st.slider("Daily study hours", 1.0, 8.0, 2.0, 0.5)
    with f2:
        level    = st.selectbox("Your level", ["Beginner", "Intermediate", "Advanced"], index=1)
        weak_opt = list(set(mem_data.get("weak_topics", []) + ["Core Theory", "Exam Review"]))
        sel_weak = st.multiselect(
            "Priority / weak topics",
            weak_opt,
            default=mem_data.get("weak_topics", []),
        )

    if st.button("📅 Generate Plan", type="primary", use_container_width=True):
        if not config.is_gemini_configured():
            st.error("Gemini API key not configured.")
        else:
            with st.spinner(f"Building study plan for **{subject}**…"):
                try:
                    plan = study_plan.generate_study_plan(
                        subject=subject,
                        exam_date=str(exam_dt),
                        daily_hours=daily_h,
                        knowledge_level=level,
                        weak_topics=sel_weak,
                    )
                    st.session_state.study_plan = plan
                    st.session_state.done_days  = set()
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")

    if st.session_state.study_plan:
        plan    = st.session_state.study_plan
        days    = study_plan.parse_study_plan_to_days(
            plan["plan_markdown"], plan.get("weak_topics", [])
        )
        total_d = len(days)
        done_d  = len(st.session_state.done_days)
        pct     = int(done_d / total_d * 100) if total_d else 0

        st.divider()
        st.markdown(f"### 📋 {plan['subject']} — {total_d}-Day Roadmap")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Days to Exam",    plan["days_remaining"])
        with m2:
            st.metric("Daily Target",    f"{plan['daily_hours']} hrs")
        with m3:
            st.metric("Plan Completed",  f"{done_d}/{total_d} ({pct}%)")

        if total_d:
            st.progress(done_d / total_d)

        st.divider()

        for day in days:
            dn     = day["day_number"]
            is_done = dn in st.session_state.done_days
            ui.day_card_header(dn, day["title"], is_done, day.get("is_weak_topic", False))

            if day.get("bullets"):
                for b in day["bullets"]:
                    st.markdown(f"  - {b}")
            elif day.get("content"):
                st.caption(day["content"][:300])

            chk = st.checkbox(f"Mark Day {dn} complete", value=is_done, key=f"day_{dn}")
            if chk and dn not in st.session_state.done_days:
                st.session_state.done_days.add(dn)
                st.rerun()
            elif not chk and dn in st.session_state.done_days:
                st.session_state.done_days.remove(dn)
                st.rerun()

        st.divider()
        st.download_button(
            "📥 Download Plan (.md)",
            data=plan["plan_markdown"],
            file_name=f"StudyPlan_{plan['subject'].replace(' ','_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    else:
        ui.empty_state("📅", "No plan yet", "Fill in the form above and click Generate Plan.")


# ══════════════════════════════════════════════════════════════════════════════
# 🗺️  LEARNING PATHWAYS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "🗺️ Learning Pathways":
    ui.page_banner(
        "🗺️ Learning Pathways",
        "Learn step by step — pick a topic, click any concept, get a full detailed lesson.",
    )

    # ── 4 feature tabs ────────────────────────────────────────────────────────
    tab_lessons, tab_road, tab_yt, tab_web = st.tabs([
        "📖 Interactive Lessons",
        "🗓️ Weekly Roadmap",
        "▶️ YouTube Channels",
        "🌐 Best Websites",
    ])

    # ════════════════════════════════════════════════════════════
    # TAB 0 — Interactive Lessons (DETAILED LEARNING)
    # ════════════════════════════════════════════════════════════
    with tab_lessons:
        st.subheader("📖 Learn Any Topic — Step by Step")
        st.caption("Pick a subject → see all stages → click any concept → get a full lesson with examples & practice.")

        # Topic input
        lesson_topic = st.text_input(
            "What do you want to learn?",
            placeholder="e.g. Python Programming, Machine Learning, Web Development…",
            key="lesson_topic",
        )

        if st.button("📚 Load Learning Path", type="primary", use_container_width=True, key="load_lessons"):
            if not lesson_topic.strip():
                st.warning("Enter a topic first.")
            else:
                topic_clean = lesson_topic.strip()
                st.session_state["lesson_topic_active"] = topic_clean
                # Load predefined stages or generate via Gemini
                pathway = lp.get_pathway(topic_clean)
                st.session_state["lesson_stages"] = pathway.get("stages") or []
                st.session_state["lesson_pathway_text"] = pathway.get("pathway_text", "")
                st.session_state["lesson_current_subtopic"] = None
                st.session_state["lesson_content"] = ""
                st.rerun()

        active_topic = st.session_state.get("lesson_topic_active", "")
        stages       = st.session_state.get("lesson_stages", [])

        if active_topic and stages:
            st.divider()
            st.markdown(f"## 📖 {active_topic} — Learning Path")
            st.caption(f"You are now learning **{active_topic}**. Click any topic below to get a full detailed lesson.")

            # Show each stage with clickable topics
            for stage in stages:
                stage_name = stage.get("stage", "Stage")
                topics     = stage.get("topics", [])
                hours      = stage.get("hours", "")

                # Stage header
                color_map = {"Beginner": "🟢", "Intermediate": "🟡", "Advanced": "🔴"}
                emoji = color_map.get(stage_name, "🔵")
                st.markdown(f"### {emoji} {stage_name}" + (f"  ·  ~{hours} hours" if hours else ""))

                # Topic buttons in a grid
                if topics:
                    btn_cols = st.columns(min(len(topics), 4))
                    for i, t in enumerate(topics):
                        with btn_cols[i % len(btn_cols)]:
                            is_current = st.session_state.get("lesson_current_subtopic") == t
                            if st.button(
                                f"{'➡️ ' if is_current else '▫️ '}{t}",
                                key=f"topic_btn_{i}_{t}",
                                use_container_width=True,
                                type="primary" if is_current else "secondary",
                            ):
                                st.session_state["lesson_current_subtopic"] = t
                                with st.spinner(f"Generating lesson: {t}…"):
                                    st.session_state["lesson_content"] = lp.get_detailed_lesson(
                                        active_topic, t
                                    )
                                st.rerun()

                st.markdown("---")

            # Show the selected lesson
            current_sub = st.session_state.get("lesson_current_subtopic")
            lesson_text = st.session_state.get("lesson_content", "")

            if current_sub and lesson_text:
                st.markdown(f"## 📚 Now Learning: {current_sub}")
                st.markdown(lesson_text)

                # Download + actions
                st.divider()
                dl1, dl2, dl3 = st.columns(3)
                with dl1:
                    st.download_button(
                        "📥 Download Lesson (.md)",
                        data=lesson_text,
                        file_name=f"Lesson_{active_topic.replace(' ','_')}_{current_sub.replace(' ','_')}.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                with dl2:
                    if st.button("🤖 Ask AI Tutor about this", use_container_width=True, key="lesson_tutor"):
                        st.session_state.prefill = f"Explain {current_sub} in {active_topic} with examples."
                        go("🤖 AI Tutor")
                with dl3:
                    if st.button("📝 Quiz me on this", use_container_width=True, key="lesson_quiz"):
                        memory.add_topic_studied(current_sub)
                        go("📝 Quiz")

        elif active_topic and st.session_state.get("lesson_pathway_text"):
            # AI-generated free-text pathway (no structured stages)
            st.divider()
            st.markdown(f"## 📖 {active_topic} — Learning Path")
            st.markdown(st.session_state["lesson_pathway_text"])

            st.info("💡 For detailed step-by-step lessons, try a common topic like 'Python Programming' which has predefined interactive stages.")

        else:
            ui.empty_state("📖", "No topic loaded yet", "Type a topic above and click 'Load Learning Path'. Try 'Python Programming' for the best experience.")

    # ════════════════════════════════════════════════════════════
    # TAB 1 — Weekly Roadmap
    # ════════════════════════════════════════════════════════════
    with tab_road:
        st.subheader("🗓️ Generate a Week-by-Week Learning Roadmap")
        st.caption("Enter any topic and get a full detailed plan with daily tasks, milestones, and a capstone project.")

        r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
        with r1:
            road_topic = st.text_input(
                "Topic", placeholder="e.g. Python, Machine Learning, React, SQL…",
                key="road_topic",
            )
        with r2:
            road_level = st.selectbox("Your level", ["Beginner", "Intermediate", "Advanced"], key="road_level")
        with r3:
            road_weeks = st.selectbox("Duration (weeks)", [4, 6, 8, 12], key="road_weeks")
        with r4:
            road_hrs   = st.selectbox("Hours/week", [5, 10, 15, 20], key="road_hrs")

        if st.button("🚀 Generate Roadmap", type="primary", use_container_width=True, key="gen_road"):
            if not road_topic.strip():
                st.warning("Enter a topic first.")
            elif not config.is_gemini_configured():
                st.error("Gemini API key not configured.")
            else:
                with st.spinner(f"Building your {road_weeks}-week roadmap for **{road_topic}**…"):
                    st.session_state["roadmap_text"]  = lp.generate_weekly_roadmap(
                        road_topic.strip(), road_level, road_weeks, road_hrs
                    )
                    st.session_state["roadmap_topic"] = road_topic.strip()

        if st.session_state.get("roadmap_text"):
            st.divider()
            st.markdown(st.session_state["roadmap_text"])
            st.divider()
            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                st.download_button(
                    "📥 Download Roadmap (.md)",
                    data=st.session_state["roadmap_text"],
                    file_name=f"Roadmap_{st.session_state.get('roadmap_topic','topic').replace(' ','_')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with dl2:
                if st.button("📝 Quiz on this topic", use_container_width=True, key="road_quiz"):
                    memory.add_topic_studied(st.session_state.get("roadmap_topic", ""))
                    go("📝 Quiz")
            with dl3:
                if st.button("📅 Build Study Plan", use_container_width=True, key="road_plan"):
                    go("📅 Study Plan")
        else:
            ui.empty_state("🗓️", "No roadmap yet", "Fill in the form above and click Generate Roadmap.")

    # ════════════════════════════════════════════════════════════
    # TAB 2 — YouTube Channels
    # ════════════════════════════════════════════════════════════
    with tab_yt:
        st.subheader("▶️ Best YouTube Channels for Any Topic")
        st.caption("Get a curated list of the best YouTube channels to learn from.")

        yt_topic = st.text_input(
            "Topic", placeholder="e.g. Python, Machine Learning, Web Development…",
            key="yt_ch_topic",
        )
        if st.button("🔍 Find Channels", type="primary", use_container_width=True, key="find_yt"):
            if not yt_topic.strip():
                st.warning("Enter a topic.")
            else:
                with st.spinner(f"Finding best YouTube channels for **{yt_topic}**…"):
                    st.session_state["yt_channels"] = lp.get_yt_channels(yt_topic.strip())
                    st.session_state["yt_ch_searched"] = yt_topic.strip()

        if st.session_state.get("yt_channels"):
            st.divider()
            st.markdown(f"### 📺 Top YouTube Channels — {st.session_state.get('yt_ch_searched','')}")
            for ch in st.session_state["yt_channels"]:
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**[{ch['name']}]({ch['url']})**")
                    st.caption(ch.get("why", ""))
                with col_btn:
                    st.link_button("▶️ Open", ch["url"], use_container_width=True)
                st.divider()

    # ════════════════════════════════════════════════════════════
    # TAB 3 — Best Websites
    # ════════════════════════════════════════════════════════════
    with tab_web:
        st.subheader("🌐 Best Websites & Free Resources")
        st.caption("Handpicked free learning sites, docs, and practice platforms.")

        web_topic = st.text_input(
            "Topic", placeholder="e.g. Cloud Computing, Database Systems…",
            key="web_topic",
        )
        if st.button("🔍 Find Resources", type="primary", use_container_width=True, key="find_web"):
            if not web_topic.strip():
                st.warning("Enter a topic.")
            else:
                with st.spinner(f"Finding best resources for **{web_topic}**…"):
                    st.session_state["websites"]       = lp.get_websites(web_topic.strip())
                    st.session_state["web_searched"]   = web_topic.strip()

        if st.session_state.get("websites"):
            st.divider()
            st.markdown(f"### 🌐 Top Resources — {st.session_state.get('web_searched','')}")
            for site in st.session_state["websites"]:
                sc1, sc2 = st.columns([4, 1])
                with sc1:
                    st.markdown(f"**[{site['name']}]({site['url']})**")
                    st.caption(site.get("what", ""))
                with sc2:
                    st.link_button("🌐 Open", site["url"], use_container_width=True)
                st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# ▶️  YOUTUBE NOTES  (top-level page)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "▶️ YouTube Notes":
    ui.page_banner(
        "▶️ YouTube Video Notes",
        "Paste a YouTube link and get downloadable AI study notes.",
    )

    if not config.is_gemini_configured():
        st.warning("⚠️ This feature needs a Gemini API key. Add it to `.env`.")

    yt_url = st.text_input(
        "YouTube video URL",
        placeholder="https://www.youtube.com/watch?v=…",
        key="yt_url",
    )
    yt_desc = st.text_area(
        "Optional: paste the video description, chapter titles, or your own notes "
        "to make the AI notes more accurate.",
        height=110,
        placeholder="Paste the video description from YouTube or any notes about the video…",
        key="yt_desc",
    )

    if st.button("📝 Generate Notes", type="primary", use_container_width=True, key="gen_notes"):
        if not yt_url.strip():
            st.warning("Paste a YouTube URL first.")
        elif not config.is_gemini_configured():
            st.error("Gemini API key not configured.")
        else:
            with st.spinner("Generating study notes for the video…"):
                st.session_state["yt_notes_result"] = lp.generate_yt_notes(
                    yt_url.strip(), yt_desc.strip()
                )

    if st.session_state.get("yt_notes_result"):
        nr = st.session_state["yt_notes_result"]
        if nr.get("success"):
            st.success(f"✅ Notes ready for: **{nr['title']}**")
            st.divider()
            st.markdown(nr["notes"])
            st.divider()

            n1, n2 = st.columns(2)
            with n1:
                st.download_button(
                    "📥 Download Notes (.md)",
                    data=nr["notes"],
                    file_name=f"Notes_{nr['title'][:40].replace(' ','_')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with n2:
                st.download_button(
                    "📥 Download Notes (.txt)",
                    data=nr["notes"],
                    file_name=f"Notes_{nr['title'][:40].replace(' ','_')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            st.link_button("▶️ Watch Video", nr["url"], use_container_width=True)

            if st.button("🗑️ Clear", use_container_width=True, key="clr_yt"):
                st.session_state["yt_notes_result"] = None
                st.rerun()
        else:
            st.error(f"❌ {nr.get('error', 'Failed to generate notes.')}")
    else:
        ui.empty_state(
            "▶️", "No notes yet",
            "Paste a YouTube URL above and click Generate Notes.",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 📖  WIKIPEDIA Q&A  (top-level page)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "📖 Wikipedia Q&A":
    ui.page_banner(
        "📖 Wikipedia Q&A",
        "Look up any topic on Wikipedia, then ask questions answered from the article.",
    )

    wk1, wk2 = st.columns([1, 2])

    # ── Load Wikipedia summary ────────────────────────────────────────────────
    with wk1:
        wiki_topic = st.text_input(
            "Wikipedia topic",
            placeholder="e.g. Neural network, TCP/IP, Photosynthesis",
            key="wiki_topic",
        )
        if st.button("📖 Load Article", type="primary", use_container_width=True, key="load_wiki"):
            if not wiki_topic.strip():
                st.warning("Enter a topic.")
            else:
                with st.spinner(f"Fetching Wikipedia: {wiki_topic}…"):
                    st.session_state["wiki_data"] = lp.get_wikipedia_summary(wiki_topic.strip())
                    st.session_state["wiki_answer"] = ""

    # ── Show summary ──────────────────────────────────────────────────────────
    with wk2:
        wd = st.session_state.get("wiki_data", {})
        if wd.get("found"):
            st.markdown(f"### 📖 [{wd['title']}]({wd['url']})")
            if wd.get("image"):
                st.image(wd["image"], width=200)
            st.info(wd["summary"][:700] + ("…" if len(wd["summary"]) > 700 else ""))
            if wd.get("url"):
                st.caption(f"Source: {wd['url']}")
        elif wd:
            st.error(f"Article not found for '{wiki_topic}'. Try a different term.")

    st.divider()

    # ── Ask question ──────────────────────────────────────────────────────────
    st.subheader("Ask a question about this topic")
    wiki_q = st.text_input(
        "Your question",
        placeholder="e.g. How does it work?  What are the main types?  Give an example.",
        key="wiki_question",
    )

    if st.button("🔎 Answer from Wikipedia", type="primary", use_container_width=True, key="ask_wiki"):
        if not st.session_state.get("wiki_data", {}).get("found"):
            st.warning("Load a Wikipedia topic first (above).")
        elif not wiki_q.strip():
            st.warning("Type a question.")
        elif not config.is_gemini_configured():
            # Fallback — show raw Wikipedia summary
            st.markdown("**Wikipedia summary (no Gemini key — raw article):**")
            st.markdown(st.session_state["wiki_data"]["summary"])
        else:
            with st.spinner("Reading Wikipedia & generating answer…"):
                ans = lp.answer_from_wikipedia(wiki_topic.strip(), wiki_q.strip())
                st.session_state["wiki_answer"]    = ans
                st.session_state["wiki_q_asked"]   = wiki_q.strip()

    if st.session_state.get("wiki_answer"):
        st.markdown(f"**Q: {st.session_state.get('wiki_q_asked','')}**")
        st.markdown(st.session_state["wiki_answer"])
        wd = st.session_state.get("wiki_data", {})
        if wd.get("url"):
            st.caption(f"📖 Answered from: [{wd.get('title','')}]({wd.get('url','')})")

        if st.button("🗑️ Clear answer", use_container_width=True, key="clr_wiki"):
            st.session_state["wiki_answer"] = ""
            st.rerun()
