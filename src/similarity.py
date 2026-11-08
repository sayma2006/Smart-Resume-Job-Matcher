import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_model = None
_model_attempted = False

def _get_embedding_model():
    """Load the optional local sentence-transformers model once."""
    global _model, _model_attempted
    if not _model_attempted:
        _model_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as exc:
            print(f"[similarity] Embeddings unavailable; using TF-IDF fallback. Details: {exc}")
            _model = None
    return _model

def _chunks(text: str, min_length: int = 25):
    chunks = re.split(r"[\n\r]+|(?<=[.!?])\s+", text or "")
    return [chunk.strip() for chunk in chunks if len(chunk.strip()) >= min_length]

def tfidf_similarity(resume: str, job_description: str) -> float:
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([resume or "", job_description or ""])
        raw = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        return round(float(np.clip(raw / 0.5, 0, 1) * 100), 1)
    except ValueError:
        return 0.0

def semantic_similarity(resume: str, job_description: str) -> dict:
    """
    Compare each job-description sentence to its best resume sentence.
    Returns a heuristic 0-100 score and the method used.
    The score is a similarity indicator, not a probability of being hired.
    """
    model = _get_embedding_model()
    resume_chunks = _chunks(resume)
    jd_chunks = _chunks(job_description)

    if model is None or not resume_chunks or not jd_chunks:
        return {"score": tfidf_similarity(resume, job_description), "method": "tfidf"}

    try:
        resume_vectors = model.encode(resume_chunks, normalize_embeddings=True)
        jd_vectors = model.encode(jd_chunks, normalize_embeddings=True)
        similarities = jd_vectors @ resume_vectors.T
        best_matches = similarities.max(axis=1)
        raw = float(best_matches.mean())
        # Heuristic normalization; validate/tune using labelled examples before production use.
        score = float(np.clip((raw - 0.20) / 0.60, 0, 1) * 100)
        return {"score": round(score, 1), "method": "sentence-transformers"}
    except Exception as exc:
        print(f"[similarity] Embedding inference failed; using TF-IDF. Details: {exc}")
        return {"score": tfidf_similarity(resume, job_description), "method": "tfidf"}
