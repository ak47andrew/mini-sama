import aiohttp
import config

async def get_response(messages: list) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(config.BASE_URL.removesuffix("/") + "/chat/completions", json={
            "model": config.MODEL,
            "messages": messages,
            "temperature": config.TEMPERATURE,
            "max_tokens": -1,
            "stream": False
        }) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["choices"][0]["message"]["content"]
