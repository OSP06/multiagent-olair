# api/routes/chat.py
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Import agents
from agents.chat_agent import answer_lease_question, get_clause_analysis, search_similar_clauses
from agents.internal_kb_agent import answer_internal_question, get_kb_stats, rebuild_all_vector_stores

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    user_id: int
    source: str = "auto"  # "auto", "internal", "lease", "property", "master_clauses", "qa"
    top_k: int = 3

class ChatResponse(BaseModel):
    answer: str
    source: str
    kb_type: Optional[str] = None  # Which specific KB was used
    enriched_clauses: Optional[list] = None
    total_clauses_found: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ClauseAnalysisRequest(BaseModel):
    clause: str

class SimilarClausesRequest(BaseModel):
    query: str
    top_k: int = 5

class InternalKBRequest(BaseModel):
    question: str
    kb_type: Optional[str] = None  # "qa", "property", "master_clauses", or None for auto
    top_k: int = 3
    use_llm: bool = True

@router.post("/", response_model=ChatResponse)
async def chat_router(request: ChatRequest):
    """
    Main chat endpoint that routes questions to appropriate agents.
    
    Args:
        request: Chat request with question, user_id, source, and top_k
        
    Returns:
        ChatResponse with answer and optional enrichment data
    """
    try:
        logger.info(f"Processing chat request: source={request.source}, user_id={request.user_id}")
        
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Handle different source types
        if request.source in ["internal", "auto", "qa", "property", "master_clauses"]:
            # Route to internal knowledge base agent
            kb_type = None if request.source in ["internal", "auto"] else request.source
            
            answer = answer_internal_question(
                user_question=request.question,
                top_k=request.top_k,
                kb_type=kb_type
            )
            
            # Try to determine which KB was actually used
            detected_kb = "unknown"
            if "Property Information:" in answer:
                detected_kb = "property"
            elif "Contract Information:" in answer:
                detected_kb = "master_clauses"
            elif "**Q:**" in answer and "**A:**" in answer:
                detected_kb = "qa"
            
            return ChatResponse(
                answer=answer,
                source="internal",
                kb_type=detected_kb,
                success=True,
                metadata={
                    "requested_kb": kb_type,
                    "detected_kb": detected_kb,
                    "top_k": request.top_k
                }
            )
            
        elif request.source == "lease":
            # Route to lease vector store agent
            result = answer_lease_question(
                question=request.question,
                user_id=request.user_id,
                top_k=request.top_k
            )
            
            return ChatResponse(
                answer=result["answer"],
                source="lease",
                kb_type="lease_clauses",
                enriched_clauses=result.get("enriched_clauses"),
                total_clauses_found=result.get("total_clauses_found"),
                success=True,
                metadata={
                    "user_id": request.user_id,
                    "top_k": request.top_k
                }
            )
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid source: {request.source}. Must be 'auto', 'internal', 'qa', 'property', 'master_clauses', or 'lease'"
            )
            
    except Exception as e:
        logger.error(f"Chat router error: {str(e)}")
        return ChatResponse(
            answer=f"❌ Error processing request: {str(e)}",
            source=request.source,
            success=False,
            error=str(e)
        )

