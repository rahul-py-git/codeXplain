"""Streamlit user interface for CodeXplain V1."""
import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")
from codexplain.config import allowed_root
from codexplain.llm import answer_question
from codexplain.repository import chunk_text, index_repository, resolve_repository
from codexplain.retrieval import retrieve

st.set_page_config(page_title="CodeXplain", page_icon="🔎", layout="wide")
st.title("🔎 CodeXplain")
st.caption("Ask questions about source code and get explanations grounded in file paths and line ranges.")
with st.sidebar:
    st.header("Workspace access")
    boundary = allowed_root()
    st.code(str(boundary), language="text")
    st.caption("Only folders inside this configured root are eligible. OS account permissions still apply.")
    st.header("Model")
    st.write("Provider: Google Gemini")
    st.write(f"Model: {os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')}")
    st.warning("Selected source snippets are sent to the configured model API.")

mode = st.radio("Choose input", ["Local repository", "Single file / snippet"], horizontal=True)
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "workspace_label" not in st.session_state:
    st.session_state.workspace_label = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

if mode == "Local repository":
    repo_input = st.text_input("Repository folder path", value=".", help="Absolute path or path relative to the configured allowed root.")
    if st.button("Scan repository", type="primary"):
        try:
            repo = resolve_repository(repo_input, boundary)
            with st.spinner("Scanning eligible source files..."):
                chunks = index_repository(repo)
            if not chunks:
                st.warning("No supported source files found. Check the path, file types and scan limits.")
            else:
                st.session_state.chunks = chunks
                st.session_state.workspace_label = str(repo)
                st.session_state.messages = []
                st.success(f"Indexed {len(chunks)} chunks from {len(set(c.path for c in chunks))} files.")
        except Exception as exc:
            st.error(f"Could not scan repository: {exc}")
else:
    uploaded = st.file_uploader("Upload a text source file", type=["py", "js", "jsx", "ts", "tsx", "java", "go", "rs", "c", "cpp", "cs", "sql", "sh", "yaml", "yml", "json", "xml", "html", "css", "md", "txt", "properties", "gradle", "tf"])
    pasted = st.text_area("Or paste a code snippet", height=220, placeholder="Paste source code here...")
    if st.button("Load file / snippet", type="primary"):
        try:
            if uploaded is not None:
                if uploaded.size > int(os.getenv("CODEXPLAIN_MAX_FILE_BYTES", "300000")):
                    raise ValueError("Uploaded file exceeds the configured file-size limit.")
                source, label = uploaded.getvalue().decode("utf-8", errors="replace"), uploaded.name
            elif pasted.strip():
                source, label = pasted, "pasted-snippet"
            else:
                raise ValueError("Upload a file or paste a snippet first.")
            st.session_state.chunks = chunk_text(label, source)
            st.session_state.workspace_label = label
            st.session_state.messages = []
            st.success(f"Loaded {len(st.session_state.chunks)} chunks from {label}.")
        except Exception as exc:
            st.error(str(exc))

if st.session_state.chunks:
    st.subheader(f"Current context: {st.session_state.workspace_label}")
    with st.expander("Show indexed source files"):
        for path in sorted(set(chunk.path for chunk in st.session_state.chunks)):
            st.write(path)
    action = st.selectbox("Quick action", ["Ask a question", "Explain the selected context", "Summarize the project / file", "Explain code step by step"])
    question = st.text_area("Your question", placeholder="e.g. Where is input validated, and what happens if it fails?", height=90)
    effective_question = question.strip()
    if action != "Ask a question" and not effective_question:
        effective_question = {"Explain the selected context": "Explain the purpose and logic of the provided source context.", "Summarize the project / file": "Summarize the responsibilities and structure of this source context.", "Explain code step by step": "Explain the execution flow step by step, distinguishing facts from assumptions."}[action]
    if st.button("Ask CodeXplain", type="primary", disabled=not effective_question):
        selected = retrieve(effective_question, st.session_state.chunks, limit=8)
        if not selected:
            st.warning("No relevant chunks found. Try exact function, class, variable or error names.")
        else:
            context = "\n\n".join(f"--- {chunk.label} ---\n{chunk.text}" for chunk in selected)
            try:
                with st.spinner("Reading relevant code and generating an answer..."):
                    answer = answer_question(effective_question, context)
                st.session_state.messages.append({"question": effective_question, "answer": answer, "sources": [chunk.label for chunk in selected]})
            except Exception as exc:
                st.error(f"Could not generate an answer: {exc}")
    for item in reversed(st.session_state.messages):
        with st.chat_message("assistant"):
            st.markdown(item["answer"])
            with st.expander("Source context supplied to the model"):
                for source in item["sources"]:
                    st.code(source, language="text")
        with st.chat_message("user"):
            st.write(item["question"])
else:
    st.info("Choose a repository folder or load a single file/snippet to get started.")
st.divider()
st.caption("V1 uses lexical retrieval and may miss indirect cross-file relationships. It never executes repository code.")
