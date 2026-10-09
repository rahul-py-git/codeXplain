# CodeXplain

CodeXplain is an LLM-powered assistant for explaining source code and answering questions about a repository or a single file. V1 uses a Streamlit UI, a permission-aware local repository scanner, lexical code retrieval, and Google's Gemini API.

## V1 features

- Explain a single source file or pasted snippet.
- Scan a local repository within a configured allowed root.
- Ask questions about a repository and retrieve relevant source chunks.
- Display source paths and line ranges used as context.
- Exclude common dependency/build directories, secret-like files, and oversized files.
- Never execute source code while indexing or explaining it.
- Keep API credentials in environment variables.

> **Privacy note:** With Gemini configured, retrieved source snippets are sent to Google's API. Do not use this with confidential or workplace code unless your organization's policies and the provider's terms permit it. For private code, review data handling before use.

## Requirements

- Python 3.11+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- Internet access for API requests

## Setup

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY`.

Set the directory CodeXplain is allowed to read. By default it is the current working directory; set it explicitly to the folder containing the repositories you want to inspect:

```powershell
$env:CODEXPLAIN_ALLOWED_ROOT = "C:\Users\YourUser\source"
```

Run:

```powershell
streamlit run app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export CODEXPLAIN_ALLOWED_ROOT="$HOME/projects"
streamlit run app.py
```

## How it works

1. The scanner resolves the selected repository path and verifies that it is inside `CODEXPLAIN_ALLOWED_ROOT`.
2. It skips configured directories, secret-like filenames, symlinks, binary files, and files over the size limit.
3. Source files are split into overlapping line-based chunks.
4. A lightweight lexical ranker selects relevant chunks for each question.
5. The selected snippets and line references are sent to Gemini to generate an answer.
6. The UI shows the answer and the exact source ranges supplied as context.

V1 uses lexical retrieval, not embeddings. This keeps the first version simple and avoids a separate vector database. Semantic retrieval, symbol-aware parsing, persistent indexing, and GitHub OAuth can be added later.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | unset | API key; required for model answers |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Model identifier; change to a model available to your API key |
| `CODEXPLAIN_ALLOWED_ROOT` | current working directory | Maximum local directory boundary |
| `CODEXPLAIN_MAX_FILE_BYTES` | `300000` | Maximum file size to read |
| `CODEXPLAIN_MAX_FILES` | `500` | Maximum files per scan |
| `CODEXPLAIN_CHUNK_LINES` | `100` | Lines per code chunk |
| `CODEXPLAIN_OVERLAP_LINES` | `15` | Overlap between adjacent chunks |

## Safety and limitations

- This is a local development tool, not a multi-user security boundary. Run it only in a trusted environment.
- The configured root is a filesystem boundary, not a replacement for OS permissions. The process can read only what its OS account can read, but you should run it with least privilege.
- Do not commit `.env` or API keys.
- Repository text is untrusted input. The model is instructed to treat source comments and files as data, not instructions.
- Answers may be wrong. Verify important conclusions against the cited code.
- The current retriever is lexical and can miss indirect relationships or relevant code in large projects.
- GitHub URL ingestion and GitHub account authorization are not implemented in V1; local checkout only.

## Tests

```bash
pytest -q
```

## Roadmap

- [ ] V1: local file/repository explanations and lexical Q&A
- [ ] Syntax-aware chunking with Tree-sitter
- [ ] Embedding-based semantic retrieval and persistent index
- [ ] Import/caller/callee relationship search
- [ ] GitHub repository access with explicit authorization
- [ ] Retrieval and answer-quality evaluation suite
