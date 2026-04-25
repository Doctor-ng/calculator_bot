from telegram import Update
from telegram.ext import ContextTypes

from services.crypto_logic import process_single_crypto # type: ignore


async def handle_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    res = await process_single_crypto(text)

    if not res:
        return False

    await update.message.reply_text(
        f"<b>{res['amount']} {res['symbol']} ({res['name']})</b>\n\n"
        f"💵 <code>${res['usd']:,.4f}</code>\n"
        f"🇮🇳 <code>₹{res['inr']:,.2f}</code>",
        parse_mode="HTML"
    )

    return True