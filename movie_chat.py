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
        self.name = "Películas"

    def call_tool(self, tool_name: str, arguments: dict):
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
            self.log_interaction("REQUEST", payload)
            result = response.json()
            self.log_interaction("RESPONSE", result)
            return result
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_interaction("ERROR", error_result)
            return error_result

    def log_interaction(self, type_msg, data):
        with open("mcp_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"[MOVIES MCP] {type_msg}: {json.dumps(data, indent=2, ensure_ascii=False)}\n\n")


class ArxivMCPClient:
    def __init__(self, server_url="http://localhost:8001"):
        self.server_url = server_url
        self.name = "ArXiv Papers"

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
            self.log_interaction("REQUEST", payload)
            result = response.json()
            self.log_interaction("RESPONSE", result)
            return result
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_interaction("ERROR", error_result)
            return error_result

    def log_interaction(self, type_msg, data):
        with open("mcp_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"[ARXIV MCP] {type_msg}: {json.dumps(data, indent=2, ensure_ascii=False)}\n\n")


class RemoteUnitConverterClient:
    def __init__(self, server_url="https://unit-converter-mcp-304357449334.us-central1.run.app"):
        self.server_url = server_url
        self.name = "Convertidor de Unidades"

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
            self.log_interaction("REQUEST", payload)
            result = response.json()
            self.log_interaction("RESPONSE", result)
            return result
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_interaction("ERROR", error_result)
            return error_result

    def log_interaction(self, type_msg, data):
        with open("mcp_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"[UNIT CONVERTER MCP] {type_msg}: {json.dumps(data, indent=2, ensure_ascii=False)}\n\n")


def show_main_menu():
    print("------------------------------- CHATBOT MULTI-MCP -------------------------------")
    print("Selecciona el servidor MCP que deseas usar:")
    print("1. Películas")
    print("2. Artículos Académicos")
    print("3. Convertidor de Unidades")
    print("4. Conversación General (Sin MCP)")
    print("5. Modo Multi-MCP (Detección automática)")
    print("0. Salir")


def extract_arxiv_query(user_input):
    """Extraer términos de búsqueda para arXiv"""
    stop_words = ['buscar', 'busca', 'encontrar', 'encuentra', 'arxiv', 'papers',
                  'artículos', 'articulos', 'artículo', 'articulo', 'paper', 'sobre', 'de', 'acerca']

    query = user_input.lower()
    for word in stop_words:
        query = query.replace(word, '')

    query = ' '.join([word for word in query.split() if not word.isdigit()])
    return query.strip() or "computer science"


def handle_movie_query(user_input: str, movie_client):
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


def handle_arxiv_query(user_input: str, arxiv_client):
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
    """Manejar consultas generales en modo multi"""
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


def handle_movie_queries(movie_client):
    """Modo específico para consultas de películas"""
    print(f"\n--- MODO: {movie_client.name} ---")
    print("  Ejemplos '")
    print("  • 'buscar inception' o '¿qué sabes de Inception?'")
    print("  • 'película aleatoria' o 'recomiéndame algo'")
    print("  • 'cuéntame de comedias' o cualquier pregunta sobre cine")
    print("  • 'volver' - Regresar al menú principal")
    print()

    while True:
        user_input = input("Películas> ").strip()

        if user_input.lower() == 'volver':
            break

        # Usar la función original que ya maneja conversación natural
        handle_movie_query(user_input, movie_client)


def handle_arxiv_queries(arxiv_client):
    print(f"\n--- MODO: {arxiv_client.name} ---")
    print("  Ejemplos '")
    print("  • 'buscar papers sobre inteligencia artificial'")
    print("  • '¿qué hay nuevo en física cuántica?'")
    print("  • 'artículos recientes de machine learning'")
    print("  • 'volver' - Regresar al menú principal")
    print()

    while True:
        user_input = input("ArXiv> ").strip()

        if user_input.lower() == 'volver':
            break

        # Usar la función original que maneja conversación natural
        handle_arxiv_query(user_input, arxiv_client)


def handle_unit_conversion_queries(unit_client):
    print(f"\n--- MODO: {unit_client.name} ---")
    print("  Ejemplos '")
    print("  • 'convertir 25 celsius a fahrenheit'")
    print("  • '¿cuánto son 100 kilómetros en millas?'")
    print("  • 'necesito pasar 5 kilos a libras'")
    print("  • 'volver' - Regresar al menú principal")
    print("Unidades soportadas: celsius, fahrenheit, kelvin, meter, kilometer, mile, kilogram, libra")
    print()

    while True:
        user_input = input("Conversión> ").strip()

        if user_input.lower() == 'volver':
            break

        # Permitir cualquier pregunta natural sobre conversión
        conversion_keywords = ['convertir', 'conversión', 'pasar', 'cuánto', 'celsius', 'fahrenheit',
                               'metro', 'kilo', 'libra', 'milla', 'kilogramo', 'kilometro']

        if any(keyword in user_input.lower() for keyword in conversion_keywords):
            handle_unit_conversion(user_input, unit_client)
        else:
            # Si no detecta conversión, usar LLM general
            print("Procesando consulta...")
            mensajes_historial.append({"role": "user", "content": user_input})
            chat_completion = cliente_groq.chat.completions.create(
                messages=mensajes_historial,
                model="llama-3.1-8b-instant",
                temperature=0.7,
            )
            respuesta = chat_completion.choices[0].message.content
            mensajes_historial.append({"role": "assistant", "content": respuesta})
            print(f"{respuesta}")


def handle_general_conversation():
    print("\n--- MODO: Conversación General ---")
    print("Escribe 'volver' para regresar al menú.")
    print()

    while True:
        user_input = input("General> ").strip()

        if user_input.lower() == 'volver':
            break

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


def handle_multi_mcp_mode():
    movie_client = MovieMCPClient("http://localhost:8000")
    arxiv_client = ArxivMCPClient("http://localhost:8001")
    remote_client = RemoteUnitConverterClient("https://unit-converter-mcp-304357449334.us-central1.run.app")

    print("\n--- MODO: Multi-MCP (Detección Automática) ---")
    print("Puedo detectar automáticamente qué tipo de consulta quieres hacer:")
    print("  • Películas: 'buscar inception', 'película aleatoria'")
    print("  • Papers: 'buscar papers sobre IA', 'artículos recientes'")
    print("  • Conversiones: 'convertir 25 celsius a fahrenheit'")
    print("  • General: cualquier otra consulta")
    print("Escribe 'volver' para regresar al menú principal")
    print()

    while True:
        user_input = input("Multi> ").strip()

        if user_input.lower() == 'volver':
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


def main():
    # Crear archivo de log
    with open("mcp_log.txt", "w", encoding="utf-8") as log_file:
        log_file.write("----------------MCP ---------------- \n\n")

    # Inicializar clientes
    movie_client = MovieMCPClient("http://localhost:8000")
    arxiv_client = ArxivMCPClient("http://localhost:8001")
    remote_client = RemoteUnitConverterClient("https://unit-converter-mcp-304357449334.us-central1.run.app")

    while True:
        show_main_menu()

        try:
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                handle_movie_queries(movie_client)
            elif opcion == "2":
                handle_arxiv_queries(arxiv_client)
            elif opcion == "3":
                handle_unit_conversion_queries(remote_client)
            elif opcion == "4":
                handle_general_conversation()
            elif opcion == "5":
                handle_multi_mcp_mode()
            elif opcion == "0":
                print("¡Hasta luego!")
                break
            else:
                print("Opción no válida. Por favor selecciona un número del 0 al 5.")

        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break


if __name__ == "__main__":
    main()
