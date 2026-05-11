from telegram import Update
from telegram.ext import ContextTypes

from services.leaderboard import format_leaderboard, get_leaderboard # type: ignore


# ================= /leaderboard =================
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_leaderboard()
    text = format_leaderboard(rows, update.effective_user)

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )
