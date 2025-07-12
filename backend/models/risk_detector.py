# models/risk_detector.py
import os
import re
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_multi_label_model.joblib")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "tfidf_vectorizer.joblib")

# Try loading model and vectorizer
try:
    risk_model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except Exception:
    risk_model = None
    vectorizer = None

RISK_LABELS = [
    "Indemnity Risk", "Termination Risk", "Penalty Risk", "Renewal Risk",
    "Arbitration Risk", "Exclusivity Risk", "Escalation Risk", "Liability Risk", "Insurance Risk"
]

RISKY_KEYWORDS = {
    "indemnify": "Indemnity: Broad indemnification may expose tenants to unlimited liability.",
    "termination": "Termination: Unilateral termination rights or short notice periods may be high risk.",
    "penalty": "Penalty: Excessive penalties can be unenforceable and burdensome.",
    "renewal": "Renewal: Automatic renewal without clear terms can trap parties in long contracts.",
    "arbitration": "Arbitration: Mandatory arbitration clauses may limit legal remedies.",
    "exclusive": "Exclusivity: Exclusive use clauses may prevent competitive use of premises.",
    "escalation": "Escalation: Uncapped rent escalation can significantly increase costs.",
    "liability": "Liability: Broad liability terms can shift undue burden to tenant.",
    "insurance": "Insurance: Lack of clear insurance coverage may create coverage gaps."
}


def detect_risk(clause_text: str):
    clause_text = clause_text.strip()
    if not clause_text:
        return False, "✅ Clause appears low risk (empty clause)."

    # ML-based detection
    if risk_model and vectorizer:
        X_vec = vectorizer.transform([clause_text])
        proba = risk_model.predict_proba(X_vec)[0]
        risks = [f"{label} (confidence: {p:.2f})"
                for label, p in zip(RISK_LABELS, proba) if p > 0.5]
        if risks:
            return True, "⚠️ Risks detected: " + " | ".join(risks)
        return False, "✅ ML model found no risk."

    # Keyword fallback
    risks_found = [msg for kw, msg in RISKY_KEYWORDS.items()
                if re.search(rf"\b{kw}\b", clause_text, re.IGNORECASE)]
    if risks_found:
        return True, "⚠️ " + " | ".join(risks_found)
    return False, "✅ Clause appears low risk."