# api/routes/crm.py
import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from crm import crud, schemas, db, models

router = APIRouter()

# Dependency
def get_db():
    db_instance = db.SessionLocal()
    try:
        yield db_instance
    finally:
        db_instance.close()

# -------------------- USERS --------------------

@router.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@router.get("/users", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted"}

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# ---------------- CONVERSATIONS ----------------

class ConversationCreate(schemas.BaseModel):
    user_id: int
    question: str
    answer: str

@router.post("/conversations", response_model=schemas.ConversationOut)
def create_conversation(convo: ConversationCreate, db: Session = Depends(get_db)):
    return crud.create_conversation(db=db, user_id=convo.user_id, question=convo.question, answer=convo.answer)

@router.get("/conversations", response_model=List[schemas.ConversationOut])
def get_all_conversations(db: Session = Depends(get_db)):
    raw_convos = crud.get_all_conversations(db)
    enriched_convos = []
    for convo in raw_convos:
        preview = convo.question[:100] + "..." if convo.question else "No preview"
        enriched_convos.append({
            "id": convo.id,
            "user_id": convo.user_id,
            "question": convo.question,
            "answer": convo.answer,
            "created_at": convo.created_at,
            "preview": preview
        })
    return enriched_convos


@router.get("/users/{user_id}/conversations", response_model=List[schemas.ConversationOut])
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    raw_convos = crud.get_conversations_by_user(db, user_id)
    enriched_convos = []
    for convo in raw_convos:
        preview = convo.question[:100] + "..." if convo.question else "No preview"
        enriched_convos.append({
            "id": convo.id,
            "user_id": convo.user_id,
            "question": convo.question,
            "answer": convo.answer,
            "created_at": convo.created_at,
            "preview": preview
        })
    return enriched_convos


@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    convo = crud.get_conversation_by_id(db, conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(convo)
    db.commit()
    return {"message": f"Conversation {conversation_id} deleted"}

@router.post("/reset/{user_id}")
def reset_user_conversations(user_id: int, db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).filter(models.Conversation.user_id == user_id).all()
    if not conversations:
        return {"message": f"No conversations found for user {user_id}"}
    for convo in conversations:
        db.delete(convo)
    db.commit()
    return {"message": f"✅ All conversations deleted for user {user_id}"}

# ---------------- LEASE CSV (Utility) ----------------

import pandas as pd

@router.get("/leases")
def get_lease_data(type: str = "property"):
    """
    type: 'property', 'master_clauses', or 'qa'
    """
    paths = {
        "property": "data/HackathonInternalKnowledgeBase.csv",
        "master_clauses": "data/master_clauses.csv",
        "qa": "data/qa_internal_kb.csv"
    }

    csv_path = paths.get(type)
    if not csv_path or not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail=f"No file found for type '{type}'")
    
    try:
        df = pd.read_csv(csv_path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))