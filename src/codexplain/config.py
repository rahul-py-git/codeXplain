"""Configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def allowed_root() -> Path:
    return Path(os.getenv("CODEXPLAIN_ALLOWED_ROOT", ".")).expanduser().resolve()

def max_file_bytes() -> int:
    return max(1, int(os.getenv("CODEXPLAIN_MAX_FILE_BYTES", "300000")))

def max_files() -> int:
    return max(1, int(os.getenv("CODEXPLAIN_MAX_FILES", "500")))

def chunk_lines() -> int:
    return max(10, int(os.getenv("CODEXPLAIN_CHUNK_LINES", "100")))

def overlap_lines() -> int:
    return max(0, min(chunk_lines() - 1, int(os.getenv("CODEXPLAIN_OVERLAP_LINES", "15"))))
