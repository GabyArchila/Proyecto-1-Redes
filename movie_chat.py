import os
import requests
import json
import groq

GROQ_API_KEY = "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"
cliente_groq = groq.Groq(api_key=GROQ_API_KEY)
mensajes_historial = []


class MovieMCPClient:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url

    def call_tool(self, tool_name: str, arguments: dict):
        """Llamar a una herramienta del servidor MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            response = requests.post(
                f"{self.server_url}/mcp/jsonrpc",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}


class ArxivMCPClient:
    def __init__(self, server_url="http://localhost:8001"):
        self.server_url = server_url

    def call_tool(self, tool_name: str, arguments: dict):
        """Llamar a una herramienta del servidor arXiv MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            response = requests.post(
                f"{self.server_url}/mcp/jsonrpc",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def handle_movie_query(user_input: str, movie_client):
    """Manejar consultas sobre peliculas"""
    if 'buscar' in user_input.lower() or 'busca' in user_input.lower():
        title = user_input.lower().replace('buscar', '').replace('busca', '').strip()
        if title:
            print("Buscando informacion de pelicula...")
            result = movie_client.call_tool("search_movie", {"title": title})

            if 'result' in result and 'title' in result['result']:
                movie = result['result']
                print(f"\n{movie['title']} ({movie.get('release_date', 'N/A')})")
                print(f"Rating: {movie.get('rating', 'N/A')}/10")
                print(f"{movie.get('overview', 'Sin sinopsis')}")
                print(f"Plataformas: {', '.join(movie.get('streaming_platforms', ['No disponible']))}")

                if movie.get('similar_movies'):
                    print("Peliculas similares:")
                    for similar in movie['similar_movies']:
                        print(f"  - {similar['title']} ({similar.get('rating', 'N/A')}/10)")
                print()

            else:
                print("No pude encontrar informacion de esa pelicula")

    elif 'aleator' in user_input.lower():
        print("Buscando pelicula aleatoria...")
        result = movie_client.call_tool("get_random_movie", {})

        if 'result' in result and 'title' in result['result']:
            movie = result['result']
            print(f"\nPelicula aleatoria: {movie['title']}")
            print(f"Rating: {movie.get('rating', 'N/A')}/10")
            print(f"{movie.get('overview', 'Sin sinopsis')}\n")
        else:
            print("Error al obtener pelicula aleatoria")

    else:
        print("Procesando consulta sobre peliculas...")
        mensajes_historial.append({"role": "user", "content": user_input})
        chat_completion = cliente_groq.chat.completions.create(
            messages=mensajes_historial,
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        respuesta = chat_completion.choices[0].message.content
        mensajes_historial.append({"role": "assistant", "content": respuesta})
        print(f"{respuesta}")


def handle_arxiv_query(user_input: str, arxiv_client):
    """Manejar consultas sobre articulos academicos usando el servidor real"""
    print("Buscando en arXiv...")

    # Extraer numero de resultados si se especifica
    num_results = 5
    for word in ['cinco', 'five', 'tres', 'three', 'diez', 'ten']:
        if word in user_input.lower():
            if word in ['cinco', 'five']:
                num_results = 5
            elif word in ['tres', 'three']:
                num_results = 3
            elif word in ['diez', 'ten']:
                num_results = 10

    if 'nuevo' in user_input.lower() or 'nuevos' in user_input.lower() or 'reciente' in user_input.lower():
        # Buscar papers nuevos
        query = extract_arxiv_query(user_input)
        result = arxiv_client.call_tool("arxiv_search_arxiv", {
            "query": query,
            "sort_by": "date",
            "sort_order": "descending"
        })

        if 'result' in result and 'papers' in result['result']:
            papers = result['result']['papers'][:num_results]
            print(f"\nEncontrados {len(papers)} papers sobre {query}:")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.get('title', 'Sin titulo')}")
                print(f"   Autores: {', '.join(paper.get('authors', []))}")
                print(f"   ID: {paper.get('id', 'N/A')}")
                print(f"   Fecha: {paper.get('published', 'N/A')}")
                print(f"   Resumen: {paper.get('summary', 'Sin resumen')[:100]}...")
                print()
        else:
            print("No se pudieron obtener papers de arXiv")

    elif 'importante' in user_input.lower() or 'relevante' in user_input.lower():
        # Buscar papers importantes (por relevancia)
        query = extract_arxiv_query(user_input)
        result = arxiv_client.call_tool("arxiv_search_arxiv", {
            "query": query,
            "sort_by": "relevance",
            "sort_order": "descending"
        })

        if 'result' in result and 'papers' in result['result']:
            papers = result['result']['papers'][:num_results]
            print(f"\nPapers relevantes sobre {query}:")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.get('title', 'Sin titulo')}")
                print(f"   Autores: {', '.join(paper.get('authors', []))}")
                print(f"   ID: {paper.get('id', 'N/A')}")
                print()
        else:
            print("No se encontraron papers relevantes")

    elif 'descargar' in user_input.lower() or 'download' in user_input.lower():
        # Descargar paper especifico
        paper_id = extract_paper_id(user_input)
        if paper_id:
            result = arxiv_client.call_tool("arxiv_download_paper_arxiv", {
                "id": paper_id,
                "filename": f"paper_{paper_id}.pdf"
            })

            if 'result' in result and 'success' in result['result']:
                print(f"Paper {paper_id} descargado exitosamente")

                # Generar BibTeX
                bib_result = arxiv_client.call_tool("arxiv_generate_bibtex", {
                    "title": extract_paper_title(user_input)
                })

                if 'result' in bib_result and 'bibtex' in bib_result['result']:
                    print("BibTeX generado:")
                    print(bib_result['result']['bibtex'])
            else:
                print("Error al descargar el paper")
        else:
            print("Por favor especifica el ID del paper a descargar")

    else:
        # Busqueda general
        query = extract_arxiv_query(user_input)
        if query:
            result = arxiv_client.call_tool("arxiv_search_arxiv", {
                "query": query,
                "sort_by": "relevance",
                "sort_order": "descending"
            })

            if 'result' in result and 'papers' in result['result']:
                papers = result['result']['papers'][:3]
                print(f"\nResultados para '{query}':")
                for i, paper in enumerate(papers, 1):
                    print(f"{i}. {paper.get('title', 'Sin titulo')}")
                    print(f"   Autores: {', '.join(paper.get('authors', []))}")
                    print(f"   ID: {paper.get('id', 'N/A')}")
                    print(f"   Resumen: {paper.get('summary', 'Sin resumen')[:100]}...")
                    print()
            else:
                print("No se encontraron articulos")
        else:
            print("Por favor especifica que quieres buscar en arXiv")


