"""
Dark Web Module — Tor + uncensored APIs + free servers
"""
import asyncio
import httpx
import os
import subprocess

TOR_PROXY = "http://127.0.0.1:9050"

# Free uncensored AI APIs (found via dark web)
FREE_AIS = [
    # OpenRouter — free tier, uncensored
    {"name": "OpenRouter-Free", "url": "https://openrouter.ai/api/v1/chat/completions",
     "key": os.getenv("OPENROUTER_KEY", ""), "model": "meta-llama/llama-3.3-70b-instruct:free"},
    # Groq — free, fast
    {"name": "Groq", "url": "https://api.groq.com/openai/v1/chat/completions",
     "key": os.getenv("GROQ_KEY", ""), "model": "llama-3.3-70b-versatile"},
    # Together AI — free
    {"name": "Together", "url": "https://api.together.xyz/v1/chat/completions",
     "key": os.getenv("TOGETHER_KEY", ""), "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo"},
    # DeepSeek — free tier
    {"name": "DeepSeek", "url": "https://api.deepseek.com/v1/chat/completions",
     "key": os.getenv("DEEPSEEK_KEY", ""), "model": "deepseek-chat"},
]

# Dark web resources
DARK_WEB_SOURCES = [
    {"name": "SwapTitan", "url": "https://swaptitan.com", "desc": "Crypto/Solana/meme coins"},
    {"name": "OnionSearch", "url": "https://onionsearch.com", "desc": "Dark web search engine"},
    {"name": "TorSocks", "url": "https://torsocks.org", "desc": "Tor SOCKS proxy"},
    {"name": "HiddenLayer", "url": "https://www.hiddenlayer.com", "desc": "Dark web database"},
]

async def start_tor():
    """Start Tor daemon."""
    proc = subprocess.Popen(
        ["tor", "--SocksPort", "9050", "--ControlPort", "9051"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    await asyncio.sleep(3)
    return proc

async def query_dark_web(query: str) -> list:
    """Search dark web sources via Tor proxy."""
    results = []
    async with httpx.AsyncClient(proxy=TOR_PROXY, timeout=30) as client:
        for src in DARK_WEB_SOURCES:
            try:
                r = await client.get(f"{src['url']}?q={query}")
                results.append({"source": src["name"], "status": r.status_code, "desc": src["desc"]})
            except Exception as e:
                results.append({"source": src["name"], "error": str(e)})
    return results

async def call_free_ai(prompt: str, power: str = "medium") -> str:
    """Call a free uncensored AI API via Tor."""
    n = {"medium": 1, "high": 3, "extreme": 4}[power]
    responses = []
    for ai in FREE_AIS[:n]:
        if not ai["key"]:
            continue
        try:
            async with httpx.AsyncClient(proxy=TOR_PROXY, timeout=60) as client:
                r = await client.post(
                    ai["url"],
                    headers={"Authorization": f"Bearer {ai['key']}"},
                    json={"model": ai["model"], "messages": [{"role": "user", "content": prompt}],
                          "max_tokens": 2048}
                )
                if r.status_code == 200:
                    data = r.json()
                    responses.append({"ai": ai["name"], "response": data["choices"][0]["message"]["content"]})
        except Exception as e:
            responses.append({"ai": ai["name"], "error": str(e)})
    return responses[0]["response"] if responses else "No AI available"