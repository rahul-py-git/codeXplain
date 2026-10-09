"""Dependency-light lexical retrieval for the first version."""
import re
from collections import Counter
from .repository import CodeChunk

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,}|\d+")
STOP_WORDS = {"the", "and", "for", "with", "from", "this", "that", "what", "where", "when", "does", "how", "are", "can", "you", "please", "explain", "code"}

def tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOP_WORDS]

def retrieve(question: str, chunks: list[CodeChunk], limit: int = 8) -> list[CodeChunk]:
    query_counts = Counter(tokens(question))
    if not query_counts:
        return chunks[:limit]
    scored: list[tuple[float, CodeChunk]] = []
    for chunk in chunks:
        body = tokens(chunk.text)
        if not body:
            continue
        counts = Counter(body)
        overlap = sum(min(counts[token], amount) for token, amount in query_counts.items())
        if overlap == 0:
            continue
        density = overlap / max(1, len(body) ** 0.5)
        identifier_bonus = sum(1.5 for token in query_counts if token in chunk.text)
        scored.append((density + identifier_bonus, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:limit]]
