from __future__ import annotations
import numpy as np

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model


def encode(text: str) -> bytes | None:
    """Encode a single text to a normalized float32 embedding stored as bytes."""
    try:
        vec = _get_model().encode(text, normalize_embeddings=True)
        return vec.astype("float32").tobytes()
    except Exception:
        return None


def encode_batch(texts: list[str]) -> list[bytes | None]:
    """Encode a list of texts in one pass (faster than calling encode() in a loop)."""
    try:
        vecs = _get_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.astype("float32").tobytes() for v in vecs]
    except Exception:
        return [None] * len(texts)


def cosine_similarity(a_bytes: bytes, b_bytes: bytes) -> float:
    """Cosine similarity between two normalized embeddings stored as bytes.
    Since both vectors are L2-normalized, cosine similarity == dot product."""
    a = np.frombuffer(a_bytes, dtype="float32")
    b = np.frombuffer(b_bytes, dtype="float32")
    return float(np.dot(a, b))
