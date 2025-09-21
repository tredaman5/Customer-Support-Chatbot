from typing import List, Tuple, Optional
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from .faq_loader import load_faqs

EMBEDDINGS_PATH = "data/faq_embeddings.npy"
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_MIN_SCORE = 0.35  # adjust to be stricter/looser

class FAQRetriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.faq_df = load_faqs()
        self._ensure_embeddings()

    def _ensure_embeddings(self):
        # compute embeddings over the QUESTION field
        questions = self.faq_df["question"].tolist()
        if os.path.exists(EMBEDDINGS_PATH):
            try:
                self.embeddings = np.load(EMBEDDINGS_PATH)
                if self.embeddings.shape[0] != len(questions):
                    raise ValueError("Embeddings out of sync with FAQs; rebuilding.")
                return
            except Exception:
                pass
        self.embeddings = self.model.encode(questions, convert_to_numpy=True, normalize_embeddings=True)
        os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
        np.save(EMBEDDINGS_PATH, self.embeddings)

    def search(self, query: str, top_k: int = 5, categories: Optional[List[str]] = None) -> List[Tuple[int, float]]:
        # Optionally filter to categories
        idx = np.arange(len(self.faq_df))
        if categories:
            mask = self.faq_df["category"].isin(categories)
            idx = np.where(mask)[0]
        if idx.size == 0:
            return []

        # build view of embeddings & compute cosine sim
        emb_view = self.embeddings[idx]
        q_emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        sims = util.cos_sim(q_emb, emb_view).cpu().numpy().reshape(-1)

        top_k = min(top_k, len(idx))
        order = sims.argsort()[::-1][:top_k]
        results = [(int(idx[i]), float(sims[i])) for i in order]
        return results

    def best_match(self, query: str, categories: Optional[List[str]] = None, min_score: float = DEFAULT_MIN_SCORE):
        ranked = self.search(query, top_k=5, categories=categories)
        if not ranked:
            return None
        best_idx, score = ranked[0]
        if score < min_score:
            return None
        row = self.faq_df.iloc[best_idx]
        return {
            "index": int(best_idx),
            "score": float(score),
            "category": row["category"],
            "question": row["question"],
            "answer": row["answer"],
        }
