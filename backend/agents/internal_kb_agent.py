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
    """
    Agent for answering questions from multiple internal knowledge bases.
    Handles three types of data:
    1. QA Internal KB (question-answer pairs)
    2. Property/Real Estate data
    3. Master Clauses (contract/legal data)
    """
    
    def __init__(self, 
                qa_csv_path: str = None,
                property_csv_path: str = None,
                master_clauses_csv_path: str = None):
        """
        Initialize the internal KB agent.
        
        Args:
            qa_csv_path: Path to QA internal KB CSV file
            property_csv_path: Path to property data CSV file
            master_clauses_csv_path: Path to master clauses CSV file
        """
        self.qa_csv_path = qa_csv_path or os.path.join("data", "qa_internal_kb.csv")
        self.property_csv_path = property_csv_path or os.path.join("data", "HackathonInternalKnowledgeBase.csv")
        self.master_clauses_csv_path = master_clauses_csv_path or os.path.join("data", "master_clauses.csv")
        
        self.qa_vector_store = None
        self.property_vector_store = None
        self.master_clauses_vector_store = None
        
        self.qa_data = None
        self.property_data = None
        self.master_clauses_data = None
        
    def load_qa_data(self) -> List[Dict[str, str]]:
        """Load QA internal knowledge base data from CSV."""
        if self.qa_data is None:
            try:
                df = pd.read_csv(self.qa_csv_path)
                self.qa_data = [
                    {"question": row["question"], "answer": row["answer"]}
                    for _, row in df.iterrows()
                ]
            except Exception as e:
                print(f"⚠️ Error loading QA data: {e}")
                self.qa_data = []
        return self.qa_data
    
    def load_property_data(self) -> List[Dict[str, Any]]:
        """Load property/real estate data from CSV."""
        if self.property_data is None:
            try:
                df = pd.read_csv(self.property_csv_path)
                self.property_data = df.to_dict('records')
            except Exception as e:
                print(f"⚠️ Error loading property data: {e}")
                self.property_data = []
        return self.property_data
    
    def load_master_clauses_data(self) -> List[Dict[str, Any]]:
        """Load master clauses data from CSV."""
        if self.master_clauses_data is None:
            try:
                df = pd.read_csv(self.master_clauses_csv_path)
                self.master_clauses_data = df.to_dict('records')
            except Exception as e:
                print(f"⚠️ Error loading master clauses data: {e}")
                self.master_clauses_data = []
        return self.master_clauses_data
    
    def create_property_search_texts(self) -> List[str]:
        """Create searchable text representations of property data."""
        property_data = self.load_property_data()
        search_texts = []
        
        for prop in property_data:
            # Create a searchable text combining key property information
            text_parts = []
            
            # Add property details
            if prop.get('Property Address'):
                text_parts.append(f"Property: {prop['Property Address']}")
            if prop.get('Floor'):
                text_parts.append(f"Floor: {prop['Floor']}")
            if prop.get('Suite'):
                text_parts.append(f"Suite: {prop['Suite']}")
            if prop.get('Size (SF)'):
                text_parts.append(f"Size: {prop['Size (SF)']} SF")
            if prop.get('Rent/SF/Year'):
                text_parts.append(f"Rent per SF: ${prop['Rent/SF/Year']}")
            if prop.get('Annual Rent'):
                text_parts.append(f"Annual Rent: ${prop['Annual Rent']}")
            if prop.get('Monthly Rent'):
                text_parts.append(f"Monthly Rent: ${prop['Monthly Rent']}")
            
            # Add broker information
            if prop.get('Associate 1'):
                text_parts.append(f"Associate: {prop['Associate 1']}")
            if prop.get('BROKER Email ID'):
                text_parts.append(f"Broker: {prop['BROKER Email ID']}")
            
            search_texts.append(" | ".join(text_parts))
        
        return search_texts
    
    def create_master_clauses_search_texts(self) -> List[str]:
        """Create searchable text representations of master clauses data."""
        clauses_data = self.load_master_clauses_data()
        search_texts = []
        
        for clause in clauses_data:
            # Create a searchable text combining key clause information
            text_parts = []
            
            # Add document details
            if clause.get('Document Name'):
                text_parts.append(f"Document: {clause['Document Name']}")
            if clause.get('Parties'):
                text_parts.append(f"Parties: {clause['Parties']}")
            
            # Add key terms and their answers
            key_terms = [
                'Agreement Date', 'Effective Date', 'Expiration Date', 'Renewal Term',
                'Governing Law', 'Non-Compete', 'Exclusivity', 'Termination For Convenience',
                'Anti-Assignment', 'License Grant', 'Warranty Duration', 'Insurance'
            ]
            
            for term in key_terms:
                if clause.get(term) and clause.get(f'{term}-Answer'):
                    text_parts.append(f"{term}: {clause[f'{term}-Answer']}")
            
            search_texts.append(" | ".join(text_parts))
        
        return search_texts
    
    def build_vector_store(self, kb_type: str, force_rebuild: bool = False):
        """Build or load vector store for specified knowledge base type."""
        if kb_type == "qa":
            return self._build_qa_vector_store(force_rebuild)
        elif kb_type == "property":
            return self._build_property_vector_store(force_rebuild)
        elif kb_type == "master_clauses":
            return self._build_master_clauses_vector_store(force_rebuild)
        else:
            raise ValueError(f"Unknown knowledge base type: {kb_type}")
    
    def _build_qa_vector_store(self, force_rebuild: bool = False):
        """Build QA vector store."""
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
            print(f"✅ QA vector store saved")
        except Exception as e:
            print(f"⚠️ Error building QA vector store: {e}")
            self.qa_vector_store = None
        
        return self.qa_vector_store
    
    def _build_property_vector_store(self, force_rebuild: bool = False):
        """Build property vector store."""
        if self.property_vector_store is not None and not force_rebuild:
            return self.property_vector_store
        
        if os.path.exists(PROPERTY_VECTOR_PATH) and not force_rebuild:
            try:
                self.property_vector_store = LeaseVectorStore()
                self.property_vector_store.load(PROPERTY_VECTOR_PATH)
                return self.property_vector_store
            except Exception as e:
                print(f"⚠️ Failed to load property vector store: {e}")
        
        search_texts = self.create_property_search_texts()
        if not search_texts:
            return None
        
        try:
            embeddings = get_embeddings(search_texts)
            self.property_vector_store = LeaseVectorStore()
            self.property_vector_store.add_embeddings(embeddings, search_texts)
            self.property_vector_store.save(PROPERTY_VECTOR_PATH)
            print(f"✅ Property vector store saved")
        except Exception as e:
            print(f"⚠️ Error building property vector store: {e}")
            self.property_vector_store = None
        
        return self.property_vector_store
    
    def _build_master_clauses_vector_store(self, force_rebuild: bool = False):
        """Build master clauses vector store."""
        if self.master_clauses_vector_store is not None and not force_rebuild:
            return self.master_clauses_vector_store
        
        if os.path.exists(MASTER_CLAUSES_VECTOR_PATH) and not force_rebuild:
            try:
                self.master_clauses_vector_store = LeaseVectorStore()
                self.master_clauses_vector_store.load(MASTER_CLAUSES_VECTOR_PATH)
                return self.master_clauses_vector_store
            except Exception as e:
                print(f"⚠️ Failed to load master clauses vector store: {e}")
        
        search_texts = self.create_master_clauses_search_texts()
        if not search_texts:
            return None
        
        try:
            embeddings = get_embeddings(search_texts)
            self.master_clauses_vector_store = LeaseVectorStore()
            self.master_clauses_vector_store.add_embeddings(embeddings, search_texts)
            self.master_clauses_vector_store.save(MASTER_CLAUSES_VECTOR_PATH)
            print(f"✅ Master clauses vector store saved")
        except Exception as e:
            print(f"⚠️ Error building master clauses vector store: {e}")
            self.master_clauses_vector_store = None
        
        return self.master_clauses_vector_store
    
    def classify_question(self, question: str) -> str:
        """
        Classify the question type to determine which knowledge base to use.
        
        Returns:
            'qa', 'property', or 'master_clauses'
        """
        question_lower = question.lower()
        
        # Property-related keywords
        property_keywords = [
            'property', 'address', 'floor', 'suite', 'rent', 'sf', 'square feet',
            'broker', 'associate', 'lease', 'monthly', 'annual', 'gci'
        ]
        
        # Legal/contract-related keywords
        legal_keywords = [
            'contract', 'agreement', 'clause', 'term', 'expiration', 'renewal',
            'governing law', 'non-compete', 'exclusivity', 'termination',
            'assignment', 'license', 'warranty', 'insurance', 'liability'
        ]
        
        # Count matches
        property_matches = sum(1 for keyword in property_keywords if keyword in question_lower)
        legal_matches = sum(1 for keyword in legal_keywords if keyword in question_lower)
        
        if property_matches > legal_matches:
            return 'property'
        elif legal_matches > property_matches:
            return 'master_clauses'
        else:
            return 'qa'  # Default to QA for general questions
    
    def search_kb(self, query: str, kb_type: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search specified knowledge base for relevant answers."""
        if kb_type is None:
            kb_type = self.classify_question(query)
        
        if kb_type == "qa":
            return self._search_qa_kb(query, top_k)
        elif kb_type == "property":
            return self._search_property_kb(query, top_k)
        elif kb_type == "master_clauses":
            return self._search_master_clauses_kb(query, top_k)
        else:
            return []
    
    def _search_qa_kb(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search QA knowledge base."""
        vector_store = self.build_vector_store("qa")
        
        if vector_store is not None:
            try:
                query_embedding = get_embedding(query)
                results = vector_store.search(query_embedding, k=top_k)
                
                qa_data = self.load_qa_data()
                formatted_results = []
                
                for result in results:
                    answer_text = result["text"]
                    matching_qa = next(
                        (qa for qa in qa_data if qa["answer"] == answer_text), 
                        None
                    )
                    
                    if matching_qa:
                        formatted_results.append({
                            "type": "qa",
                            "question": matching_qa["question"],
                            "answer": matching_qa["answer"],
                            "score": result["score"]
                        })
                
                return formatted_results
            except Exception as e:
                print(f"⚠️ QA vector search failed: {e}")
        
        return []
    
    def _search_property_kb(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search property knowledge base."""
        vector_store = self.build_vector_store("property")
        
        if vector_store is not None:
            try:
                query_embedding = get_embedding(query)
                results = vector_store.search(query_embedding, k=top_k)
                
                property_data = self.load_property_data()
                formatted_results = []
                
                for i, result in enumerate(results):
                    if i < len(property_data):
                        formatted_results.append({
                            "type": "property",
                            "data": property_data[i],
                            "score": result["score"]
                        })
                
                return formatted_results
            except Exception as e:
                print(f"⚠️ Property vector search failed: {e}")
        
        return []
    
    def _search_master_clauses_kb(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search master clauses knowledge base."""
        vector_store = self.build_vector_store("master_clauses")
        
        if vector_store is not None:
            try:
                query_embedding = get_embedding(query)
                results = vector_store.search(query_embedding, k=top_k)
                
                clauses_data = self.load_master_clauses_data()
                formatted_results = []
                
                for i, result in enumerate(results):
                    if i < len(clauses_data):
                        formatted_results.append({
                            "type": "master_clauses",
                            "data": clauses_data[i],
                            "score": result["score"]
                        })
                
                return formatted_results
            except Exception as e:
                print(f"⚠️ Master clauses vector search failed: {e}")
        
        return []


def answer_internal_question(
    user_question: str, 
    top_k: int = 3, 
    qa_csv_path: str = None,
    property_csv_path: str = None,
    master_clauses_csv_path: str = None,
    use_llm: bool = True
) -> str:
    """
    Answer a question using the appropriate internal knowledge base.
    
    Args:
        user_question: The user's question
        top_k: Number of top matches to consider
        qa_csv_path: Path to QA internal KB CSV
        property_csv_path: Path to property data CSV
        master_clauses_csv_path: Path to master clauses CSV
        use_llm: Whether to use LLM for answer generation
        
    Returns:
        Generated answer string
    """
    if not user_question.strip():
        return "❌ Please provide a question."
    
    try:
        # Initialize agent
        agent = InternalKBAgent(qa_csv_path, property_csv_path, master_clauses_csv_path)
        
        # Search for relevant information
        results = agent.search_kb(user_question, top_k=top_k)
        
        if not results:
            return "🤔 No relevant information found in internal knowledge base."
        
        # Format response based on result type
        if not use_llm:
            return format_simple_response(results)
        
        # Use LLM to generate comprehensive answer
        try:
            context = format_context_for_llm(results)
            
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that answers questions based on internal knowledge base documents. Provide clear, accurate answers based on the provided context."
                    },
                    {
                        "role": "user", 
                        "content": f"Context from knowledge base:\n{context}\n\nUser question: {user_question}\n\nProvide a comprehensive answer based on the context above."
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"⚠️ LLM failed: {str(e)}\n\n{format_simple_response(results)}"
            
    except Exception as e:
        return f"❌ Error processing question: {str(e)}"


def format_simple_response(results: List[Dict[str, Any]]) -> str:
    """Format results for simple response without LLM."""
    if not results:
        return "No results found."
    
    top_result = results[0]
    
    if top_result["type"] == "qa":
        return f"**Q:** {top_result['question']}\n**A:** {top_result['answer']}"
    elif top_result["type"] == "property":
        data = top_result["data"]
        response = "**Property Information:**\n"
        for key, value in data.items():
            if value and str(value).strip():
                response += f"- {key}: {value}\n"
        return response
    elif top_result["type"] == "master_clauses":
        data = top_result["data"]
        response = "**Contract Information:**\n"
        important_fields = [
            'Document Name', 'Parties', 'Agreement Date', 'Effective Date',
            'Expiration Date', 'Governing Law', 'Non-Compete', 'Exclusivity'
        ]
        for field in important_fields:
            if data.get(field):
                response += f"- {field}: {data[field]}\n"
        return response
    
    return "Unknown result type."


def format_context_for_llm(results: List[Dict[str, Any]]) -> str:
    """Format results as context for LLM."""
    context_parts = []
    
    for result in results:
        if result["type"] == "qa":
            context_parts.append(f"Q: {result['question']}\nA: {result['answer']}")
        elif result["type"] == "property":
            data = result["data"]
            prop_info = []
            for key, value in data.items():
                if value and str(value).strip():
                    prop_info.append(f"{key}: {value}")
            context_parts.append("Property Data:\n" + "\n".join(prop_info))
        elif result["type"] == "master_clauses":
            data = result["data"]
            clause_info = []
            for key, value in data.items():
                if value and str(value).strip():
                    clause_info.append(f"{key}: {value}")
            context_parts.append("Contract Data:\n" + "\n".join(clause_info))
    
    return "\n\n".join(context_parts)


def get_kb_stats(
    qa_csv_path: str = None,
    property_csv_path: str = None,
    master_clauses_csv_path: str = None
) -> Dict[str, Any]:
    """Get statistics about all knowledge bases."""
    try:
        agent = InternalKBAgent(qa_csv_path, property_csv_path, master_clauses_csv_path)
        
        qa_data = agent.load_qa_data()
        property_data = agent.load_property_data()
        clauses_data = agent.load_master_clauses_data()
        
        return {
            "qa_pairs": len(qa_data),
            "property_records": len(property_data),
            "clause_records": len(clauses_data),
            "vector_stores": {
                "qa": os.path.exists(QA_VECTOR_PATH),
                "property": os.path.exists(PROPERTY_VECTOR_PATH),
                "master_clauses": os.path.exists(MASTER_CLAUSES_VECTOR_PATH)
            }
        }
        
    except Exception as e:
        return {"error": str(e)}


def rebuild_all_vector_stores(
    qa_csv_path: str = None,
    property_csv_path: str = None,
    master_clauses_csv_path: str = None
) -> Dict[str, bool]:
    """Force rebuild of all vector stores."""
    agent = InternalKBAgent(qa_csv_path, property_csv_path, master_clauses_csv_path)
    
    results = {}
    
    for kb_type in ["qa", "property", "master_clauses"]:
        try:
            agent.build_vector_store(kb_type, force_rebuild=True)
            results[kb_type] = True
        except Exception as e:
            print(f"❌ Failed to rebuild {kb_type} vector store: {e}")
            results[kb_type] = False
    
    return results