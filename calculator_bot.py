# A Telegram bot that serves as a calculator for both mathematical expressions and cryptocurrency prices. It also includes features for setting price alerts and an admin panel for broadcasting messages to all users.
# By @DoctorEX0
# ================= IMPORTS =================
import sqlite3

from config import BOT_TOKEN, ADMIN_ID # type: ignore
from handlers.start import start, help_command # type: ignore
from handlers.calculator import calculate # type: ignore
from handlers.price import price_command, price_callbacks # type: ignore
from handlers.alerts import alert_command, myalerts, alert_callbacks# type: ignore
from handlers.inline import inline_query # type: ignore
from admin.admin import admin, admin_callbacks, handle_broadcast, cancel_broadcast # type: ignore


from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

<<<<<<< HEAD
# ================= CONFIG =================
BOT_TOKEN = "8558150692:AAHoYgdu8RtogjeB50wYnwfe83h4fn3IPpac" #Set Your Bot Token
ADMIN_ID = 5182907633 #Set Your Telegram ID


=======
>>>>>>> 864bc94 (update)
# ================= GROUP TRACK =================
import sqlite3

def get_db():
    return sqlite3.connect("bot.db", check_same_thread=False)

async def track_groups(update, context):
    if update.effective_chat.type in ("group", "supergroup"):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO groups VALUES (?)",
                    (update.effective_chat.id,))
        conn.commit()
        conn.close()
        
# ================= MAIN =================
async def post_init(application):
    pass

def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # ================= COMMAND HANDLERS =================
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("p", price_command))
    app.add_handler(CommandHandler("alert", alert_command))
    app.add_handler(CommandHandler("myalerts", myalerts))
    
    from telegram.ext import InlineQueryHandler
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(price_callbacks))

    # ================= CALLBACK HANDLERS =================
    app.add_handler(CallbackQueryHandler(
        price_callbacks,
        pattern="^(refresh:|close$)"
    ))

    app.add_handler(CallbackQueryHandler(
        admin_callbacks,
        pattern="^(bc_|restart_|close$)"
    ))
    
    app.add_handler(CallbackQueryHandler(
    alert_callbacks,
    pattern="^(delete_alert$)"
    ))
    
    # ================= ADMIN =================
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("cancel", cancel_broadcast))
    app.add_handler(CallbackQueryHandler(admin_callbacks, pattern="^(bc_|restart_|admin_|close)"))

    # ================= GROUP TRACK =================
    app.add_handler(
        MessageHandler(filters.StatusUpdate.ALL, track_groups)
    )

    # ================= MAIN MESSAGE FLOW =================

    # 🔥 PRIORITY 0 → Calculator (crypto + math)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, calculate),
        group=0
    )

    # 🔥 PRIORITY 1 → Broadcast (admin only)
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.User(ADMIN_ID) & ~filters.COMMAND,
            handle_broadcast
        ),
        group=1
    )

    # ================= RUN =================
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
