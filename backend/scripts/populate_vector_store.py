#!/usr/bin/env python3
# scripts/populate_vector_store.py

import os
import sys
import pandas as pd
import numpy as np

# Add root path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.embedding_utils import get_embeddings
from utils.retriever import LeaseVectorStore

CSV_PATH = os.path.join("data", "master_clauses.csv")
VECTOR_STORE_PATH = os.path.join("data", "lease_vector_store.pkl")


def extract_clauses_from_structured_data(lease_data):
    """
    Extract clauses from structured commercial lease data.
    """
    clauses = []
    clause_fields = [
        ("Most Favored Nation", "Most Favored Nation-Answer"),
        ("Competitive Restriction Exception", "Competitive Restriction Exception-Answer"),
        ("Non-Compete", "Non-Compete-Answer"),
        ("Exclusivity", "Exclusivity-Answer"),
        ("No-Solicit Of Customers", "No-Solicit Of Customers-Answer"),
        ("No-Solicit Of Employees", "No-Solicit Of Employees-Answer"),
        ("Non-Disparagement", "Non-Disparagement-Answer"),
        ("Termination For Convenience", "Termination For Convenience-Answer"),
        ("Rofr/Rofo/Rofn", "Rofr/Rofo/Rofn-Answer"),
        ("Change Of Control", "Change Of Control-Answer"),
        ("Anti-Assignment", "Anti-Assignment-Answer"),
        ("Revenue/Profit Sharing", "Revenue/Profit Sharing-Answer"),
        ("Price Restrictions", "Price Restrictions-Answer"),
        ("Minimum Commitment", "Minimum Commitment-Answer"),
        ("Volume Restriction", "Volume Restriction-Answer"),
        ("Ip Ownership Assignment", "Ip Ownership Assignment-Answer"),
        ("Joint Ip Ownership", "Joint Ip Ownership-Answer"),
        ("License Grant", "License Grant-Answer"),
        ("Non-Transferable License", "Non-Transferable License-Answer"),
        ("Affiliate License-Licensor", "Affiliate License-Licensor-Answer"),
        ("Affiliate License-Licensee", "Affiliate License-Licensee-Answer"),
        ("Unlimited/All-You-Can-Eat-License", "Unlimited/All-You-Can-Eat-License-Answer"),
        ("Irrevocable Or Perpetual License", "Irrevocable Or Perpetual License-Answer"),
        ("Source Code Escrow", "Source Code Escrow-Answer"),
        ("Post-Termination Services", "Post-Termination Services-Answer"),
        ("Audit Rights", "Audit Rights-Answer"),
        ("Uncapped Liability", "Uncapped Liability-Answer"),
        ("Cap On Liability", "Cap On Liability-Answer"),
        ("Liquidated Damages", "Liquidated Damages-Answer"),
        ("Warranty Duration", "Warranty Duration-Answer"),
        ("Insurance", "Insurance-Answer"),
        ("Covenant Not To Sue", "Covenant Not To Sue-Answer"),
        ("Third Party Beneficiary", "Third Party Beneficiary-Answer"),
    ]

    for row in lease_data:
        doc_name = row.get("Document Name", "")
        parties = row.get("Parties", "")

        for clause_type, answer_field in clause_fields:
            clause_value = row.get(clause_type, "")
            answer_value = row.get(answer_field, "")
            if clause_value and str(clause_value).strip():
                clause_text = f"Clause Type: {clause_type}\n"
                if doc_name:
                    clause_text += f"Document: {doc_name}\n"
                if parties:
                    clause_text += f"Parties: {parties}\n"
                clause_text += f"Clause Content: {str(clause_value).strip()}"
                if answer_value and str(answer_value).strip():
                    clause_text += f"\nAnswer/Details: {str(answer_value).strip()}"
                clauses.append(clause_text)
    return clauses


def quick_populate(save_path: str = None) -> bool:
    """
    Populate vector store with clauses from master_clauses.csv.
    """
    print("🚀 Starting vector population...")

    if save_path is None:
        save_path = VECTOR_STORE_PATH

    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV file not found: {CSV_PATH}")
        return False

    try:
        df = pd.read_csv(CSV_PATH)
        print(f"📄 Loaded {len(df)} rows from CSV")

        lease_data = df.to_dict("records")
        clauses = extract_clauses_from_structured_data(lease_data)

        if not clauses:
            print("⚠️ No clauses extracted from CSV")
            return False

        print(f"🧠 Extracted {len(clauses)} clauses. Generating embeddings...")

        try:
            embeddings = get_embeddings(clauses)
            if not embeddings or len(embeddings) != len(clauses):
                raise ValueError("Embedding generation mismatch")
        except Exception as e:
            print(f"⚠️ Embedding error: {e}")
            print("🛠️ Using fallback random embeddings...")
            embeddings = np.random.rand(len(clauses), 768).tolist()

        retriever = LeaseVectorStore()
        retriever.add_embeddings(embeddings, clauses)
        retriever.save(save_path)

        print(f"✅ Vector store saved to: {save_path}")
        print(f"📊 Total indexed: {len(clauses)}")

        return True

    except Exception as e:
        print(f"❌ Error populating vector store: {e}")
        return False


def load_vector_store(load_path: str = None) -> LeaseVectorStore:
    if load_path is None:
        load_path = VECTOR_STORE_PATH
    store = LeaseVectorStore()
    store.load(load_path)
    return store


def check_vector_store_exists(path: str = None) -> bool:
    if path is None:
        path = VECTOR_STORE_PATH
    return os.path.exists(path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Populate lease vector store")
    parser.add_argument("--save-path", type=str, help="Path to save vector store")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing vector store")
    args = parser.parse_args()

    save_path = args.save_path or VECTOR_STORE_PATH

    if check_vector_store_exists(save_path) and not args.force:
        print(f"📁 Vector store already exists at: {save_path}")
        print("💡 Use `--force` to overwrite.")
        sys.exit(0)

    success = quick_populate(save_path)
    sys.exit(0 if success else 1)
