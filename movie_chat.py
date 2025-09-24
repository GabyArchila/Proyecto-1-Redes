import os
import requests
import json
import groq
import re

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


class RemoteUnitConverterClient:

    def __init__(self, server_url="https://unit-converter-mcp-304357449334.us-central1.run.app"):
        self.server_url = server_url

    def call_tool(self, tool_name: str, arguments: dict):
        """Llamar a la herramienta remota de conversión de unidades"""
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
    """Manejar consultas sobre películas"""
    if 'buscar' in user_input.lower() or 'busca' in user_input.lower():
        title = user_input.lower().replace('buscar', '').replace('busca', '').strip()
        if title:
            print("Buscando información de película...")
            result = movie_client.call_tool("search_movie", {"title": title})

            if 'result' in result and 'title' in result['result']:
                movie = result['result']
                print(f"\n{movie['title']} ({movie.get('release_date', 'N/A')})")
                print(f"Rating: {movie.get('rating', 'N/A')}/10")
                print(f"{movie.get('overview', 'Sin sinopsis')}")
                print(f"Plataformas: {', '.join(movie.get('streaming_platforms', ['No disponible']))}")

                if movie.get('similar_movies'):
                    print("Películas similares:")
                    for similar in movie['similar_movies']:
                        print(f"  - {similar['title']} ({similar.get('rating', 'N/A')}/10)")
                print()

            else:
                print("No pude encontrar información de esa película")

    elif 'aleator' in user_input.lower():
        print("Buscando película aleatoria...")
        result = movie_client.call_tool("get_random_movie", {})

        if 'result' in result and 'title' in result['result']:
            movie = result['result']
            print(f"\nPelícula aleatoria: {movie['title']}")
            print(f"Rating: {movie.get('rating', 'N/A')}/10")
            print(f"{movie.get('overview', 'Sin sinopsis')}\n")
        else:
            print("Error al obtener película aleatoria")

    else:
        print("Procesando consulta sobre películas...")
        mensajes_historial.append({"role": "user", "content": user_input})
        chat_completion = cliente_groq.chat.completions.create(
            messages=mensajes_historial,
            model="llama-3.1-8b-instant",
            temperature=0.7,
        )
        respuesta = chat_completion.choices[0].message.content
        mensajes_historial.append({"role": "assistant", "content": respuesta})
        print(f"{respuesta}")


def extract_arxiv_query(user_input):
    """Extraer términos de búsqueda para arXiv"""
    stop_words = ['buscar', 'busca', 'encontrar', 'encuentra', 'arxiv', 'papers',
                  'artículos', 'articulos', 'artículo', 'articulo', 'paper', 'sobre', 'de', 'acerca']

    query = user_input.lower()
    for word in stop_words:
        query = query.replace(word, '')

    # Remover números si son para cantidad
    query = ' '.join([word for word in query.split() if not word.isdigit()])

    return query.strip() or "computer science"


def extract_paper_id(user_input):
    """Extraer ID de paper para descargar"""
    words = user_input.split()
    for i, word in enumerate(words):
        if word.lower() in ['paper', 'artículo', 'articulo', 'numero', 'number'] and i + 1 < len(words):
            return words[i + 1]

    # Buscar patrones de ID de arXiv
    arxiv_pattern = r'\d+\.\d+(v\d+)?'
    matches = re.findall(arxiv_pattern, user_input)
    if matches:
        return matches[0]

    return None


def handle_arxiv_query(user_input: str, arxiv_client):
    """Manejar consultas sobre artículos académicos"""
    print("Buscando en arXiv...")

    # Extraer número de resultados si se especifica
    num_results = 3
    for word in ['cinco', 'five', 'tres', 'three', 'diez', 'ten']:
        if word in user_input.lower():
            if word in ['cinco', 'five']:
                num_results = 5
            elif word in ['tres', 'three']:
                num_results = 3
            elif word in ['diez', 'ten']:
                num_results = 10

    if 'reciente' in user_input.lower() or 'recientes' in user_input.lower() or 'nuevo' in user_input.lower() or 'nuevos' in user_input.lower():
        # Buscar papers nuevos
        query = extract_arxiv_query(user_input)
        result = arxiv_client.call_tool("search_arxiv", {
            "query": query,
            "sort_by": "date",
            "sort_order": "descending"
        })

        if 'result' in result and 'papers' in result['result']:
            papers = result['result']['papers'][:num_results]
            print(f"\nArtículos recientes sobre {query}:")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.get('title', 'Sin título')}")
                print(f"   Autores: {', '.join(paper.get('authors', []))}")
                print(f"   Fecha: {paper.get('published', 'N/A')}")
                print(f"   ID: {paper.get('id', 'N/A')}")
                print()
        else:
            print("No se pudieron obtener artículos de arXiv")

    elif 'importante' in user_input.lower() or 'relevante' in user_input.lower():
        # Buscar papers importantes (por relevancia)
        query = extract_arxiv_query(user_input)
        result = arxiv_client.call_tool("search_arxiv", {
            "query": query,
            "sort_by": "relevance",
            "sort_order": "descending"
        })

        if 'result' in result and 'papers' in result['result']:
            papers = result['result']['papers'][:num_results]
            print(f"\nArtículos relevantes sobre {query}:")
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper.get('title', 'Sin título')}")
                print(f"   Autores: {', '.join(paper.get('authors', []))}")
                print(f"   ID: {paper.get('id', 'N/A')}")
                print()
        else:
            print("No se encontraron artículos relevantes")

    else:
        # Búsqueda general
        query = extract_arxiv_query(user_input)
        if query:
            result = arxiv_client.call_tool("search_arxiv", {
                "query": query,
                "max_results": num_results
            })

            if 'result' in result and 'papers' in result['result']:
                papers = result['result']['papers']
                print(f"\nResultados para '{query}':")
                for i, paper in enumerate(papers, 1):
                    print(f"{i}. {paper.get('title', 'Sin título')}")
                    print(f"   Autores: {', '.join(paper.get('authors', []))}")
                    print(f"   Resumen: {paper.get('summary', 'Sin resumen')[:100]}...")
                    print()
            else:
                print("No se encontraron artículos")
        else:
            print("Por favor especifica qué quieres buscar en arXiv")


