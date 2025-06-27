#!/bin/bash

# Activar el entorno virtual creado por Oryx
source /home/site/wwwroot/antenv/bin/activate

# Iniciar la aplicación Uvicorn
uvicorn main:app --host 0.0.0.0 --port $PORT