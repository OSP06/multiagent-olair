# models/redline_suggestor.py
import re

REDLINE_SUGGESTIONS = {
    "indemnify": "Limit indemnity to direct damages and landlord's negligence.",
    "termination": "Add mutual termination clauses with at least 60 days' notice.",
    "penalty": "Replace penalties with reasonable liquidated damages.",
    "renewal": "Include tenant opt-out options and renewal caps.",
    "arbitration": "Make arbitration optional or allow court choice.",
    "exclusive": "Narrow exclusivity clauses to critical business needs.",
    "escalation": "Cap escalation rates and tie them to market indices.",
    "liability": "Clearly define liability limits and exclusions.",
    "insurance": "Specify both parties’ insurance responsibilities and coverage types."
}

def suggest_redline(clause_text: str):
    suggestions = [s for k, s in REDLINE_SUGGESTIONS.items()
                if re.search(rf"\b{k}\b", clause_text, re.IGNORECASE)]
    return " | ".join(suggestions) if suggestions else "No redline suggestion found."