from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3

from services.crypto_logic import get_coin_id # type: ignore


DB_FILE = "bot.db"


# ================= DB =================
def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


# ================= /alert =================
async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "<b>ℹ️ Use:</b>\n\n"
            "<code>/alert btc 70000</code>",
            parse_mode="HTML"
        )
        return

    if len(context.args) != 2:
        await update.message.reply_text(
            "<b>❌ Invalid format</b>\n"
            "<code>/alert btc 70000</code>",
            parse_mode="HTML"
        )
        return

    symbol, target = context.args

    try:
        target = float(target)
    except ValueError:
        await update.message.reply_text("<b>❌ Price must be number</b>", parse_mode="HTML")
        return

    cid = await get_coin_id(symbol)
    if not cid:
        await update.message.reply_text("<b>❌ Coin not found</b>", parse_mode="HTML")
        return

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO alerts (user_id, coin_id, target) VALUES (?,?,?)",
        (update.effective_user.id, cid, target)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"🔔 <b>Alert set</b>\n"
        f"<b>{symbol.upper()}</b> → <code>${target}</code>",
        parse_mode="HTML"
    )


# ================= /myalerts =================
async def myalerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT coin_id, target FROM alerts WHERE user_id=?",
        (update.effective_user.id,)
    ).fetchall()

    conn.close()

    if not rows:
        await update.message.reply_text(
            "<b>📭 No alerts</b>",
            parse_mode="HTML"
        )
        return

    text = "<b>🔔 Your Alerts</b>\n\n"
    for i, (cid, target) in enumerate(rows, start=1):
        text += f"{i}. <b>{cid.upper()}</b> → <code>${target}</code>\n"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Delete Alert", callback_data="delete_alert")]
    ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=kb
    )


# ================= CALLBACK =================
async def alert_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data

    if data == "delete_alert":
        context.user_data["delete_mode"] = True
        await q.message.reply_text(
            "<b>Send alert number to delete</b>",
            parse_mode="HTML"
        )
        await q.answer()
        return


# ================= DELETE HANDLER =================
async def delete_alert_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("delete_mode"):
        return False

    text = update.message.text

    if not text.isdigit():
        await update.message.reply_text("<b>❌ Send valid number</b>", parse_mode="HTML")
        return True

    index = int(text)

    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT coin_id, target FROM alerts WHERE user_id=?",
        (update.effective_user.id,)
    ).fetchall()

    if 1 <= index <= len(rows):
        cid, target = rows[index - 1]

        cur.execute(
            "DELETE FROM alerts WHERE user_id=? AND coin_id=? AND target=?",
            (update.effective_user.id, cid, target)
        )
        conn.commit()

        await update.message.reply_text(
            "<b>✅ Alert deleted</b>",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            "<b>❌ Invalid number</b>",
            parse_mode="HTML"
        )

    conn.close()
    context.user_data.pop("delete_mode", None)
    return True