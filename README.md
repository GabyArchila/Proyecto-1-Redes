# MCP para Búsqueda de Películas

## Componentes del proyecto

- **`main.py`**: Servidor MCP local (FastAPI) que se conecta a TMDB para obtener datos de películas.
- **`movie_chat.py`**: Código que interactúa con el usuario y llama al servidor MCP cuando se detectan consultas sobre películas.
- **`F_general.py`**: Caso base de chat con Groq (sin MCP).
- **`requirements.txt`**: Dependencias.

## Requisitos

- Python 3.8+
- Cuenta en [TMDB](https://www.themoviedb.org/) (para la API key)
- Cuenta en [Groq](https://groq.com/) (para la API key)

## Instalación y ejecución

### 1. Clonar o descargar los archivos
```bash
git clone <tu-repositorio>
cd <carpeta-del-proyecto>
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar el servidor MCP
```bash
python main.py
```
El servidor estará en `http://localhost:8000`

### 5. Ejecutar el chatbot (en otra terminal)
```bash
python movie_chat.py
```

## Uso

- Escribe preguntas normales para hablar con el LLM.
- Usa palabras como *"película"*, *"buscar"*, *"recomendar"*, *"aleatoria"* para activar las herramientas MCP.

##  Estructura MCP implementada

- **Servidor MCP local**: Ofrece 3 herramientas:
  - `search_movie(title)`
  - `get_random_movie()`
  - `get_movie_recommendations(genres, min_rating)`

- **Cliente MCP**: Integrado en `movie_chat.py`, detecta palabras clave y llama al servidor.

## Recursos utilizados

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [JSON-RPC](https://www.jsonrpc.org/)
- [TMDB API](https://www.themoviedb.org/documentation/api)
- [Groq API](https://groq.com/)
