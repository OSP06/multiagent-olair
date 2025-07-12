# utils/file_utils.py
import csv
import os
import pandas as pd
from typing import List, Dict, Any

def load_internal_knowledge_base(csv_path: str) -> List[Dict[str, str]]:
    """
    Loads internal knowledge base CSV as a list of {"question": ..., "answer": ...} pairs.
    Expects a CSV with headers: 'question', 'answer'
    
    Args:
        csv_path: Path to the CSV file containing Q&A pairs
        
    Returns:
        List of dictionaries with question and answer keys
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is empty or missing required fields
        RuntimeError: For other CSV reading errors
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ CSV file not found at: {csv_path}")

    qa_pairs = []
    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = row.get("question", "").strip()
                answer = row.get("answer", "").strip()
                if question and answer:
                    qa_pairs.append({"question": question, "answer": answer})

        if not qa_pairs:
            raise ValueError("⚠️ CSV file is empty or missing required fields.")
        return qa_pairs

    except Exception as e:
        raise RuntimeError(f"❌ Failed to read internal KB CSV: {e}")
    
def load_commercial_lease_csv(path: str = None) -> List[Dict[str, Any]]:
    """
    Loads commercial lease data CSV as a list of dictionaries.
    Each dictionary represents a row from the CSV.
    
    Args:
        path: Path to the CSV file (optional, defaults to data/master_clause.csv)
        
    Returns:
        List of dictionaries containing lease data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        RuntimeError: For CSV loading errors
    """
    if path is None:
        path = os.path.join("data", "master_clause.csv")
        
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Lease data file not found: {path}")

    try:
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load commercial lease CSV: {e}")

def validate_csv_columns(csv_path: str, required_columns: List[str]) -> bool:
    """
    Validate that a CSV file contains the required columns.
    
    Args:
        csv_path: Path to the CSV file
        required_columns: List of column names that must be present
        
    Returns:
        True if all required columns are present
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ CSV file not found at: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path, nrows=0)  # Read only headers
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"❌ Missing required columns: {missing_columns}")
        
        return True
    except Exception as e:
        raise RuntimeError(f"❌ Failed to validate CSV columns: {e}")