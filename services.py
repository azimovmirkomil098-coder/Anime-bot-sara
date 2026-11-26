import aiohttp

JIKAN_URL = "https://api.jikan.moe/v4"


async def _get_json(path: str, *, params=None):
    timeout = aiohttp.ClientTimeout(total=20, connect=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{JIKAN_URL}{path}", params=params) as response:
                if response.status == 429:
                    raise RuntimeError(
                        "Qidiruv xizmati vaqtincha band. Birozdan keyin urinib ko‘ring."
                    )
                if response.status >= 500:
                    raise RuntimeError("Anime ma’lumotlari xizmati vaqtincha ishlamayapti.")
                response.raise_for_status()
                payload = await response.json(content_type=None)
                return payload.get("data") if isinstance(payload, dict) else None
    except aiohttp.ClientError as exc:
        raise RuntimeError("Anime ma’lumotlari xizmatiga ulanib bo‘lmadi.") from exc
    except TimeoutError as exc:
        raise RuntimeError("Anime ma’lumotlari xizmati javob bermadi.") from exc


async def search_anime(query: str):
    query = query.strip()
    if not query:
        return []
    data = await _get_json("/anime", params={"q": query, "limit": 8, "sfw": "true"})
    return data if isinstance(data, list) else []


async def get_anime(anime_id: int):
    if int(anime_id) <= 0:
        return None
    data = await _get_json(f"/anime/{int(anime_id)}/full")
    return data if isinstance(data, dict) else None
