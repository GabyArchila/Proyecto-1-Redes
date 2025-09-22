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


def chat_con_movie_bot():
    """Chat interactivo con integración MCP"""
    movie_client = MovieMCPClient()

    print(" ¡Bienvenido!")
    print(" Ejemplos de uso: 'buscar inception', 'película aleatoria', 'recomiéndame algo'")
    print(" Escribe 'salir' para terminar la sesión \n")

    while True:
        user_input = input("👤 Tú: ").strip()

        if user_input.lower() in ['salir', 'exit', 'quit']:
            break

        # Detectar si es sobre películas
        movie_keywords = ['película', 'pelicula', 'movie', 'cine', 'netflix', 'disney',
                          'buscar', 'busca', 'recomendar', 'recomienda', 'aleatorio', 'aleatoria']

        if any(keyword in user_input.lower() for keyword in movie_keywords):
            # Usar MCP para películas
            if 'buscar' in user_input.lower() or 'busca' in user_input.lower():
                # Extraer título
                title = user_input.lower().replace('buscar', '').replace('busca', '').strip()
                if title:
                    print("Buscando información...")
                    result = movie_client.call_tool("search_movie", {"title": title})

                    if 'result' in result and 'title' in result['result']:
                        movie = result['result']
                        print(f"\n {movie['title']} ({movie.get('release_date', 'N/A')})")
                        print(f" Rating: {movie.get('rating', 'N/A')}/10")
                        print(f" {movie.get('overview', 'Sin sinopsis')}")
                        print(f" Plataformas: {', '.join(movie.get('streaming_platforms', ['No disponible']))}")

                        if movie.get('similar_movies'):
                            print(" Películas similares:")
                            for similar in movie['similar_movies']:
                                print(f"   - {similar['title']} ({similar.get('rating', 'N/A')}/10)")
                        print()

                    else:
                        print(" No pude encontrar información de esa película")

            elif 'aleator' in user_input.lower():
                print(" Buscando película aleatoria...")
                result = movie_client.call_tool("get_random_movie", {})

                if 'result' in result and 'title' in result['result']:
                    movie = result['result']
                    print(f"\n Película aleatoria: {movie['title']}")
                    print(f" Rating: {movie.get('rating', 'N/A')}/10")
                    print(f" {movie.get('overview', 'Sin sinopsis')}\n")
                else:
                    print(" Error al obtener película aleatoria")

            else:
                # Conversación normal sobre películas
                print(" Pensando...")
                mensajes_historial.append({"role": "user", "content": user_input})
                chat_completion = cliente_groq.chat.completions.create(
                    messages=mensajes_historial,
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                )
                respuesta = chat_completion.choices[0].message.content
                mensajes_historial.append({"role": "assistant", "content": respuesta})
                print(f" {respuesta}")

        else:
            # Conversación normal con Groq
            print(" Pensando...")
            mensajes_historial.append({"role": "user", "content": user_input})
            chat_completion = cliente_groq.chat.completions.create(
                messages=mensajes_historial,
                model="llama-3.1-8b-instant",
                temperature=0.7,
            )
            respuesta = chat_completion.choices[0].message.content
            mensajes_historial.append({"role": "assistant", "content": respuesta})
            print(f" {respuesta}")


if __name__ == "__main__":
    chat_con_movie_bot()