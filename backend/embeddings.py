from __future__ import annotations

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

_model = None


def _get_model():
    global _model
    if not _AVAILABLE:
        return None
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model


def encode(text: str) -> bytes | None:
    if not _AVAILABLE:
        return None
    try:
        model = _get_model()
        if model is None:
            return None
        vec = model.encode(text, normalize_embeddings=True)
        return vec.astype("float32").tobytes()
    except Exception:
        return None


def encode_batch(texts: list[str]) -> list[bytes | None]:
    if not _AVAILABLE:
        return [None] * len(texts)
    try:
        model = _get_model()
        if model is None:
            return [None] * len(texts)
        vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.astype("float32").tobytes() for v in vecs]
    except Exception:
        return [None] * len(texts)


def cosine_similarity(a_bytes: bytes, b_bytes: bytes) -> float:
    if not _AVAILABLE:
        return 0.0
    try:
        import numpy as np
        a = np.frombuffer(a_bytes, dtype="float32")
        b = np.frombuffer(b_bytes, dtype="float32")
        return float(np.dot(a, b))
    except Exception:
        return 0.0
