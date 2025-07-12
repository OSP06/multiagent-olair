from sqlalchemy.orm import Session
from crm.models import Conversation, User
from crm.schemas import UserUpdate
from crm.schemas import UserCreate
from typing import List, Optional

def create_conversation(db: Session, user_id: int, question: str, answer: str) -> Conversation:
    db_convo = Conversation(user_id=user_id, question=question, answer=answer)
    db.add(db_convo)
    db.commit()
    db.refresh(db_convo)
    return db_convo

def get_conversations_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
    return db.query(Conversation).filter(Conversation.user_id == user_id).offset(skip).limit(limit).all()

def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_all_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
    return db.query(Conversation).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(name=user.name, email=user.email, tags=user.tags)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, update_data: UserUpdate) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    if update_data.name is not None:
        user.name = update_data.name
    if update_data.email is not None:
        user.email = update_data.email
    if update_data.tags is not None:
        user.tags = update_data.tags

    db.commit()
    db.refresh(user)
    return user