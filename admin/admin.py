from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config import ADMIN_ID  # type: ignore

# ===== ADMIN PANEL =====
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_menu")],
        [InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_confirm")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ])

    await update.message.reply_text(
        "<b>Admin Panel</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )


# ===== CALLBACKS =====
async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    user_id = q.from_user.id

    await q.answer()

    if user_id != ADMIN_ID:
        return

    # -------- BROADCAST MENU --------
    if data == "broadcast_menu":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 Users", callback_data="bc_users")],
            [InlineKeyboardButton("👥 Groups", callback_data="bc_groups")],
            [InlineKeyboardButton("🌍 All", callback_data="bc_all")],
            [InlineKeyboardButton("⬅ Back", callback_data="admin_back")]
        ])

        await q.message.edit_text(
            "<b>Select Broadcast Type</b>",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return

    # -------- BACK --------
    if data == "admin_back":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_menu")],
            [InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_confirm")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ])

        await q.message.edit_text(
            "<b>Admin Panel</b>",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return

    # -------- RESTART --------
    if data == "restart_confirm":
        await q.message.edit_text("♻️ Restarting...")
        import subprocess
        subprocess.Popen(["sudo", "systemctl", "restart", "calcbot"])
        return

    # -------- CLOSE --------
    if data == "close":
        await q.message.delete()


# ===== REGISTER =====
def register_admin(app):
    app.add_handler(CommandHandler("admin", admin))

    app.add_handler(
        CallbackQueryHandler(
            admin_callbacks,
            pattern="^(broadcast_menu|admin_back|restart_confirm|close)"
        )
    )