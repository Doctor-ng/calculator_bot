from telegram import Update
from telegram.ext import ContextTypes

from services.math_logic import process_math # type: ignore
from handlers.crypto import handle_crypto # type: ignore


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.lower().strip()
    words = text.split()
    
    if "prag" in text:
       await update.message.reply_text("Chutiya hai bhai!")
       return

    if "1 bmw" in text:
       await update.message.reply_text("1.5$ /Per Night 💦")
       return

    if "price" in text:
       await update.message.reply_text("Use /p btc")
       return

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