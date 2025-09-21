import pandas as pd

def load_faqs(path: str = "data/faqs.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize columns
    df.columns = [c.strip().lower() for c in df.columns]
    expected = {"category", "question", "answer"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in faqs.csv: {missing}")
    df = df.dropna(subset=["question", "answer"]).reset_index(drop=True)
    return df
