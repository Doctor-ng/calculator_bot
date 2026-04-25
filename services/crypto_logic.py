import httpx
import time

CACHE_TTL = 60

price_cache = {}
coin_id_cache = {}
usd_inr_cache = (0.0, 0.0)

from config import COINGECKO_API_KEY  # type: ignore
 
# ===== USD → INR =====
async def get_usd_inr():
    global usd_inr_cache
    rate, ts = usd_inr_cache
    if time.time() - ts < CACHE_TTL and rate:
        return rate

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "usd",
                "vs_currencies": "inr",
                "x_cg_demo_api_key": COINGECKO_API_KEY,
            },
        )
        rate = r.json()["usd"]["inr"]
        usd_inr_cache = (rate, time.time())
        return rate

# ===== COIN ID (same as old) =====
async def get_coin_id(symbol: str):
    symbol = symbol.lower()
    if symbol in coin_id_cache:
        return coin_id_cache[symbol]

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": symbol},
        )
        coins = r.json().get("coins", [])
        if not coins:
            return None

        cid = coins[0]["id"]
        coin_id_cache[symbol] = cid
        return cid


# ===== USD PRICE (same as old) =====
async def get_coin_price(cid: str):
    if cid in price_cache:
        data, ts = price_cache[cid]
        if time.time() - ts < CACHE_TTL:
            return data

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": cid,
                "vs_currencies": "usd,inr",
                "x_cg_demo_api_key": COINGECKO_API_KEY,
            },
        )

    data = r.json().get(cid)

    if not data:
        return None

    price_cache[cid] = (data, time.time())
    return data
    
# ===== SAME OLD FUNCTION (IMPORTANT) =====
async def process_single_crypto(text: str):
    import re

    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([A-Za-z]{2,10})", text)
    if not m:
        return None

    amount, symbol = m.groups()

    cid = await get_coin_id(symbol)
    if not cid:
        return None

    price_data = await get_coin_price(cid)

    if not price_data:
     return None

    usd_price = price_data.get("usd")
    inr_price = price_data.get("inr")

    usd = float(amount) * usd_price
    
    # ✅ fallback system
    if inr_price:
       inr = float(amount) * inr_price
    else:
       inr = usd * await get_usd_inr()
   
    return {
        "amount": amount,
        "symbol": symbol.upper(),
        "name": cid.replace("-", " ").title(),
        "usd": usd,
        "inr": inr
    }