# Diabetes Analysis

Este proyecto tiene como objetivo analizar datos relacionados con la diabetes utilizando **Metabase** para visualizar los datos y **PostgresSQL** para almacenarlos.

## Pre-requisitos

- Docker y Docker Compose instalados en tu máquina.
- Python 3.x

## Levantar el proyecto

1. Clona este repositorio:
   ```bash
   git clone https://github.com/William10101995/diabetes-analysis.git
   cd diabetes-analysis
   ```
2. Construye y levanta los contenedores de Docker:
   ```bash
   docker compose up -d --build
   ```
3. Accede a Metabase en tu navegador web:
   ```
   http://localhost:3000
   ```
4. Configura Metabase para conectarse a la base de datos PostgreSQL utilizando las siguientes credenciales:
   - Host: `db`
   - Puerto: `5432`
   - Nombre de la base de datos: `diabetes_db`
   - Usuario: `admin`
   - Contraseña: `admin123`

## Exploración y limpieza de datos desde los notebooks (opcional)

Si deseas explorar y limpiar los datos antes de cargarlos en la base de datos, puedes utilizar los notebooks ubicados en la carpeta `notebooks`.

1. Dentro del repositorio clonado crea un entorno virtual de python y activalo
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar Jupyter Lab sin navegador interno a fin de evitar problemas en entornos linux:
   ```bash
   jupyter lab --no-browser
   ```
4. Abre tu navegador web y navega a `http://localhost:8888`
5. Abre los notebooks en la carpeta `notebooks` para explorar y limpiar los datos.
