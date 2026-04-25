from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import httpx
import time
import httpx
import json
import urllib.parse


from services.crypto_logic import get_coin_id, get_coin_price # type: ignore

CHANNEL_LINKS = [
    "https://t.me/Doc_Tools",
    "https://t.me/DoctorEX0?start=1"
]

REFRESH_COOLDOWN = 7


# ================= API =================
async def get_coin_full(cid: str):
    async with httpx.AsyncClient(timeout=15) as c:
        try:
            r = await c.get(
                f"https://api.coingecko.com/api/v3/coins/{cid}",
                params={"market_data": "true"},
            )
            return r.json()
        except:
            return {}


# ================= COMMAND =================
async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "<b>ℹ️ To get full info of a coin use:</b>\n\n"
            "<b>/p [Coin Name]</b>\n\n"
            "E.g: <code>/p btc</code>",
            parse_mode="HTML"
        )
        return

    cid = await get_coin_id(context.args[0])
    if not cid:
        await update.message.reply_text(
            "<b>❌ Not supported</b>",
            parse_mode="HTML"
        )
        return

    await send_price(update, context, cid)


# ================= MAIN PRICE =================
async def send_price(update, context, cid, edit=False):
    
    # Rotate channel link
    index = context.user_data.get("link_index", 0)
    channel_link = CHANNEL_LINKS[index]
    context.user_data["link_index"] = (index + 1) % len(CHANNEL_LINKS)

    data = await get_coin_full(cid)

    if not data or "market_data" not in data:
        if update.callback_query:
            await update.callback_query.answer("⚠️ Try again later", show_alert=True)
        return

    md = data["market_data"]

    price = md["current_price"]["usd"]
    inr = md["current_price"]["inr"]

    market_cap = md.get("market_cap", {}).get("usd", 0)
    volume_24h = md.get("total_volume", {}).get("usd", 0)

    text = (
        f"🪙 <b>{data['name']} ({data['symbol'].upper()})</b>\n\n"
        f"💵 <b>$</b> <code>{price:,.4f} | ₹{inr:,.2f}</code>\n"
        f"📈 <b>1h:</b> <code>{md.get('price_change_percentage_1h_in_currency', {}).get('usd', 0):.2f}%</code>\n"
        f"📉 <b>24h:</b> <code>{md.get('price_change_percentage_24h', 0):.2f}%</code>\n"
        f"📊 <b>7d:</b> <code>{md.get('price_change_percentage_7d', 0):.2f}%</code>\n\n"
        f"🏆 <b>ATH:</b> <code>${md.get('ath', {}).get('usd', 0):,.2f}</code>\n"
        f"📉 <b>From ATH:</b> <code>{md.get('ath_change_percentage', {}).get('usd', 0):.2f}%</code>\n\n"
        f"🏦 <b>Market Cap:</b> <code>${market_cap:,.0f}</code>\n"
        f"📊 <b>24h Vol:</b> <code>${volume_24h:,.0f}</code>\n\n"
        f"<a href='{channel_link}'>🔗 Join Channel</a>"
    )
     
    # get symbol for chart link
    symbol = data["symbol"].upper()
    tv_url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}USDT"

    kb = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📊 Chart", url=tv_url),
        InlineKeyboardButton("🔄 Refresh", callback_data=f"refresh:{cid}")
    ],
    [
        InlineKeyboardButton("❌ Close", callback_data="close")
    ]
   ])

    # EDIT (for refresh)
    if edit and update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=kb,
            parse_mode="HTML"
        )
        return

    # NORMAL SEND
    await update.message.reply_text(
        text,
        reply_markup=kb,
        parse_mode="HTML"
    )

# ================= CALLBACK =================
async def price_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data

    # CLOSE
    if data == "close":
        await q.message.delete()
        return

    # REFRESH
    if data.startswith("refresh:"):
        cid = data.split(":")[1]

        now = time.time()
        last = context.user_data.get("last_refresh", 0)

        if now - last < REFRESH_COOLDOWN:
            await q.answer("⚠️ Wait 7 sec...", show_alert=False)
            return

        context.user_data["last_refresh"] = now

        try:
            await send_price(update, context, cid, edit=True)
            await q.answer("✅ Refreshed", show_alert=False)
        except Exception as e:
            print("Refresh error:", e)
            await q.answer("⚠️ Error", show_alert=False)
            