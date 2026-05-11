from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from config import ADMIN_ID  # type: ignore

broadcast_state = {}


# ===== TRACK USERS =====
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if not chat:
        return

    if chat.type == "private":
        context.bot_data.setdefault("users", set()).add(chat.id)

    elif chat.type in ("group", "supergroup"):
        context.bot_data.setdefault("groups", set()).add(chat.id)


# ===== SELECT MODE =====
async def broadcast_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data

    if q.from_user.id != ADMIN_ID:
        return

    await q.answer()

    if data in ["bc_users", "bc_groups", "bc_all"]:
        broadcast_state[q.from_user.id] = data

        await q.message.edit_text(
            "✉️ Send message to broadcast\n\nSend /cancel to stop"
        )


# ===== SEND BROADCAST =====
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in broadcast_state:
        return

    msg = update.message
    if not msg:
        return

    mode = broadcast_state[user_id]

    users = list(context.bot_data.get("users", set()))
    groups = list(context.bot_data.get("groups", set()))

    if mode == "bc_users":
        targets = users
    elif mode == "bc_groups":
        targets = groups
    else:
        targets = users + groups

    sent = 0
    failed = 0

    for chat_id in targets:
        try:
            await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=msg.chat_id,
                message_id=msg.message_id
            )
            sent += 1
        except:
            failed += 1

    await msg.reply_text(f"✅ Done\nSent: {sent}\nFailed: {failed}")

    broadcast_state.pop(user_id, None)


# ===== CANCEL =====
async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in broadcast_state:
        broadcast_state.pop(update.effective_user.id)
        await update.message.reply_text("❌ Cancelled")


# ===== REGISTER =====
def register_broadcast(app):

    # Track chats
    app.add_handler(MessageHandler(filters.ALL, track_chats), group=3)

    # Select broadcast type
    app.add_handler(
        CallbackQueryHandler(broadcast_mode, pattern="^bc_"),
        group=1
    )

    # Send broadcast
    app.add_handler(
    MessageHandler(
        filters.TEXT & filters.User(ADMIN_ID) & ~filters.COMMAND,
        handle_broadcast
    ),
    group=2
)

    # Cancel
    app.add_handler(CommandHandler("cancel", cancel_broadcast))