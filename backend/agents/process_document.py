from models.clause_classifier import classify_clauses
from models.risk_detector import detect_risks
from models.redline_suggestor import suggest_redlines
from summarization_agent import summarize_text

def process_document(text: str):
    """
    Processes a lease document or legal file and returns all AI/NLP outputs.
    """
    clauses = classify_clauses(text)
    risks = detect_risks(text)
    redlines = suggest_redlines(text)
    summary = summarize_text(text)

    return {
        "summary": summary,
        "clauses": clauses,
        "risks": risks,
        "redlines": redlines
    }
