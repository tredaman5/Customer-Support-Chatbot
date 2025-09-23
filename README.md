# 💬 Customer Support Chatbot

An interactive **Customer Support Chatbot** built with **Streamlit**, **pandas**, **sentence-transformers**, and **SQLite**.  
It answers FAQs for a fake company and logs user interactions for simple analytics.

---

## 🚀 Features

- **Semantic Search** — uses embeddings (`all-MiniLM-L6-v2`) to match user questions with the closest FAQ.
- **Multi-turn Chat** — remembers recent conversation turns for better context.
- **Streamlit Web App** — clean chat UI with chat bubbles, category filters, and an analytics preview.
- **Analytics Logging** — saves questions and matches to a local SQLite database (`analytics/usage.db`).

---

## 📂 Project Structure
```plaintext
customer-support-chatbot/
├── app.py # Streamlit app entry point
├── core/
│ ├── chatbot.py # Chatbot logic + logging
│ ├── faq_loader.py # Loads and validates faqs.csv
│ └── retriever.py # Embedding-based semantic search
├── data/
│ └── faqs.csv # FAQ dataset (editable)
├── analytics/
│ └── usage.db # Created automatically on first run
├── requirements.txt
└── README.md
```
## 🖥️ How to Run Locally

Follow these **five steps** to get the chatbot running on your machine:

1. **Clone or Download the Repo**
   ```bash
   git clone https://github.com/YOUR-USERNAME/customer-support-chatbot.git
   cd customer-support-chatbot
(Or download as a ZIP and extract to a folder.)

Create and Activate a Virtual Environment

### Windows (PowerShell):
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
You should see (.venv) at the beginning of your terminal prompt.

### Install Dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
Note: The first run will download the sentence-transformers model (~100MB).

Ensure Required Folders Exist

```bash
mkdir analytics
Confirm that you have a data/faqs.csv file (this is your FAQ dataset).
```
### Run the Web App

```bash
streamlit run app.py
```
This will start a local web server and open a browser window (usually at http://localhost:8501).

