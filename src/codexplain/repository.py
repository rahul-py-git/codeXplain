"""Bounded source discovery and line-aware code chunking."""
import os
from dataclasses import dataclass
from pathlib import Path
from .config import chunk_lines, max_file_bytes, max_files, overlap_lines

IGNORED_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "dist", "build", "target", "vendor", ".idea", ".vscode"}
SECRET_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519", "credentials", "secrets.json", "secrets.yaml", "secrets.yml"}
ALLOWED_SUFFIXES = {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".go", ".rs", ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".rb", ".swift", ".scala", ".sql", ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".yaml", ".yml", ".toml", ".json", ".xml", ".html", ".css", ".scss", ".md", ".rst", ".txt", ".properties", ".conf", ".ini", ".gradle", ".tf"}

@dataclass(frozen=True)
class CodeChunk:
    path: str
    start_line: int
    end_line: int
    text: str
    @property
    def label(self) -> str:
        return f"{self.path}:{self.start_line}-{self.end_line}"

def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False

def resolve_repository(repo_path: str, root: Path | None = None) -> Path:
    boundary = (root or Path.cwd()).resolve()
    candidate = Path(repo_path).expanduser()
    if not candidate.is_absolute():
        candidate = boundary / candidate
    candidate = candidate.resolve(strict=True)
    if not is_within(candidate, boundary):
        raise PermissionError(f"Selected path must be inside the allowed root: {boundary}")
    if not candidate.is_dir():
        raise NotADirectoryError(f"Not a directory: {candidate}")
    return candidate

def _is_secret(path: Path) -> bool:
    name = path.name.lower()
    return name in SECRET_NAMES or name.startswith(".env.") or "secret" in name or name.endswith((".pem", ".key", ".p12", ".pfx"))

def discover_files(repo: Path) -> list[Path]:
    root = repo.resolve(strict=True)
    found: list[Path] = []
    for current, dirs, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not (current_path / d).is_symlink()]
        for filename in filenames:
            path = current_path / filename
            if path.is_symlink() or _is_secret(path):
                continue
            if path.suffix.lower() not in ALLOWED_SUFFIXES and filename.lower() != "dockerfile":
                continue
            try:
                resolved = path.resolve(strict=True)
                if not is_within(resolved, root) or not resolved.is_file() or resolved.stat().st_size > max_file_bytes():
                    continue
            except (OSError, RuntimeError):
                continue
            found.append(resolved)
            if len(found) >= max_files():
                return sorted(found)
    return sorted(found)

def read_source_file(path: Path, repo: Path) -> str:
    root = repo.resolve(strict=True)
    if path.is_symlink():
        raise PermissionError("Symbolic links are not read")
    resolved = path.resolve(strict=True)
    if not is_within(resolved, root) or not resolved.is_file():
        raise PermissionError("File is outside the repository or is not a regular file")
    if _is_secret(resolved) or resolved.stat().st_size > max_file_bytes():
        raise PermissionError("File is excluded by CodeXplain safety limits")
    return resolved.read_text(encoding="utf-8", errors="replace")

def chunk_text(path_label: str, text: str) -> list[CodeChunk]:
    lines = text.splitlines()
    if not lines:
        return []
    size, overlap = chunk_lines(), overlap_lines()
    step = max(1, size - overlap)
    chunks: list[CodeChunk] = []
    for start in range(0, len(lines), step):
        end = min(start + size, len(lines))
        chunks.append(CodeChunk(path_label, start + 1, end, "\n".join(lines[start:end])))
        if end == len(lines):
            break
    return chunks

def index_repository(repo: Path) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []
    for path in discover_files(repo):
        try:
            content = read_source_file(path, repo)
            chunks.extend(chunk_text(path.relative_to(repo.resolve()).as_posix(), content))
        except (OSError, UnicodeError, PermissionError):
            continue
    return chunks
