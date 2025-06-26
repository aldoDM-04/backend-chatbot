from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

# Importar módulos del proyecto
import models, schemas, crud, auth, dependencies, ml_service
from database import engine, get_db

# Crear todas las tablas en la base de datos (si no existen)
# En una aplicación de producción, podrías usar Alembic para migraciones.
models.Base.metadata.create_all(bind=engine)

# Evento de ciclo de vida para cargar modelos de ML al iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar recursos
    print("Iniciando aplicación y cargando recursos de ML...")
    ml_service.load_ml_resources()
    yield
    # Limpiar recursos si es necesario al apagar
    print("Apagando la aplicación.")

app = FastAPI(
    title="DevHelper API",
    description="API para el tutor inteligente DevHelper con autenticación y base de datos.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Configuración de CORS ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://aldodm-04.github.io/DevHelper/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Incluir routers ---
app.include_router(auth.router)

# --- Dependencia de usuario actual ---
CurrentUserDep = Depends(dependencies.get_current_active_user)

# --- Endpoints ---

@app.get("/", tags=["General"])
async def read_root():
    return {"message": "Bienvenido a la API de DevHelper v1.0"}

# --- Endpoints de Chats ---
@app.get("/api/chats", response_model=List[schemas.Chat], tags=["Chats"])
async def get_all_user_chats(db: Session = Depends(get_db), current_user: models.User = CurrentUserDep):
    """
    Obtiene todos los chats para el usuario autenticado, ordenados por última actualización.
    """
    chats = crud.get_chats_by_user(db=db, user_id=current_user.id)
    return chats

@app.post("/api/chats", response_model=schemas.Chat, status_code=201, tags=["Chats"])
async def create_chat_endpoint(
    request_body: schemas.ChatCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = CurrentUserDep
):
    """
    Crea un nuevo chat para el usuario.
    Si se provee `first_message_text`, se añade como primer mensaje
    y el sistema genera una respuesta del tutor.
    """
    first_message = request_body.first_message_text
    title = "Nuevo Chat"
    if first_message and first_message.strip():
        title = first_message[:60] + ("..." if len(first_message) > 60 else "")

    new_chat = crud.create_chat(db=db, user_id=current_user.id, title=title)

    if first_message and first_message.strip():
        # Añadir mensaje de usuario y respuesta de tutor
        crud.create_message(db=db, chat_id=new_chat.id, text=first_message, sender="user")
        tutor_response = ml_service.generate_simulated_tutor_response(first_message)
        crud.create_message(db=db, chat_id=new_chat.id, text=tutor_response, sender="tutor")
        # Refrescar el chat para obtener los mensajes añadidos
        db.refresh(new_chat)
    
    return new_chat

@app.get("/api/chats/{chat_id}", response_model=schemas.Chat, tags=["Chats"])
async def get_chat_messages_endpoint(chat_id: str, db: Session = Depends(get_db), current_user: models.User = CurrentUserDep):
    """
    Obtiene un chat específico incluyendo todos sus mensajes.
    """
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id, user_id=current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado o no pertenece al usuario.")
    return chat

# --- Endpoint de Mensajes ---
@app.post("/api/chats/{chat_id}/messages", response_model=schemas.Chat, tags=["Messages"])
async def send_message_to_chat_endpoint(
    chat_id: str,
    message_data: schemas.MessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = CurrentUserDep
):
    """
    Envía un mensaje a un chat y obtiene una respuesta del tutor.
    Devuelve el chat actualizado.
    """
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id, user_id=current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat no encontrado o no pertenece al usuario.")

    if not message_data.text or not message_data.text.strip():
        raise HTTPException(status_code=400, detail="El texto del mensaje no puede estar vacío.")

    # Añadir mensaje del usuario
    crud.create_message(db=db, chat_id=chat.id, text=message_data.text, sender="user")
    
    # Generar y añadir respuesta del tutor
    tutor_response = ml_service.generate_simulated_tutor_response(message_data.text)
    crud.create_message(db=db, chat_id=chat.id, text=tutor_response, sender="tutor")

    # Devolver el chat completo y actualizado
    db.refresh(chat)
    return chat