@router.post("/internal", response_model=ChatResponse)
async def chat_internal_enhanced(request: InternalKBRequest):
    """
    Enhanced internal knowledge base endpoint with support for specific KB types.
    
    Args:
        request: Internal KB request with question, kb_type, top_k, and use_llm
        
    Returns:
        ChatResponse with answer from specified or auto-detected KB
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        answer = answer_internal_question(
            user_question=request.question,
            top_k=request.top_k,
            kb_type=request.kb_type,
            use_llm=request.use_llm
        )
        
        # Determine which KB was used
        detected_kb = "unknown"
        if "Property Information:" in answer:
            detected_kb = "property"
        elif "Contract Information:" in answer:
            detected_kb = "master_clauses"
        elif "**Q:**" in answer and "**A:**" in answer:
            detected_kb = "qa"
        
        return ChatResponse(
            answer=answer,
            source="internal",
            kb_type=detected_kb,
            success=True,
            metadata={
                "requested_kb": request.kb_type,
                "detected_kb": detected_kb,
                "top_k": request.top_k,
                "use_llm": request.use_llm
            }
        )
        
    except Exception as e:
        logger.error(f"Internal chat enhanced error: {str(e)}")
        return ChatResponse(
            answer=f"❌ Error: {str(e)}",
            source="internal",
            success=False,
            error=str(e)
        )

@router.post("/analyze-clause")
async def analyze_clause(request: ClauseAnalysisRequest):
    """
    Analyze a single clause for risk, redlines, and classification.
    
    Args:
        request: Clause analysis request
        
    Returns:
        Detailed analysis of the clause
    """
    try:
        if not request.clause.strip():
            raise HTTPException(status_code=400, detail="Clause cannot be empty")
        
        analysis = get_clause_analysis(request.clause)
        return {
            "clause": request.clause,
            "analysis": analysis,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Clause analysis error: {str(e)}")
        return {
            "clause": request.clause,
            "analysis": None,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

@router.post("/search-similar-clauses")
async def search_clauses(request: SimilarClausesRequest):
    """
    Search for clauses similar to the given query.
    
    Args:
        request: Similar clauses search request
        
    Returns:
        List of similar clauses with analysis
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = search_similar_clauses(request.query, request.top_k)
        return {
            "query": request.query,
            "results": results,
            "total_found": len(results),
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Similar clauses search error: {str(e)}")
        return {
            "query": request.query,
            "results": [],
            "total_found": 0,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/kb-stats")
async def get_knowledge_base_stats():
    """
    Get comprehensive statistics about all knowledge bases.
    
    Returns:
        KB statistics including all knowledge bases and vector store status
    """
    try:
        stats = get_kb_stats()
        return {
            "knowledge_bases": {
                "internal": stats,
                "lease": "Available"  # You might want to get actual lease KB stats
            },
            "summary": {
                "total_qa_pairs": stats.get("qa_pairs", 0),
                "total_property_records": stats.get("property_records", 0),
                "total_clause_records": stats.get("clause_records", 0),
                "vector_stores_active": sum(1 for v in stats.get("vector_stores", {}).values() if v)
            },
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"KB stats error: {str(e)}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

@router.post("/kb-rebuild")
async def rebuild_knowledge_bases():
    """
    Force rebuild of all internal knowledge base vector stores.
    
    Returns:
        Status of rebuild operation for each KB
    """
    try:
        logger.info("Starting knowledge base rebuild...")
        
        results = rebuild_all_vector_stores()
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return {
            "rebuild_results": results,
            "summary": {
                "successful": success_count,
                "total": total_count,
                "success_rate": f"{success_count}/{total_count}"
            },
            "success": success_count > 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"KB rebuild error: {str(e)}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

@router.post("/internal/legacy")
async def chat_internal_legacy(
    question: str = Query(..., description="Question to ask"),
    top_k: int = Query(3, description="Number of top results to consider"),
    use_llm: bool = Query(True, description="Whether to use LLM for answer generation")
):
    """
    Legacy endpoint for internal knowledge base queries (backward compatibility).
    
    Args:
        question: User question
        top_k: Number of top matches to consider
        use_llm: Whether to use LLM for answer generation
        
    Returns:
        Answer from internal knowledge base
    """
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        answer = answer_internal_question(
            user_question=question,
            top_k=top_k,
            use_llm=use_llm
        )
        
        return {
            "question": question,
            "answer": answer,
            "source": "internal",
            "parameters": {
                "top_k": top_k,
                "use_llm": use_llm
            },
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Internal chat legacy error: {str(e)}")
        return {
            "question": question,
            "answer": f"❌ Error: {str(e)}",
            "source": "internal",
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/lease")
async def chat_lease_only(
    question: str = Query(..., description="Question to ask"),
    user_id: int = Query(..., description="User ID for conversation logging"),
    top_k: int = Query(3, description="Number of top clauses to retrieve")
):
    """
    Direct endpoint for lease-related queries.
    
    Args:
        question: User question
        user_id: User ID for logging
        top_k: Number of top clauses to retrieve
        
    Returns:
        Answer with lease clause analysis
    """
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        result = answer_lease_question(
            question=question,
            user_id=user_id,
            top_k=top_k
        )
        
        return {
            "question": question,
            "result": result,
            "source": "lease",
            "parameters": {
                "user_id": user_id,
                "top_k": top_k
            },
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Lease chat error: {str(e)}")
        return {
            "question": question,
            "result": {
                "answer": f"❌ Error: {str(e)}",
                "enriched_clauses": [],
                "total_clauses_found": 0
            },
            "source": "lease",
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify all agents are working.
    
    Returns:
        Status of all knowledge bases and agents
    """
    try:
        # Test internal KB agent with different KB types
        health_status = {
            "internal_kb": {},
            "lease_agent": "unknown",
            "overall_status": "unknown"
        }
        
        # Test each internal KB type
        for kb_type in ["qa", "property", "master_clauses"]:
            try:
                test_result = answer_internal_question(
                    "test", 
                    top_k=1, 
                    kb_type=kb_type,
                    use_llm=False
                )
                health_status["internal_kb"][kb_type] = "ok" if not test_result.startswith("❌") else "error"
            except Exception as e:
                health_status["internal_kb"][kb_type] = f"error: {str(e)}"
        
        # Test lease agent
        try:
            lease_test = answer_lease_question("test", user_id=0, top_k=1)
            health_status["lease_agent"] = "ok" if not lease_test["answer"].startswith("❌") else "error"
        except Exception as e:
            health_status["lease_agent"] = f"error: {str(e)}"
        
        # Determine overall status
        internal_ok = all(status == "ok" for status in health_status["internal_kb"].values())
        lease_ok = health_status["lease_agent"] == "ok"
        
        if internal_ok and lease_ok:
            health_status["overall_status"] = "healthy"
        elif internal_ok or lease_ok:
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "error"
        
        return {
            "status": health_status["overall_status"],
            "agents": health_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/sources")
async def get_available_sources():
    """
    Get list of available chat sources and knowledge bases.
    
    Returns:
        List of available sources with descriptions
    """
    return {
        "sources": [
            {
                "id": "auto",
                "name": "Auto-detect",
                "description": "Automatically determine the best knowledge base to use"
            },
            {
                "id": "internal",
                "name": "Internal Knowledge Base (All)",
                "description": "Search across all internal knowledge bases"
            },
            {
                "id": "qa",
                "name": "Q&A Knowledge Base",
                "description": "Internal FAQ and question-answer pairs"
            },
            {
                "id": "property",
                "name": "Property Database",
                "description": "Real estate property information, rent, brokers"
            },
            {
                "id": "master_clauses",
                "name": "Contract Clauses",
                "description": "Legal contract terms and clause analysis"
            },
            {
                "id": "lease",
                "name": "Lease Analysis",
                "description": "AI-powered analysis of lease clauses with risk assessment"
            }
        ],
        "default_source": "auto",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/kb-types")
async def get_knowledge_base_types():
    """
    Get detailed information about each knowledge base type.
    
    Returns:
        Detailed information about each KB type
    """
    try:
        stats = get_kb_stats()
        
        return {
            "knowledge_bases": {
                "qa": {
                    "name": "Q&A Knowledge Base",
                    "description": "Question and answer pairs for internal FAQ",
                    "record_count": stats.get("qa_pairs", 0),
                    "vector_store_ready": stats.get("vector_stores", {}).get("qa", False),
                    "sample_fields": ["question", "answer"]
                },
                "property": {
                    "name": "Property Database",
                    "description": "Real estate property information",
                    "record_count": stats.get("property_records", 0),
                    "vector_store_ready": stats.get("vector_stores", {}).get("property", False),
                    "sample_fields": ["Property Address", "Floor", "Suite", "Size (SF)", "Rent/SF/Year", "Associate 1", "BROKER Email ID"]
                },
                "master_clauses": {
                    "name": "Contract Clauses",
                    "description": "Legal contract terms and clause analysis",
                    "record_count": stats.get("clause_records", 0),
                    "vector_store_ready": stats.get("vector_stores", {}).get("master_clauses", False),
                    "sample_fields": ["Document Name", "Parties", "Agreement Date", "Governing Law", "Non-Compete", "Exclusivity"]
                }
            },
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"KB types error: {str(e)}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

# Utility endpoint for testing specific KB types
@router.get("/test-kb/{kb_type}")
async def test_knowledge_base(kb_type: str):
    """
    Test a specific knowledge base type.
    
    Args:
        kb_type: Type of KB to test ("qa", "property", "master_clauses")
        
    Returns:
        Test results for the specified KB
    """
    try:
        if kb_type not in ["qa", "property", "master_clauses"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid KB type: {kb_type}. Must be 'qa', 'property', or 'master_clauses'"
            )
        
        test_questions = {
            "qa": "How do I submit a request?",
            "property": "What properties are available?",
            "master_clauses": "What are the termination clauses?"
        }
        
        test_question = test_questions[kb_type]
        
        answer = answer_internal_question(
            user_question=test_question,
            top_k=2,
            kb_type=kb_type,
            use_llm=False
        )
        
        return {
            "kb_type": kb_type,
            "test_question": test_question,
            "answer": answer,
            "success": not answer.startswith("❌"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"KB test error: {str(e)}")
        return {
            "kb_type": kb_type,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }