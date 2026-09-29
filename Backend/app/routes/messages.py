from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.models import Message, User, Conversation
from app.schemas import MessageCreate, MessageResponse, MessageExchangeResponse
from app.auth import get_current_user

from app.services.embedding_service import generate_embeddings, EmbeddingServiceError
from app.services.retrieval_service import retrieve_chunks 
from app.services.llm_service import generate_answer,  LLMServiceError
from app.services.prompt_service import build_rag_prompt

from sqlalchemy.orm import Session

router=APIRouter()

@router.post("/{conversation_id}/messages/",response_model=MessageExchangeResponse)
def create_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation=db.query(Conversation).filter(
        Conversation.id==conversation_id,
        Conversation.user_id==current_user.id
        ).first()
    
    if not conversation:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Conversation not found"
        )
        
    try:
        query_embedding=generate_embeddings([data.content])[0]
    except EmbeddingServiceError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embedding service unavailable"
        )
    
    chunks=retrieve_chunks(
        document_id=conversation.document_id,
        db=db,
        query_embedding=query_embedding,
        top_k=5
        )
    if not chunks:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No document content available for this conversation"
        )
    
    conversation_history=db.query(Message).filter(
        Message.conversation_id==conversation.id
        ).order_by(Message.created_at.desc()
                   ).limit(10).all()
    conversation_history.reverse()
    
    prompt = build_rag_prompt(
        question=data.content,
        chunks=chunks,
        conversation_history=conversation_history
        )
    
    try:
        answer=generate_answer(prompt)
    except LLMServiceError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service unavailable"
        )
       
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=data.content
    )
    
    assistant_message=Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )
    
    sources=[
        {
            "chunk_id":chunk.id,
            "page_number":chunk.page_number
        }
        for chunk in chunks
    ]
    try:
        db.add(user_message)
        db.add(assistant_message)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(user_message)
    db.refresh(assistant_message)
    return {
        "user_message":user_message,
        "assistant_message":assistant_message,
        "sources":sources
    }
    
@router.get("/{conversation_id}/messages/", response_model=list[MessageResponse])
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.id.asc()).all()

    return messages