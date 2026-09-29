from sqlalchemy import Integer, Boolean,String,DateTime,Column, ForeignKey, CheckConstraint
from app.database import Base
from datetime import datetime
from pgvector.sqlalchemy import Vector

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String, unique=True,index=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)
    created_at=Column(DateTime, default=datetime.now, nullable=False)
    updated_at=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_verified=Column(Boolean, default=False, nullable=False)
    
class Document(Base):
    __tablename__="documents"
    id=Column(Integer,primary_key=True, index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    filename=Column(String,nullable=False)
    file_path=Column(String,nullable=False)
    created_at=Column(DateTime,nullable=False,default=datetime.now)
    
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_messages_role"
            ),
        )
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column( DateTime, nullable=False, default=datetime.now)