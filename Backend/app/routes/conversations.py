from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import ConversationCreate,ConversationResponse
from app.database import get_db
from app.models import User, Document, Conversation
from app.auth import get_current_user
from sqlalchemy.orm import Session

router=APIRouter()

@router.post("/",response_model=ConversationResponse)
def create_conversation(
    data:ConversationCreate,
    db: Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    document=db.query(Document).filter(
        Document.id==data.document_id,
        Document.user_id==current_user.id
        ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    conversation=Conversation(
        user_id=current_user.id,
        document_id=data.document_id
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

@router.get("/", response_model=list[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()

    return conversations