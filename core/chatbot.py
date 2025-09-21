from typing import List, Dict, Optional
import sqlite3
from datetime import datetime
from .retriever import FAQRetriever

MEMORY_TURNS = 4  # how many recent turns to keep in context

class Chatbot:
    def __init__(self, db_path: str = "analytics/usage.db"):
        self.retriever = FAQRetriever()
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                user_question TEXT NOT NULL,
                matched_question TEXT,
                answer TEXT,
                category TEXT,
                score REAL
            )
            """
        )
        conn.commit()
        conn.close()

    def _log(self, user_question: str, matched_question: Optional[str], answer: Optional[str],
             category: Optional[str], score: Optional[float]):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO interactions (ts, user_question, matched_question, answer, category, score) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), user_question, matched_question, answer, category, score)
        )
        conn.commit()
        conn.close()

    def _build_context_query(self, history: List[Dict], new_question: str) -> str:
        # Very light-weight "context infusion": include last N user messages
        recent = [h["content"] for h in history if h["role"] == "user"][-MEMORY_TURNS:]
        joined = " ".join(recent[-MEMORY_TURNS:])
        # If the new question is very short, prepend last context
        if len(new_question.strip().split()) <= 4 and joined:
            return joined + " " + new_question
        return new_question

    def answer(self, question: str, history: Optional[List[Dict]] = None, categories: Optional[List[str]] = None):
        history = history or []
        enriched_q = self._build_context_query(history, question)
        match = self.retriever.best_match(enriched_q, categories=categories)
        if not match:
            answer = "I'm not fully sure about that yet. Please check our Help Center or contact support@fakecompany.com."
            self._log(question, None, answer, None, None)
            return {"answer": answer, "match": None}

        self._log(question, match["question"], match["answer"], match["category"], match["score"])
        return {"answer": match["answer"], "match": match}
