# models/clause_classifier.py
import re
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

def clean_text(text):
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

def train_clause_classifier(X: pd.Series, y, save_path: str):
    X_clean = X.apply(clean_text)
    model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 3), max_features=10000)),
        ('clf', LogisticRegression(max_iter=1000, random_state=42))
    ])
    model.fit(X_clean, y)
    joblib.dump(model, save_path)

def load_model(path: str):
    return joblib.load(path)