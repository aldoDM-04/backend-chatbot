# crud.py
from sqlalchemy.orm import Session
from uuid import UUID
import models, schemas, auth
import datetime

# --- Funciones CRUD para Usuarios ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Funciones CRUD para Chats y Mensajes ---

def get_chats_by_user(db: Session, user_id: UUID):
    return db.query(models.Chat).filter(models.Chat.owner_id == user_id).order_by(models.Chat.updated_at.desc()).all()

def get_chat_by_id(db: Session, chat_id: UUID, user_id: UUID):
    return db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.owner_id == user_id).first()

def create_chat(db: Session, user_id: UUID, title: str):
    new_chat = models.Chat(owner_id=user_id, title=title)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

def create_message(db: Session, chat_id: UUID, text: str, sender: str):
    message = models.Message(chat_id=chat_id, text=text, sender=sender)
    db.add(message)
    
    # Actualizar el timestamp del chat asociado
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if chat:
        chat.updated_at = datetime.datetime.now(datetime.UTC)

    db.commit()
    db.refresh(message)
    return message
