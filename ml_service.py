# ml_service.py
import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

# Variables globales para los recursos de ML
modelo_st: SentenceTransformer = None
nn_model: NearestNeighbors = None
embeddings: np.ndarray = None
df_total: pd.DataFrame = None

def load_ml_resources():
    """Carga todos los recursos de Machine Learning en memoria"""
    global modelo_st, nn_model, embeddings, df_total

    embeddings_file = "embeddings.npy"
    dataset_file = "dataset_unificado.csv"

    if not os.path.exists(embeddings_file) or not os.path.exists(dataset_file):
        print("Error: Los archivos 'embeddings.npy' o 'dataset_unificado.csv' no se encontraron.")
        return False

    print("Cargando embeddings y dataset...")
    embeddings = np.load(embeddings_file)
    df_total = pd.read_csv(dataset_file)

    print("Cargando modelo SentenceTransformer...")
    modelo_st = SentenceTransformer('all-MiniLM-L6-v2')

    print("Inicializando y ajustando NearestNeighbors...")
    nn_model = NearestNeighbors(n_neighbors=3, metric='cosine')
    nn_model.fit(embeddings)
    print("Recursos ML cargados y listos.")
    return True

def generate_simulated_tutor_response(user_message_text: str) -> str:
    """Genera una respuesta basada en la similitud de embeddings."""
    if modelo_st is None or nn_model is None or embeddings is None or df_total is None:
        print("ADVERTENCIA: Los recursos ML no están cargados. Intentando cargar...")
        if not load_ml_resources():
            return "Error interno del servidor: Los recursos de IA no están disponibles."

    emb_pregunta = modelo_st.encode([user_message_text])
    distancias, indices = nn_model.kneighbors(emb_pregunta)
    mejor_idx = indices[0][0]
    resultado = df_total.iloc[mejor_idx]

    # Construir la respuesta asegurándose de que los componentes son strings
    descripcion_str = f"Descripción:\n\n{resultado['descripcion']}" if pd.notna(resultado['descripcion']) else ""
    ejemplo_uso_str = f"Ejemplo:\n\n{resultado['ejemplo_uso']}" if pd.notna(resultado['ejemplo_uso']) else ""
    url_str = f"Fuente:\n\n{resultado['url']}" if pd.notna(resultado['url']) else ""

    # Unir las partes con saltos de línea, filtrando las vacías
    respuesta_parts = [part for part in [descripcion_str, ejemplo_uso_str, url_str] if part]
    respuesta = "\n\n".join(respuesta_parts)
    
    return respuesta
