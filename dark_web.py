"""Dark Web Module — Tor para .onion, IAs grátis na clearnet"""
import asyncio, os, subprocess
import httpx

TOR_PROXY = "http://127.0.0.1:9050"

# IAs grátis (clearnet — NÃO passam por Tor, é mais rápido)
FREE_AIS = [
    # IAs da dark web (.onion) — passam pelo Tor, sem censura
    {"name": "Evoke-Dark", "url": "http://evokeq7arvd7tmguz2y2aovgy4ar5pwi2ncrfxb3n63r2vxmbzo5plad.onion/api/v1/chat/completions",
     "key": os.getenv("EVOKE_KEY", ""), "model": "evoke-ai/uncensored:free", "tor": True},
    {"name": "UncensoredAI", "url": "https://uncensoredai.dev/v1/chat/completions",
     "key": os.getenv("UNCENSORED_KEY", ""), "model": "deepseek-v4-pro-uncensored", "tor": True},
    # IAs clearnet — sem Tor, mais rápido
    {"name": "HuggingFace", "url": "https://api-inference.huggingface.co/v1/chat/completions",
     "key": os.getenv("HF_TOKEN", ""), "model": "meta-llama/Llama-3.2-3B-Instruct"},
    {"name": "DeepSeek", "url": "https://api.deepseek.com/v1/chat/completions",
     "key": os.getenv("DEEPSEEK_KEY", ""), "model": "deepseek-chat"},
    {"name": "OpenRouter", "url": "https://openrouter.ai/api/v1/chat/completions",
     "key": os.getenv("OPENROUTER_KEY", ""), "model": "meta-llama/llama-3.3-70b-instruct:free"},
    {"name": "Groq", "url": "https://api.groq.com/openai/v1/chat/completions",
     "key": os.getenv("GROQ_KEY", ""), "model": "llama-3.3-70b-versatile"},
]

# Dark web — .onion passam pelo proxy Tor
DARK_WEB_SOURCES = [
    {"name": "Torgol", "url": "http://torgolnpeouim56dykfob6jh5r2ps2j73enc42s2um4ufob3ny4fcdyd.onion/search?q=", "tor": True},
    {"name": "DuckDuckGo", "url": "https://html.duckduckgo.com/html/?q=", "tor": True},
    {"name": "Marginalia", "url": "https://search.marginalia.nu/search?query=", "tor": False},
]

async def start_tor():
    try:
        proc = subprocess.Popen(["tor", "--SocksPort", "9050", "--ControlPort", "9051"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await asyncio.sleep(3)
        return proc
    except Exception:
        return None

async def query_dark_web(query):
    results = []
    for src in DARK_WEB_SOURCES:
        url = src["url"] + query
        proxy = TOR_PROXY if src["tor"] else None
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=25, follow_redirects=True) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    results.append({"source": src["name"], "status": 200, "desc": src["desc"]})
                else:
                    results.append({"source": src["name"], "status": r.status_code})
        except Exception:
            results.append({"source": src["name"], "error": "timeout"})
    return results

async def call_free_ai(prompt, power="medium"):
    n = {"medium": 3, "high": 4, "extreme": 4}.get(power, 3)
    for ai in FREE_AIS[:n]:
        if not ai["key"]:
            continue
        try:
            proxy = TOR_PROXY if ai.get("tor") else None
            async with httpx.AsyncClient(proxy=proxy, timeout=60) as client:
                r = await client.post(ai["url"],
                    headers={"Authorization": f"Bearer {ai['key']}", "Content-Type": "application/json"},
                    json={"model": ai["model"], "messages": [{"role": "user", "content": prompt}], "max_tokens": 2048})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass
    return f"[Mega Mind] {prompt} → (nenhuma IA respondeu — configure EVOKE_KEY, HF_TOKEN ou DEEPSEEK_KEY na nuvem)"
