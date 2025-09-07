import os
import sys
import json
import asyncio
import shlex
from pathlib import Path

import groq
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, types

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Falta GROQ_API_KEY en variables de entorno.")
    sys.exit(1)

cliente = groq.Groq(api_key=GROQ_API_KEY)
mensajes_historial = []

WORKDIR = str(Path.cwd().resolve())

class MCPManager:
    def __init__(self, allowed_dir: str):
        self.allowed_dir = str(Path(allowed_dir).resolve())
        self.fs_session: ClientSession | None = None
        self.git_session: ClientSession | None = None

    async def connect_filesystem(self):
        # server oficial filesystem vía npx
        fs_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", self.allowed_dir],
            env=os.environ.copy(),
        )
        read, write = await stdio_client(fs_params)
        self.fs_session = ClientSession(read, write)
        await self.fs_session.initialize()

    async def connect_git(self):
        # servidor Git MCP (Python) instalado con pip: mcp-server-git
        git_params = StdioServerParameters(
            command="mcp-server-git",
            args=[],
            env=os.environ.copy(),
        )
        read, write = await stdio_client(git_params)
        self.git_session = ClientSession(read, write)
        await self.git_session.initialize()

    async def ensure_connected(self):
        if self.fs_session is None:
            await self.connect_filesystem()
        if self.git_session is None:
            await self.connect_git()

    async def list_tools(self):
        await self.ensure_connected()
        fs_tools = await self.fs_session.list_tools()
        git_tools = await self.git_session.list_tools()
        return fs_tools.tools, git_tools.tools

    async def fs_write_file(self, abs_path: str, content: str):
        await self.ensure_connected()

        return await self.fs_session.call_tool("write_file", {"path": abs_path, "content": content})

    async def fs_read_file(self, abs_path: str):
        await self.ensure_connected()
        return await self.fs_session.call_tool("read_file", {"path": abs_path})

    async def git_init(self, repo_path: str):
        await self.ensure_connected()
        return await self.git_session.call_tool("git_init", {"repo_path": repo_path})

    async def git_add(self, repo_path: str, files: list[str]):
        await self.ensure_connected()

        tools_resp = await self.git_session.list_tools()
        add_tool = next((t for t in tools_resp.tools if t.name == "git_add"), None)
        args = {"repo_path": repo_path}
        if add_tool and add_tool.inputSchema and hasattr(add_tool.inputSchema, "json"):
            schema = json.loads(add_tool.inputSchema.json()) if hasattr(add_tool.inputSchema, "json") else {}
            props = schema.get("properties", {})
            if "files" in props:
                args["files"] = files
            elif "paths" in props:
                args["paths"] = files
            elif "pathspec" in props:
                # algunos servidores aceptan una string tipo "." o "README.md"
                args["pathspec"] = " ".join(files)
            else:
                # fallback razonable
                args["files"] = files
        else:
            args["files"] = files
        return await self.git_session.call_tool("git_add", args)

    async def git_commit(self, repo_path: str, message: str):
        await self.ensure_connected()
        return await self.git_session.call_tool("git_commit", {"repo_path": repo_path, "message": message})

    async def demo_repo(self, repo_dir: str):

        abs_repo = str(Path(repo_dir).resolve())
        if not abs_repo.startswith(self.allowed_dir):
            raise ValueError(f"La ruta debe estar dentro de {self.allowed_dir}")

        readme_path = str(Path(abs_repo) / "README.md")
        readme_text = "# Demo MCP\n\nRepositorio creado por el bot con MCP (Filesystem + Git).\n"

        await self.fs_write_file(readme_path, readme_text)

        # 3) git init
        await self.git_init(abs_repo)

        # 4) git add README
        await self.git_add(abs_repo, ["README.md"])

        # 5) git commit
        out = await self.git_commit(abs_repo, "chore: commit inicial con README")
        return {
            "repo": abs_repo,
            "readme": readme_path,
            "commit": out.structuredContent if hasattr(out, "structuredContent") else None,
        }

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

mcp_manager = MCPManager(WORKDIR)

def main_loop():
    print("Bot listo. Comandos MCP disponibles:")
    print("  /demo_repo <ruta>               -> crea repo, README, add, commit")
    print("  /fs write <ruta_abs> <texto>    -> escribe archivo (crea dirs)")
    print("  /git init <ruta_repo>           -> git init")
    print("  /git add <ruta_repo> <files...> -> git add")
    print("  /git commit <ruta_repo> <msg>   -> git commit")
    print("Cualquier otro texto -> conversación normal con el LLM (Groq).")
    while True:
        user_input = input("Pregunta (o 'salir'): ").strip()
        if user_input.lower() == "salir":
            break

        if user_input.startswith("/demo_repo"):
            # /demo_repo ./pelis-demo
            parts = shlex.split(user_input)
            if len(parts) < 2:
                print("Uso: /demo_repo <ruta>")
                continue
            ruta = parts[1]
            try:
                result = asyncio.run(mcp_manager.demo_repo(ruta))
                print(f"OK: Repo en {result['repo']}")
                print(f"     README: {result['readme']}")
                print("     Commit inicial realizado.")
            except Exception as e:
                print(f"Error demo_repo: {e}")
            continue

        if user_input.startswith("/fs write"):
            # /fs write /abs/path/file.txt "contenido"
            parts = shlex.split(user_input)
            if len(parts) < 4:
                print("Uso: /fs write <ruta_abs> <contenido>")
                continue
            path_abs, content = parts[2], parts[3]
            try:
                asyncio.run(mcp_manager.fs_write_file(path_abs, content))
                print("OK: Archivo escrito.")
            except Exception as e:
                print(f"Error fs write: {e}")
            continue

        if user_input.startswith("/git init"):
            parts = shlex.split(user_input)
            if len(parts) < 3:
                print("Uso: /git init <ruta_repo>")
                continue
            ruta_repo = parts[2]
            try:
                asyncio.run(mcp_manager.git_init(str(Path(ruta_repo).resolve())))
                print("OK: git init.")
            except Exception as e:
                print(f"Error git init: {e}")
            continue

        if user_input.startswith("/git add"):
            parts = shlex.split(user_input)
            if len(parts) < 4:
                print("Uso: /git add <ruta_repo> <files...>")
                continue
            ruta_repo = str(Path(parts[2]).resolve())
            files = parts[3:]
            try:
                asyncio.run(mcp_manager.git_add(ruta_repo, files))
                print("OK: git add.")
            except Exception as e:
                print(f"Error git add: {e}")
            continue

        if user_input.startswith("/git commit"):
            # /git commit <ruta_repo> "mensaje"
            parts = shlex.split(user_input)
            if len(parts) < 4:
                print('Uso: /git commit <ruta_repo> "mensaje"')
                continue
            ruta_repo = str(Path(parts[2]).resolve())
            msg = parts[3]
            try:
                asyncio.run(mcp_manager.git_commit(ruta_repo, msg))
                print("OK: git commit.")
            except Exception as e:
                print(f"Error git commit: {e}")
            continue

        # Conversación normal con Groq
        print(f"USER: {user_input}")
        chat_LLM(user_input)

if __name__ == "__main__":
    main_loop()