def handle_unit_conversion(user_input: str, remote_client):
    """Manejar conversión de unidades"""
    print("Conectando con servidor remoto...")

    # Extraer números del input
    numbers = re.findall(r'\d+\.?\d*', user_input)
    if not numbers:
        print("Por favor incluye un valor numérico para convertir (ej: 'convertir 25 celsius a fahrenheit')")
        return

    value = float(numbers[0])

    # Detectar unidades
    units_map = {
        'celsius': ['celsius', 'c°', 'centígrados', 'centigrados'],
        'fahrenheit': ['fahrenheit', 'f°'],
        'kelvin': ['kelvin', 'k°'],
        'meter': ['metro', 'metros', 'm'],
        'kilometer': ['kilómetro', 'kilometro', 'km', 'kilómetros', 'kilometros'],
        'mile': ['milla', 'millas'],
        'kilogram': ['kilogramo', 'kilo', 'kg', 'kilogramos'],
        'pound': ['libra', 'libras', 'lb']
    }

    from_unit = None
    to_unit = None

    for unit_key, unit_names in units_map.items():
        for name in unit_names:
            if name in user_input.lower():
                if from_unit is None:
                    from_unit = unit_key
                else:
                    to_unit = unit_key
                    break

    if from_unit and to_unit:
        result = remote_client.call_tool("convert_units", {
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit
        })

        if 'result' in result and 'converted_value' in result['result']:
            conv = result['result']
            print(f"\n{conv['original_value']} {conv['from_unit']} = {conv['converted_value']} {conv['to_unit']}")
        else:
            print(
                "Error en la conversión. Unidades soportadas: celsius, fahrenheit, meter, kilometer, mile, kilogram, pound")
    else:
        print("Ejemplos de uso:")
        print("  • 'convertir 25 celsius a fahrenheit'")
        print("  • '100 kilómetros a millas'")
        print("  • '5 kilogramos a libras'")


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
    """Chat interactivo con integración MCP múltiple"""
    movie_client = MovieMCPClient("http://localhost:8000")
    arxiv_client = ArxivMCPClient("http://localhost:8001")
    remote_client = RemoteUnitConverterClient("https://unit-converter-mcp-304357449334.us-central1.run.app")  # Cambiar por URL remota después

    print("Bienvenido al Chatbot Multi-MCP")
    print("Puedo ayudarte con:")
    print("  • Películas: 'buscar inception', 'película aleatoria'")
    print("  • Artículos académicos: 'buscar papers sobre IA', 'artículos recientes de física'")
    print("  • Conversión de unidades: 'convertir 25 celsius a fahrenheit', '100 km a millas'")
    print("  • Conversación general")
    print("Escribe 'salir' para terminar la sesión\n")

    while True:
        user_input = input("Tu: ").strip()

        if user_input.lower() in ['salir', 'exit', 'quit']:
            break

        # Detectar tipo de consulta
        movie_keywords = ['película', 'pelicula', 'movie', 'cine', 'netflix', 'disney',
                          'buscar película', 'película aleatoria']

        arxiv_keywords = ['arxiv', 'paper', 'papers', 'artículo', 'articulo', 'investigación',
                          'académico', 'científico', 'investigacion', 'academico', 'cientifico']

        unit_keywords = ['convertir', 'conversión', 'unidades', 'celsius', 'fahrenheit',
                         'kelvin', 'metros', 'kilómetros', 'millas', 'kilogramos', 'libras',
                         'conversion', 'km', 'm', 'kg', 'lb']

        if any(keyword in user_input.lower() for keyword in movie_keywords):
            handle_movie_query(user_input, movie_client)

        elif any(keyword in user_input.lower() for keyword in arxiv_keywords):
            handle_arxiv_query(user_input, arxiv_client)

        elif any(keyword in user_input.lower() for keyword in unit_keywords):
            handle_unit_conversion(user_input, remote_client)

        else:
            handle_general_query(user_input)


if __name__ == "__main__":
    chat_con_multi_bot()