import streamlit as st
import pandas as pd
import sqlite3
from core.chatbot import Chatbot
from core.faq_loader import load_faqs

st.set_page_config(page_title="Customer Support Chatbot", page_icon="💬", layout="centered")

st.title("💬 Customer Support Chatbot")
st.caption("Ask anything about FakeCompany — hours, billing, orders, security, and more.")

# Sidebar: filters and analytics toggle
faq_df = load_faqs()
all_categories = sorted(faq_df["category"].unique().tolist())
with st.sidebar:
    st.header("⚙️ Controls")
    selected = st.multiselect("Filter by category (optional)", options=all_categories, default=[])
    show_history = st.checkbox("Show chat history panel", value=True)
    st.markdown("---")
    st.subheader("📈 Analytics (preview)")
    show_analytics = st.checkbox("Show usage analytics", value=False)
    if show_analytics:
        conn = sqlite3.connect("analytics/usage.db")
        df = pd.read_sql_query("SELECT * FROM interactions ORDER BY id DESC LIMIT 200", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=250)
            st.write("Top matched questions (last 200):")
            topq = df["matched_question"].value_counts().head(10).rename_axis("question").reset_index(name="count")
            st.table(topq)
        else:
            st.info("No analytics yet. Ask a few questions to populate data.")

# Initialize app state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "bot" not in st.session_state:
    st.session_state.bot = Chatbot()

# History panel
if show_history and st.session_state.messages:
    with st.expander("🕘 Conversation History", expanded=False):
        for m in st.session_state.messages:
            st.write(f"**{m['role'].title()}:** {m['content']}")

# Chat UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your question (e.g., 'What are your business hours?')")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        result = st.session_state.bot.answer(prompt, history=st.session_state.messages, categories=selected or None)
        st.markdown(result["answer"])

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

st.markdown("---")
st.caption("Tip: Update `data/faqs.csv` with your own company FAQs to customize the bot.")
