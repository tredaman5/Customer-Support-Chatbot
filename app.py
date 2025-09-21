import streamlit as st
from chatbot import get_answer

st.title("💬 Customer Support Chatbot")
st.write("Ask me a question about FakeCompany!")

user_question = st.text_input("Your question:")
if user_question:
    answer = get_answer(user_question)
    st.success(answer)
