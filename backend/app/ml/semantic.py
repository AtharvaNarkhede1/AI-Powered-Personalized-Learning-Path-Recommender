"""TF-IDF -> Truncated SVD (LSA) semantic space, fitted on the course corpus.

One fitted space serves every semantic need in the app: course recommendations,
"similar courses", career matching, and known-skill / required-skill matching.
Pickled to disk keyed by the dataset's (mtime, row count) so restarts are fast.
"""
from __future__ import annotations

import os
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from app.ml.catalog import Catalog

SVD_COMPONENTS = 256
TFIDF_MAX_FEATURES = 40000


class SemanticSpace:
    def __init__(self, vectorizer: TfidfVectorizer, svd: TruncatedSVD, course_vectors: np.ndarray):
        self.vectorizer = vectorizer
        self.svd = svd
        self.course_vectors = course_vectors            # (n_courses, k) L2-normalized

    # ---- fitting -------------------------------------------------------------
    @classmethod
    def fit(cls, catalog: Catalog) -> "SemanticSpace":
        docs = catalog.docs
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), stop_words="english", sublinear_tf=True,
            min_df=2, max_features=TFIDF_MAX_FEATURES,
        )
        tfidf = vectorizer.fit_transform(docs)
        k = min(SVD_COMPONENTS, min(tfidf.shape) - 1)
        svd = TruncatedSVD(n_components=k, random_state=42)
        reduced = svd.fit_transform(tfidf)
        course_vectors = normalize(reduced)
        return cls(vectorizer, svd, course_vectors)

    # ---- queries ----------------------------------------------------------
    def encode(self, text: str) -> np.ndarray:
        vec = self.svd.transform(self.vectorizer.transform([(text or "").lower()]))
        return normalize(vec)[0]

    def cosine_to_courses(self, vec: np.ndarray) -> np.ndarray:
        return np.clip(self.course_vectors @ vec, 0.0, 1.0)

    def similar_courses(self, text: str, k: int = 6, exclude: int | None = None):
        sims = self.cosine_to_courses(self.encode(text))
        order = np.argsort(-sims)
        out = []
        for pos in order:
            if exclude is not None and pos == exclude:
                continue
            out.append((int(pos), float(sims[pos])))
            if len(out) >= k:
                break
        return out

    def similar_to_course(self, pos: int, k: int = 6):
        sims = np.clip(self.course_vectors @ self.course_vectors[pos], 0.0, 1.0)
        order = np.argsort(-sims)
        return [(int(p), float(sims[p])) for p in order if p != pos][:k]

    def text_similarity(self, a: str, b: str) -> float:
        """Cosine similarity between two free-text strings in the LSA space.
        Used by career_engine / skill_gap_engine to replace substring matching."""
        if not a or not b:
            return 0.0
        return float(np.clip(self.encode(a) @ self.encode(b), 0.0, 1.0))

    def best_text_similarity(self, query: str, candidates) -> float:
        return max((self.text_similarity(query, c) for c in candidates), default=0.0)


# ---- disk cache ---------------------------------------------------------------
def _cache_key(csv_path: str, n_rows: int) -> str:
    mtime = int(os.path.getmtime(csv_path))
    return f"{mtime}-{n_rows}"


def load_or_fit(catalog: Catalog, csv_path: str, cache_dir: str) -> SemanticSpace:
    import joblib

    os.makedirs(cache_dir, exist_ok=True)
    key = _cache_key(csv_path, len(catalog))
    path = os.path.join(cache_dir, "semantic.pkl")
    if os.path.exists(path):
        try:
            blob = joblib.load(path)
            if blob.get("key") == key:
                return SemanticSpace(blob["vectorizer"], blob["svd"], blob["course_vectors"])
        except Exception:
            pass
    space = SemanticSpace.fit(catalog)
    try:
        joblib.dump(
            {"key": key, "vectorizer": space.vectorizer, "svd": space.svd,
             "course_vectors": space.course_vectors},
            path, compress=3,
        )
    except Exception:
        pass
    return space
