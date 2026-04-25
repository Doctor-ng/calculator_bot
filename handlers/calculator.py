from telegram import Update
from telegram.ext import ContextTypes

from services.math_logic import process_math # type: ignore
from handlers.crypto import handle_crypto # type: ignore


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # -------- CRYPTO FIRST --------
    hit = await handle_crypto(update, context, text)

    if hit:
        return

    # -------- MATH --------
    result = await process_math(text)

    if result:
        await update.message.reply_text(
        result,
        parse_mode="HTML"
   )