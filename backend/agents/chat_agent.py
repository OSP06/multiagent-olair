# agents/chat_agent.py
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from utils.embedding_utils import get_embedding
from utils.retriever import LeaseVectorStore
from sqlalchemy.orm import Session
from crm.db import SessionLocal
from crm.crud import create_conversation

# Risk and Redline
from models.risk_detector import detect_risk
from models.redline_suggestor import suggest_redline

# Optional: Clause classification
try:
    from models.clause_classifier import load_model, clean_text
    classifier_model = load_model("models/clause_classifier.joblib")
except Exception:
    classifier_model = None

# OpenAI
try:
    from openai import OpenAI
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=openai_key) if openai_key else None
    USE_OPENAI = openai_client is not None
except ImportError:
    openai_client = None
    USE_OPENAI = False

# Vector store path
VECTOR_STORE_PATH = os.path.join("data", "lease_vector_store.pkl")

def load_vector_store(path: str = None) -> LeaseVectorStore:
    """
    Load the persistent vector store from disk.
    
    Args:
        path: Path to load from (optional)
        
    Returns:
        LeaseVectorStore instance
        
    Raises:
        FileNotFoundError: If vector store doesn't exist
        Exception: For loading errors
    """
    if path is None:
        path = VECTOR_STORE_PATH
    
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"❌ Vector store not found at: {path}\n"
            "💡 Run 'python scripts/populate_vector_store.py' first"
        )
    
    store = LeaseVectorStore()
    store.load(path)
    return store

def answer_lease_question(
    question: str, 
    user_id: int, 
    top_k: int = 3, 
    vector_store_path: str = None
) -> Dict[str, Any]:
    """
    Answer a lease-related question using the vector store and AI enrichment.
    
    Args:
        question: The user's question
        user_id: User ID for conversation logging
        top_k: Number of top clauses to retrieve
        vector_store_path: Path to vector store file (optional)
        
    Returns:
        Dictionary containing answer and enriched clause information
    """
    if not question.strip():
        return {"answer": "❌ Please provide a question."}

    try:
        # Load vector store from disk
        store = load_vector_store(vector_store_path)
        
        # Search for relevant clauses
        query_embedding = get_embedding(question)
        results = store.search(query_embedding, k=top_k)
        top_clauses = [r["text"] for r in results]

        if not top_clauses:
            return {"answer": "🤔 No relevant clauses found for your question."}

        # Generate answer using OpenAI
        if USE_OPENAI:
            try:
                context = "\n\n".join(top_clauses)
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a helpful legal assistant answering questions about lease agreements. Provide clear, concise answers based on the provided clauses."
                        },
                        {
                            "role": "user", 
                            "content": f"Based on the following lease clauses:\n\n{context}\n\nAnswer this question: {question}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=300,
                )
                final_answer = response.choices[0].message.content.strip()
            except Exception as e:
                final_answer = f"⚠️ LLM failed: {str(e)}"
        else:
            final_answer = (
                f"🤖 **Simulated Answer**:\n"
                f"**Q:** {question}\n"
                f"**A:** Based on the relevant clauses found, this appears to be related to lease terms. "
                f"Real response will work when OpenAI key is active."
            )

        # Risk, Redline, and Classification Enrichment
        enrichment = []
        for i, clause in enumerate(top_clauses):
            try:
                # Risk detection
                risk_flag, risk_msg = detect_risk(clause)
                
                # Redline suggestion
                redline_msg = suggest_redline(clause)
                
                # Clause classification
                clause_type = "N/A"
                if classifier_model:
                    try:
                        clause_type = classifier_model.predict([clean_text(clause)])[0]
                    except:
                        clause_type = "Unknown"
                
                # Relevance score from search results
                relevance_score = results[i].get("score", 0.0) if i < len(results) else 0.0
                
                enrichment.append({
                    "clause": clause,
                    "risk": risk_msg,
                    "redline": redline_msg,
                    "type": clause_type,
                    "relevance_score": relevance_score
                })
                
            except Exception as e:
                print(f"⚠️ Error enriching clause {i}: {e}")
                enrichment.append({
                    "clause": clause,
                    "risk": "Analysis failed",
                    "redline": "Analysis failed",
                    "type": "Unknown",
                    "relevance_score": 0.0
                })

        # Save to CRM conversation
        try:
            db: Session = SessionLocal()
            create_conversation(db, user_id=user_id, question=question, answer=final_answer)
            db.commit()
            db.close()
        except Exception as e:
            print(f"⚠️ Failed to log conversation: {e}")

        return {
            "answer": final_answer,
            "enriched_clauses": enrichment,
            "total_clauses_found": len(top_clauses)
        }
        
    except FileNotFoundError as e:
        return {"answer": str(e)}
    except Exception as e:
        return {"answer": f"❌ Error processing question: {str(e)}"}

def get_clause_analysis(clause: str) -> Dict[str, Any]:
    """
    Get detailed analysis of a single clause.
    
    Args:
        clause: The clause text to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Risk detection
        risk_flag, risk_msg = detect_risk(clause)
        
        # Redline suggestion
        redline_msg = suggest_redline(clause)
        
        # Clause classification
        clause_type = "N/A"
        if classifier_model:
            try:
                clause_type = classifier_model.predict([clean_text(clause)])[0]
            except:
                clause_type = "Unknown"
        
        return {
            "clause": clause,
            "risk_flag": risk_flag,
            "risk_analysis": risk_msg,
            "redline_suggestion": redline_msg,
            "clause_type": clause_type,
            "success": True
        }
        
    except Exception as e:
        return {
            "clause": clause,
            "error": str(e),
            "success": False
        }

def search_similar_clauses(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for clauses similar to the given query.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        List of similar clauses with relevance scores
    """
    try:
        store = load_vector_store()
        query_embedding = get_embedding(query)
        results = store.search(query_embedding, k=top_k)
        
        return [
            {
                "clause": result["text"],
                "relevance_score": result["score"],
                "analysis": get_clause_analysis(result["text"])
            }
            for result in results
        ]
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]