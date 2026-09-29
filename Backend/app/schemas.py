from pydantic import BaseModel, EmailStr, Field, ConfigDict, StringConstraints
from datetime import datetime
from typing import Annotated

class UserBase(BaseModel):
    email:Annotated[EmailStr,Field(max_length=254)]

class UserCreate(UserBase):
    password:Annotated[str,Field(min_length=8,max_length=128)]

class UserLogin(UserBase):
    password:Annotated[str,Field(min_length=8,max_length=128)]

class UserResponse(UserBase):
    id: int
    is_verified:bool
    is_active:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token:str
    token_type:str
    
class ConversationCreate(BaseModel):
    document_id:int

class MessageCreate(BaseModel):
    content:Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)
    ]
    
class ConversationResponse(BaseModel):
    id: int
    user_id: int
    document_id: int
    created_at: datetime
    model_config=ConfigDict(from_attributes=True)
    
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    model_config=ConfigDict(from_attributes=True)
    
class MessageSource(BaseModel):
    chunk_id: int
    page_number:int

class MessageExchangeResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: list[MessageSource]