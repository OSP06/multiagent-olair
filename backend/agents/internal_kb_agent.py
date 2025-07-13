# agents/internal_kb_agent.py
import os
import pandas as pd
from typing import Dict, Any, List, Optional
from utils.file_utils import load_internal_knowledge_base
from utils.embedding_utils import get_embedding, get_embeddings
from utils.retriever import LeaseVectorStore
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Vector store paths for different knowledge bases
QA_VECTOR_PATH = os.path.join("data", "qa_internal_kb_vector_store.pkl")
PROPERTY_VECTOR_PATH = os.path.join("data", "property_kb_vector_store.pkl")
MASTER_CLAUSES_VECTOR_PATH = os.path.join("data", "master_clauses_vector_store.pkl")

class InternalKBAgent:
    def __init__(self, qa_csv_path=None, property_csv_path=None, master_clauses_csv_path=None):
        self.qa_csv_path = qa_csv_path or os.path.join("data", "qa_internal_kb.csv")
        self.property_csv_path = property_csv_path or os.path.join("data", "HackathonInternalKnowledgeBase.csv")
        self.master_clauses_csv_path = master_clauses_csv_path or os.path.join("data", "master_clauses.csv")

        self.qa_vector_store = None
        self.property_vector_store = None
        self.master_clauses_vector_store = None

        self.qa_data = None
        self.property_data = None
        self.master_clauses_data = None

    def load_qa_data(self):
        if self.qa_data is None:
            try:
                df = pd.read_csv(self.qa_csv_path)
                self.qa_data = [{"question": row["question"], "answer": row["answer"]} for _, row in df.iterrows()]
            except Exception as e:
                print(f"⚠️ Error loading QA data: {e}")
                self.qa_data = []
        return self.qa_data

    def load_property_data(self):
        if self.property_data is None:
            try:
                df = pd.read_csv(self.property_csv_path)
                self.property_data = df.to_dict('records')
            except Exception as e:
                print(f"⚠️ Error loading property data: {e}")
                self.property_data = []
        return self.property_data

    def load_master_clauses_data(self):
        if self.master_clauses_data is None:
            try:
                df = pd.read_csv(self.master_clauses_csv_path)
                self.master_clauses_data = df.to_dict('records')
            except Exception as e:
                print(f"⚠️ Error loading master clauses data: {e}")
                self.master_clauses_data = []
        return self.master_clauses_data

    def build_vector_store(self, kb_type, force_rebuild=False):
        if kb_type == "qa":
            return self._build_qa_vector_store(force_rebuild)
        elif kb_type == "property":
            return self._build_property_vector_store(force_rebuild)
        elif kb_type == "master_clauses":
            return self._build_master_clauses_vector_store(force_rebuild)
        else:
            raise ValueError(f"Unknown knowledge base type: {kb_type}")

    def _build_qa_vector_store(self, force_rebuild=False):
        if self.qa_vector_store is not None and not force_rebuild:
            return self.qa_vector_store

        if os.path.exists(QA_VECTOR_PATH) and not force_rebuild:
            try:
                self.qa_vector_store = LeaseVectorStore()
                self.qa_vector_store.load(QA_VECTOR_PATH)
                return self.qa_vector_store
            except Exception as e:
                print(f"⚠️ Failed to load QA vector store: {e}")

        qa_data = self.load_qa_data()
        if not qa_data:
            return None

        questions = [item["question"] for item in qa_data]
        answers = [item["answer"] for item in qa_data]

        try:
            embeddings = get_embeddings(questions)
            self.qa_vector_store = LeaseVectorStore()
            self.qa_vector_store.add_embeddings(embeddings, answers)
            self.qa_vector_store.save(QA_VECTOR_PATH)
            print("✅ QA vector store saved")
        except Exception as e:
            print(f"⚠️ Error building QA vector store: {e}")
            self.qa_vector_store = None

        return self.qa_vector_store

    def _build_property_vector_store(self, force_rebuild=False):
        if self.property_vector_store is not None and not force_rebuild:
            return self.property_vector_store

        if os.path.exists(PROPERTY_VECTOR_PATH) and not force_rebuild:
            try:
                self.property_vector_store = LeaseVectorStore()
                self.property_vector_store.load(PROPERTY_VECTOR_PATH)
                return self.property_vector_store
            except Exception as e:
                print(f"⚠️ Failed to load property vector store: {e}")

        df = pd.read_csv(self.property_csv_path)
        texts = df.apply(lambda row: ' '.join([str(x) for x in row.values]), axis=1).tolist()

        try:
            embeddings = get_embeddings(texts)
            self.property_vector_store = LeaseVectorStore()
            self.property_vector_store.add_embeddings(embeddings, texts)
            self.property_vector_store.save(PROPERTY_VECTOR_PATH)
            print("✅ Property vector store saved")
        except Exception as e:
            print(f"⚠️ Error building property vector store: {e}")
            self.property_vector_store = None

        return self.property_vector_store

    def _build_master_clauses_vector_store(self, force_rebuild=False):
        if self.master_clauses_vector_store is not None and not force_rebuild:
            return self.master_clauses_vector_store

        if os.path.exists(MASTER_CLAUSES_VECTOR_PATH) and not force_rebuild:
            try:
                self.master_clauses_vector_store = LeaseVectorStore()
                self.master_clauses_vector_store.load(MASTER_CLAUSES_VECTOR_PATH)
                return self.master_clauses_vector_store
            except Exception as e:
                print(f"⚠️ Failed to load master clauses vector store: {e}")

        df = pd.read_csv(self.master_clauses_csv_path)
        texts = df.apply(lambda row: ' '.join([str(x) for x in row.values]), axis=1).tolist()

        try:
            embeddings = get_embeddings(texts)
            self.master_clauses_vector_store = LeaseVectorStore()
            self.master_clauses_vector_store.add_embeddings(embeddings, texts)
            self.master_clauses_vector_store.save(MASTER_CLAUSES_VECTOR_PATH)
            print("✅ Master clauses vector store saved")
        except Exception as e:
            print(f"⚠️ Error building master clauses vector store: {e}")
            self.master_clauses_vector_store = None

        return self.master_clauses_vector_store

    def search_kb(self, query, kb_type=None, top_k=3):
        if kb_type == "qa":
            store = self._build_qa_vector_store()
        elif kb_type == "property":
            store = self._build_property_vector_store()
        elif kb_type == "master_clauses":
            store = self._build_master_clauses_vector_store()
        else:
            store = self._build_qa_vector_store()

        if not store:
            return []

        query_vec = get_embedding(query)
        results = store.search(query_vec, k=top_k)
        return results

