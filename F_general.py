import groq

cliente = groq.Groq(api_key="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")
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

    print(f"USER: {user_input}")
    print(f"LLM: {respuesta_LLM}")
    with open("mcp_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"USER: {user_input}\nLLM: {respuesta_LLM}\n\n")

    return respuesta_LLM


while True:
    user_input = input("Pregunta (si deseas salir puedes escribe 'salir'): ")
    if user_input.lower() in ["salir"]:
        break
    respuesta = chat_LLM(user_input)