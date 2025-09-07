# chatbot_groq_mcp.py
import os
import sys
import asyncio
import shlex
import groq
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

GROQ_API_KEY = os.environ.get("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")
if not GROQ_API_KEY:
    print("Debes definir GROQ_API_KEY en variables de entorno.")
    sys.exit(1)

cliente = groq.Groq(api_key=GROQ_API_KEY)
mensajes_historial = []

def chat_LLM(user_input):
    mensajes_historial.append({"role": "user", "content": user_input})
    chat_completion = cliente.chat.completions.create(
        messages=mensajes_historial,
        model="openai/gpt-oss-20b",
        temperature=0.5,
    )
    respuesta_LLM = chat_completion.choices[0].message.content
    mensajes_historial.append({"role": "assistant", "content": respuesta_LLM})
    print(f"LLM: {respuesta_LLM}")
    with open("mcp_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"USER: {user_input}\nLLM: {respuesta_LLM}\n\n")
    return respuesta_LLM

class MovieMCPManager:
    def __init__(self):
        self.session: ClientSession | None = None

    async def connect(self):
        if self.session is not None:
            return
        params = StdioServerParameters(
            command="python",
            args=["movie_server.py"],
            env=os.environ.copy(),
        )
        read, write = await stdio_client(params)
        self.session = ClientSession(read, write)
        await self.session.initialize()

    async def call_tool(self, tool_name: str, args: dict = None):
        await self.connect()
        return await self.session.call_tool(tool_name, args or {})

mcp_manager = MovieMCPManager()

def main_loop():
    print("Chatbot con Groq + Movie MCP Server")
    print("Comandos disponibles:")
    print("  /movie <titulo>      -> busca película")
    print("  /random              -> sugiere película aleatoria")
    print("  /recommend <género>  -> recomienda películas por género")
    print("Cualquier otro texto   -> conversación normal con el LLM")
    while True:
        user_input = input(">> ").strip()
        if user_input.lower() == "salir":
            break

        if user_input.startswith("/movie"):
            parts = shlex.split(user_input)
            if len(parts) < 2:
                print("Uso: /movie <titulo>")
                continue
            titulo = " ".join(parts[1:])
            result = asyncio.run(mcp_manager.call_tool("search_movie_tool", {"query": titulo}))
            print("🎬 Resultados:")
            print(result.content)
            continue

        if user_input.startswith("/random"):
            result = asyncio.run(mcp_manager.call_tool("random_movie_tool"))
            print("🎲 Sugerencia:")
            print(result.content)
            continue

        if user_input.startswith("/recommend"):
            parts = shlex.split(user_input)
            genre = parts[1] if len(parts) > 1 else "Action"
            result = asyncio.run(mcp_manager.call_tool("recommend_movies_tool", {"genre": genre}))
            print("⭐ Recomendaciones:")
            print(result.content)
            continue

        print(f"USER: {user_input}")
        chat_LLM(user_input)

if __name__ == "__main__":
    main_loop()
