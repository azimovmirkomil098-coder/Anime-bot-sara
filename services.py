import aiohttp

JIKAN_URL = "https://api.jikan.moe/v4"

async def search_anime(query: str):
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f"{JIKAN_URL}/anime", params={"q": query, "limit": 8, "sfw": "true"}) as resp:
            if resp.status == 429:
                raise RuntimeError("Qidiruv xizmati vaqtincha band. Birozdan keyin urinib ko‘ring.")
            resp.raise_for_status()
            data = await resp.json()
            return data.get("data", [])

async def get_anime(anime_id: int):
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(f"{JIKAN_URL}/anime/{anime_id}/full") as resp:
            if resp.status == 429:
                raise RuntimeError("Xizmat vaqtincha band. Birozdan keyin urinib ko‘ring.")
            resp.raise_for_status()
            data = await resp.json()
            return data.get("data")