def extract_arxiv_query(user_input):
    """Extraer terminos de busqueda para arXiv"""
    stop_words = ['buscar', 'busca', 'encontrar', 'encuentra', 'arxiv', 'papers',
                  'articulos', 'articulo', 'paper', 'sobre', 'de', 'acerca']

    query = user_input.lower()
    for word in stop_words:
        query = query.replace(word, '')

    # Remover numeros si son para cantidad
    query = ' '.join([word for word in query.split() if not word.isdigit()])

    return query.strip() or "computer science"


def extract_paper_id(user_input):
    """Extraer ID de paper para descargar"""
    words = user_input.split()
    for i, word in enumerate(words):
        if word.lower() in ['paper', 'articulo', 'numero', 'number'] and i + 1 < len(words):
            return words[i + 1]

    # Buscar patrones de ID de arXiv
    import re
    arxiv_pattern = r'\d+\.\d+(v\d+)?'
    matches = re.findall(arxiv_pattern, user_input)
    if matches:
        return matches[0]

    return None


def extract_paper_title(user_input):
    """Extraer titulo de paper para BibTeX"""
    # Esto es basico, podria mejorarse
    if 'paper' in user_input.lower():
        parts = user_input.lower().split('paper')
        if len(parts) > 1:
            return parts[1].strip()
    return "Paper de arXiv"


def handle_general_query(user_input: str):
    """Manejar consultas generales"""
    print("Pensando...")
    mensajes_historial.append({"role": "user", "content": user_input})
    chat_completion = cliente_groq.chat.completions.create(
        messages=mensajes_historial,
        model="llama-3.1-8b-instant",
        temperature=0.7,
    )
    respuesta = chat_completion.choices[0].message.content
    mensajes_historial.append({"role": "assistant", "content": respuesta})
    print(f"{respuesta}")


def chat_con_multi_bot():
    """Chat interactivo con integracion MCP multiple"""
    movie_client = MovieMCPClient("http://localhost:8000")
    arxiv_client = ArxivMCPClient("http://localhost:8001")

    print("Bienvenido al Chatbot Multi-MCP")
    print("Puedo ayudarte con:")
    print("  • Peliculas: 'buscar inception', 'pelicula aleatoria'")
    print("  • Articulos academicos: 'buscar papers sobre IA', 'cinco papers nuevos de fisica'")
    print("  • Descargas: 'descargar paper 1701.08184v1'")
    print("  • Conversacion general")
    print("Escribe 'salir' para terminar la sesion\n")

    while True:
        user_input = input("Tu: ").strip()

        if user_input.lower() in ['salir', 'exit', 'quit']:
            break

        # Detectar tipo de consulta
        movie_keywords = ['pelicula', 'película', 'movie', 'cine', 'netflix', 'disney']

        arxiv_keywords = ['arxiv', 'paper', 'papers', 'articulo', 'articulos', 'investigacion',
                          'academico', 'cientifico', 'descargar', 'download', 'bibtex']

        if any(keyword in user_input.lower() for keyword in movie_keywords):
            handle_movie_query(user_input, movie_client)

        elif any(keyword in user_input.lower() for keyword in arxiv_keywords):
            handle_arxiv_query(user_input, arxiv_client)

        else:
            handle_general_query(user_input)


if __name__ == "__main__":
    chat_con_multi_bot()