def answer_internal_question(
    user_question: str,
    top_k: int = 3,
    kb_type: Optional[str] = None,
    qa_csv_path: str = None,
    property_csv_path: str = None,
    master_clauses_csv_path: str = None,
    use_llm: bool = True
) -> str:
    if not user_question.strip():
        return "❌ Please provide a question."

    try:
        agent = InternalKBAgent(qa_csv_path, property_csv_path, master_clauses_csv_path)
        results = agent.search_kb(user_question, kb_type=kb_type, top_k=top_k)

        if not results:
            return "🤔 No relevant information found in internal knowledge base."

        return "\n".join([r["text"] if isinstance(r, dict) and "text" in r else str(r) for r in results])

    except Exception as e:
        return f"❌ Error processing question: {str(e)}"

def get_kb_stats(
    qa_csv_path: str = None,
    property_csv_path: str = None,
    master_clauses_csv_path: str = None
) -> Dict[str, Any]:
    agent = InternalKBAgent(qa_csv_path, property_csv_path, master_clauses_csv_path)

    return {
        "qa_pairs": len(agent.load_qa_data()),
        "property_records": len(agent.load_property_data()),
        "clause_records": len(agent.load_master_clauses_data()),
        "vector_stores": {
            "qa": os.path.exists(QA_VECTOR_PATH),
            "property": os.path.exists(PROPERTY_VECTOR_PATH),
            "master_clauses": os.path.exists(MASTER_CLAUSES_VECTOR_PATH)
        }
    }

def rebuild_all_vector_stores(
    qa_csv_path: str = None,
    property_csv_path: str = None,
    master_clauses_csv_path: str = None
) -> Dict[str, bool]:
    agent = InternalKBAgent(qa_csv_path, property_csv_path, master_clauses_csv_path)
    result = {}
    for kb in ["qa", "property", "master_clauses"]:
        try:
            agent.build_vector_store(kb, force_rebuild=True)
            result[kb] = True
        except Exception:
            result[kb] = False
    return result