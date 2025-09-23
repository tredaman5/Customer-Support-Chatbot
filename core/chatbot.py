# core/chatbot.py

import re
from typing import List, Dict, Optional
import sqlite3
from datetime import datetime
from .retriever import FAQRetriever

MEMORY_TURNS = 4  # how many recent turns to keep in context

SMALL_TALK_RESPONSES = {
    r"\b(hi|hello|hey|yo|sup)\b": "Hey there! 👋 How can I help you today?",
    r"how are you": "I'm doing great, thanks for asking! 😊 What can I help you with?",
    r"thank(s| you)": "You're very welcome! 🙌",
    r"(bye|goodbye|see you)": "Goodbye! Have a great day! 👋",
    r"(who are you|what are you)": "I'm your friendly FakeCompany support bot! 🤖",
}

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
        recent = [h["content"] for h in history if h["role"] == "user"][-MEMORY_TURNS:]
        joined = " ".join(recent[-MEMORY_TURNS:])
        if len(new_question.strip().split()) <= 4 and joined:
            return joined + " " + new_question
        return new_question

    def _check_small_talk(self, text: str) -> Optional[str]:
        """Returns a casual response if text matches small talk patterns."""
        lowered = text.lower()
        for pattern, response in SMALL_TALK_RESPONSES.items():
            if re.search(pattern, lowered):
                return response
        return None

    def answer(self, question: str, history: Optional[List[Dict]] = None, categories: Optional[List[str]] = None):
        history = history or []

        # 🔑 Check small talk first
        casual_reply = self._check_small_talk(question)
        if casual_reply:
            self._log(question, None, casual_reply, "small-talk", None)
            return {"answer": casual_reply, "match": None}

        # Otherwise fall back to FAQ search
        enriched_q = self._build_context_query(history, question)
        match = self.retriever.best_match(enriched_q, categories=categories)
        if not match:
            answer = "I'm not fully sure about that yet, but I'd love to help! Could you be more specific? 🤔"
            self._log(question, None, answer, None, None)
            return {"answer": answer, "match": None}

        self._log(question, match["question"], match["answer"], match["category"], match["score"])
        return {"answer": match["answer"], "match": match}
