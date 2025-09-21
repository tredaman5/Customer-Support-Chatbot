from transformers import pipeline
import pandas as pd

# Load FAQ dataset
faq_df = pd.read_csv("faqs.csv")

# Load Q&A model
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def get_answer(user_question):
    best_answer = None
    best_score = 0
    for _, row in faq_df.iterrows():
        context = row['answer']
        result = qa_pipeline(question=user_question, context=context)
        if result['score'] > best_score:
            best_score = result['score']
            best_answer = context
    return best_answer or "Sorry, I don’t know the answer to that yet."
