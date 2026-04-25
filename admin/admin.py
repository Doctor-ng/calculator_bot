from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import ADMIN_ID  # type: ignore
import subprocess

# ===== TEMP STORAGE =====
broadcast_state = {}


# ================= TRACK USERS & GROUPS =================
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if not chat:
        return

    if chat.type == "private":
        users = context.bot_data.setdefault("users", set())
        users.add(chat.id)

    elif chat.type in ("group", "supergroup"):
        groups = context.bot_data.setdefault("groups", set())
        groups.add(chat.id)


# ================= ADMIN PANEL =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if update.effective_chat.type != "private":
        return

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast Users", callback_data="bc_users")],
        [InlineKeyboardButton("👥 Broadcast Groups", callback_data="bc_groups")],
        [InlineKeyboardButton("🌍 Broadcast All", callback_data="bc_all")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_confirm")],
        [InlineKeyboardButton("❌ Close", callback_data="close")],
    ])

    await update.message.reply_text(
        "<b>Admin Panel</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )


# ================= CALLBACKS =================
async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # ---- BROADCAST MODES ----
    if data == "bc_users":
        broadcast_state[q.from_user.id] = "users"
        await q.message.edit_text("✉️ Send message to broadcast (Users)\n\nSend /cancel to stop")
        return

    if data == "bc_groups":
        broadcast_state[q.from_user.id] = "groups"
        await q.message.edit_text("✉️ Send message to broadcast (Groups)\n\nSend /cancel to stop")
        return

    if data == "bc_all":
        broadcast_state[q.from_user.id] = "all"
        await q.message.edit_text("✉️ Send message to broadcast (All)\n\nSend /cancel to stop")
        return

    # ---- RESTART CONFIRM ----
    if data == "restart_confirm":
        if q.from_user.id != ADMIN_ID:
            return

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data="restart_bot"),
                InlineKeyboardButton("⬅️ Back", callback_data="admin_back")
            ]
        ])

        await q.message.edit_text(
            "⚠️ <b>Restart bot?</b>",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return

    # ---- BACK ----
    if data == "admin_back":
        await admin(update, context)
        return

    # ---- RESTART ----
    if data == "restart_bot":
        if q.from_user.id != ADMIN_ID:
            return

        await q.message.edit_text("♻️ Restarting...")
        subprocess.Popen(["sudo", "systemctl", "restart", "calcbot"])
        return

    # ---- CLOSE ----
    if data == "close":
        await q.message.delete()
        return


# ================= BROADCAST =================
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in broadcast_state:
        return

    message = update.message
    if not message:
        return

    mode = broadcast_state[user_id]

    users = list(context.bot_data.get("users", set()))
    groups = list(context.bot_data.get("groups", set()))

    if mode == "users":
        targets = users
    elif mode == "groups":
        targets = groups
    else:
        targets = users + groups

    sent = 0
    failed = 0

    for chat_id in targets:
        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=update.effective_chat.id,
                message_id=message.message_id
            )
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ Broadcast done\n\nSent: {sent}\nFailed: {failed}"
    )

    broadcast_state.pop(user_id, None)


# ================= CANCEL =================
async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in broadcast_state:
        broadcast_state.pop(user_id)
        await update.message.reply_text("❌ Broadcast cancelled")


# ================= REGISTER =================
def register_admin(app):

    # ---- TRACK FIRST (VERY IMPORTANT) ----
    app.add_handler(MessageHandler(filters.ALL, track_chats), group=0)

    # ---- ADMIN ----
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(admin_callbacks))

    # ---- BROADCAST ----
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast),
        group=1
    )

    # ---- CANCEL ----
    app.add_handler(CommandHandler("cancel", cancel_broadcast))