from pathlib import Path
import pytest
from codexplain.repository import chunk_text, discover_files, resolve_repository

def test_resolve_repository_allows_child_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert resolve_repository("repo", tmp_path) == repo.resolve()

def test_resolve_repository_rejects_outside_path(tmp_path: Path) -> None:
    allowed, outside = tmp_path / "allowed", tmp_path / "outside"
    allowed.mkdir(); outside.mkdir()
    with pytest.raises(PermissionError):
        resolve_repository(str(outside), allowed)

def test_discover_files_skips_secrets_and_dependencies(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True); (repo / "node_modules").mkdir()
    (repo / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
    (repo / ".env").write_text("TOKEN=do-not-read", encoding="utf-8")
    (repo / "node_modules" / "dependency.js").write_text("ignored", encoding="utf-8")
    assert [p.name for p in discover_files(repo)] == ["main.py"]

def test_chunk_text_preserves_line_ranges(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEXPLAIN_CHUNK_LINES", "10")
    text = "\n".join(f"line-{i}" for i in range(1, 24))
    chunks = chunk_text("example.py", text)
    assert chunks[0].start_line == 1
    assert chunks[0].end_line <= 10
    assert chunks[0].text.splitlines()[0] == "line-1"
