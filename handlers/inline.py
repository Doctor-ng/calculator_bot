import uuid
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes

from services.crypto_logic import process_single_crypto # type: ignore
from services.math_logic import process_math # type: ignore

TOP_COINS = [
    ("btc", "Bitcoin"),
    ("eth", "Ethereum"),
    ("bnb", "BNB"),
    ("sol", "Solana"),
    ("xaut", "Tether Gold"),
]

COIN_IMAGES = {
    "btc": "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
    "eth": "https://cryptologos.cc/logos/ethereum-eth-logo.png",
    "bnb": "https://cryptologos.cc/logos/bnb-bnb-logo.png",
    "sol": "https://cryptologos.cc/logos/solana-sol-logo.png",
    "xaut": "https://cryptologos.cc/logos/tether-gold-xaut-logo.png",
}

# ✅ YOUR IMAGES
CRYPTO_IMG = "https://cryptologos.cc/logos/bitcoin-btc-logo.png"
MATH_IMG = "https://i.postimg.cc/Qd9fjByM/mathematics-space-theme-logo-76wefyazr4ip9mh3.png"

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().lower()
    results = []
    
    # ================= AUTO SUGGEST =================
    if not query:
        for symbol, name in TOP_COINS:
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"🪙 {symbol.upper()}",
                    description=name,
                    thumbnail_url=COIN_IMAGES.get(symbol),
                    input_message_content=InputTextMessageContent(
                        f"1 {symbol}"
                    )
                )
            )

        await update.inline_query.answer(results, cache_time=1)
        return
    
    # ================= PARTIAL MATCH =================
    for symbol, name in TOP_COINS:
        if query in symbol or query in name.lower():
            results.append(
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"🪙 {symbol.upper()}",
                    description=name,
                    thumbnail_url=COIN_IMAGES.get(symbol),
                    input_message_content=InputTextMessageContent(
                        f"1 {symbol}"
                    )
                )
            )

    # ================= CRYPTO =================
    res = await process_single_crypto(query)
    
    if res and not res.get("error"):
        text = (
            f"<b>{res['amount']} {res['symbol']} ({res['name']})</b>\n\n"
            f"💵 <code>${res['usd']:.4f}</code>\n"
            f"🇮🇳 <code>₹{res['inr']:.2f}</code>"
        )

        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="🪙 Crypto Result",
                description=f"${res['usd']:.4f} | ₹{res['inr']:.2f}",
                thumbnail_url=CRYPTO_IMG,  # ✅ image added
                input_message_content=InputTextMessageContent(
                    text,
                    parse_mode="HTML"
                )
            )
        )
        
    # ================= MATH =================
    math = await process_math(query)

    if math:
       clean_preview = math.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "")

       results.append(
         InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="🧮 Math Result",
            description=clean_preview,
            thumbnail_url=MATH_IMG,
            
    input_message_content=InputTextMessageContent(
            math,
            parse_mode="HTML"
          )
        )
    )

    # ================= SEND RESULTS =================
    await update.inline_query.answer(results, cache_time=1)