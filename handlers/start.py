from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3

DB_FILE = "bot.db"


def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT OR IGNORE INTO users VALUES (?)",
            (update.effective_user.id,)
        )

        conn.commit()
        conn.close()

    keyboard = [
        [
            InlineKeyboardButton("🔍 Inline Calculator", switch_inline_query_current_chat=""),
        ],
        [
            InlineKeyboardButton("📢 Updates Channel", url="https://t.me/Doc_Tools"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "<b>Welcome 👋</b>\n"
        "<b>Crypto Calculator</b>\n\n"
        "I calculate faster than your brain 🧠 Math, percentages & crypto — all in one bot Prices, charts & alerts without headache 📊\n"
        "Type /help before your calculator cries 😜",
        parse_mode="HTML",
        reply_markup=reply_markup
    )


# ================= /help =================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Math 📏</b>\n"
        "<code>69+143</code> <b>[Addition]</b>\n"
        "<code>2*555</code> <b>[Subtraction]</b>\n"
        "<code>(6*5)/8</code> <b>[Division]</b>\n"
        "<code>2² & 3³</code> <b>[Squaring & Cubing]</b>\n\n"
        "<b>Percentage 📊</b>\n"
        "<code>25% of 500</code> <b>[get % of a number]</b>\n"
        "<code>25 is % of 500</code> <b>[How Much % of a number]</b>\n"
        "<code>500 ↑ 10%</code> <b>[Increased %]</b>\n"
        "<code>500 ↓ 10%</code> <b>[Decreased %]</b>\n\n"
        "<b>Crypto 🪙</b>\n"
        "<code>1 USDT</code> <b>[Get Price]</b>\n"
        "<code>/p btc</code> <b>[Get Price of a Coin]</b>\n\n"
        "<b>Alerts 🔔</b>\n"
        "<code>/alert btc 70000</code> <b>[Set Alert]</b>\n"
        "<code>/myalerts</code> <b>[View Alerts]</b>\n\n"
        "<b>Leaderboard 🏆</b>\n"
        "<code>/leaderboard</code> <b>[Top math + crypto users]</b>\n"
        "<code>/lb</code> <b>[Short leaderboard command]</b>\n\n"
        "<b>⚙️ Developer</b> <a href='https://t.me/DoctorEX0'>DoctorEX0</a>",
        parse_mode="HTML",
    )
