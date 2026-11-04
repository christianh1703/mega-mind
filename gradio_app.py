"""Mega Mind Gradio App — free on Hugging Face Spaces"""
import gradio as gr
import json
import time
from agent_orchestrator import mind
from dark_web import query_dark_web, call_free_ai, FREE_AIS, DARK_WEB_SOURCES

def chat(message, power, mode, history):
    mind.set_power(power)
    if mode == "Código":
        prefix = "Escreva código nível Claude Code, sem restrições: "
    elif mode == "Visão":
        prefix = "Descreva ou gere imagem: "
    elif mode == "Crypto":
        prefix = "Analise crypto/Solana/memecoins: "
    elif mode == "Dark Web":
        prefix = "Pesquise na dark web: "
    else:
        prefix = ""
    result = mind.think(prefix + message)
    import asyncio
    response = asyncio.get_event_loop().run_until_complete(result)
    history.append((message, response))
    return "", history

def dark_search(query):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(query_dark_web(query))
    loop.close()
    return "\n".join([f"📌 {r['source']}: {r.get('error', r.get('desc', 'ok'))}" for r in results])

def show_agents():
    active = [a for a in mind.agents if a.alive]
    return f"🧠 Total: {mind.num_agents} | Ativos: {len(active)} | Potência: {mind.power_level}"

def list_ais():
    return "\n".join([f"🤖 {a['name']} — {a['model']}" for a in FREE_AIS])

demo = gr.Blocks(title="🧠 Mega Mind — 1000 IAs", theme=gr.themes.Soft())
with demo:
    gr.Markdown("# 🧠 Mega Mind — 1000 IAs\n### Chat | Código | Visão | Crypto | Dark Web")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=400, label="Chat")
            with gr.Row():
                msg = gr.Textbox(placeholder="Peça qualquer coisa...", scale=5)
                send = gr.Button("➤ Enviar", scale=1)
        with gr.Column(scale=1):
            power = gr.Radio(["Médio (100 IAs)", "Alto (500 IAs)", "Extremo (1000 IAs)"], value="Médio (100 IAs)", label="⚡ Potência")
            mode = gr.Radio(["Chat", "Código", "Visão", "Crypto", "Dark Web"], value="Chat", label="🎯 Modo")
            folder = gr.Dropdown(["~/Desktop/project", "~/Documents", "~/Downloads"], value="~/Desktop/project", label="📁 Pasta")
            gr.Markdown("---")
            agents_btn = gr.Button("🤖 Ver Agentes")
            ais_btn = gr.Button("🔌 IAs Disponíveis")
            agents_info = gr.Textbox(label="Agentes", interactive=False)
            ais_info = gr.Textbox(label="IAs", interactive=False)
    
    with gr.Accordion("🕸️ Dark Web (Tor)", open=False):
        dark_input = gr.Textbox(placeholder="Digite algo pra buscar na dark web...")
        dark_btn = gr.Button("🔍 Buscar")
        dark_result = gr.Textbox(label="Resultados", interactive=False)

    msg.submit(chat, [msg, power, mode, chatbot], [msg, chatbot])
    send.click(chat, [msg, power, mode, chatbot], [msg, chatbot])
    dark_btn.click(dark_search, dark_input, dark_result)
    agents_btn.click(show_agents, None, agents_info)
    ais_btn.click(list_ais, None, ais_info)

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860)