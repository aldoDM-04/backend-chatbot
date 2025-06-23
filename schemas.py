# schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import datetime
import uuid

# --- Esquemas para Mensajes ---
class MessageBase(BaseModel):
    sender: str
    text: str

class Message(MessageBase):
    id: uuid.UUID
    chat_id: uuid.UUID
    timestamp: datetime.datetime

    class Config:
        from_attributes = True # Anteriormente orm_mode

class MessageCreateRequest(BaseModel):
    text: str

# --- Esquemas para Chats ---
class ChatBase(BaseModel):
    title: str

class Chat(ChatBase):
    id: uuid.UUID
    user_id: uuid.UUID = Field(..., alias='owner_id') # Mapea owner_id a user_id en la respuesta
    messages: List[Message] = []
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
        populate_by_name = True # Permite usar el alias

class ChatCreateRequest(BaseModel):
    first_message_text: Optional[str] = None

# --- Esquemas para Usuarios y Autenticación ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
