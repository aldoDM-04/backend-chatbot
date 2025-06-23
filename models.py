# models.py
import datetime
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func  # <--- Importa func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    chats = relationship("Chat", back_populates="owner", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # --- CORRECCIÓN ---
    # Usamos func.now() para que la base de datos genere la hora.
    # Es la forma más robusta.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.timestamp")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String, nullable=False)
    sender = Column(String, nullable=False) # 'user' o 'tutor'
    
    # --- CORRECCIÓN ---
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)

    chat = relationship("Chat", back_populates="messages")
