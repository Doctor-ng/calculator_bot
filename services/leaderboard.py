# services/leaderboard.py

import html
import sqlite3
from datetime import datetime, timezone

DB_FILE = "bot.db"
VALID_CALCULATION_TYPES = {"math", "crypto"}


def get_db():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def _table_columns(cur):
    rows = cur.execute("PRAGMA table_info(calculation_leaderboard)").fetchall()
    return {row[1] for row in rows}


def init_leaderboard_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS calculation_leaderboard (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            calculation_count INTEGER NOT NULL DEFAULT 0,
            math_count INTEGER NOT NULL DEFAULT 0,
            crypto_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """
    )

    columns = _table_columns(cur)
    if "math_count" not in columns:
        cur.execute(
            "ALTER TABLE calculation_leaderboard "
            "ADD COLUMN math_count INTEGER NOT NULL DEFAULT 0"
        )
    if "crypto_count" not in columns:
        cur.execute(
            "ALTER TABLE calculation_leaderboard "
            "ADD COLUMN crypto_count INTEGER NOT NULL DEFAULT 0"
        )

    conn.commit()
    conn.close()


def record_calculation(user, calculation_type="math"):
    if not user:
        return

    if calculation_type not in VALID_CALCULATION_TYPES:
        calculation_type = "math"

    init_leaderboard_db()

    math_increment = 1 if calculation_type == "math" else 0
    crypto_increment = 1 if calculation_type == "crypto" else 0
    now = datetime.now(timezone.utc).isoformat()

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO calculation_leaderboard (
            user_id,
            username,
            first_name,
            calculation_count,
            math_count,
            crypto_count,
            updated_at
        )
        VALUES (?, ?, ?, 1, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            calculation_count=calculation_count + 1,
            math_count=math_count + excluded.math_count,
            crypto_count=crypto_count + excluded.crypto_count,
            updated_at=excluded.updated_at
        """,
        (
            user.id,
            user.username,
            user.first_name,
            math_increment,
            crypto_increment,
            now,
        ),
    )

    conn.commit()
    conn.close()


def _display_name(username, first_name, user_id):
    if username:
        return f"@{html.escape(username)}"

    if first_name:
        return html.escape(first_name)

    return f"User {user_id}"


def get_leaderboard(limit=10):
    init_leaderboard_db()

    conn = get_db()
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT user_id, username, first_name, calculation_count, math_count, crypto_count
        FROM calculation_leaderboard
        ORDER BY calculation_count DESC, updated_at ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    conn.close()
    return rows


def get_user_rank(user_id):
    init_leaderboard_db()

    conn = get_db()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT calculation_count, math_count, crypto_count
        FROM calculation_leaderboard
        WHERE user_id=?
        """,
        (user_id,),
    ).fetchone()

    if not row:
        conn.close()
        return None

    count, math_count, crypto_count = row
    rank = cur.execute(
        """
        SELECT COUNT(*) + 1
        FROM calculation_leaderboard
        WHERE calculation_count > ?
        """,
        (count,),
    ).fetchone()[0]

    conn.close()
    return {
        "rank": rank,
        "total": count,
        "math": math_count,
        "crypto": crypto_count,
    }


def format_leaderboard(rows, current_user=None):
    if not rows:
        return (
            "<b>🏆 Calculation Leaderboard</b>\n\n"
            "No calculations have been counted yet.\n"
            "Solve a math or crypto calculation to get started!"
        )

    medals = ["🥇", "🥈", "🥉"]
    text = "<b>🏆 Calculation Leaderboard</b>\n\n"

    for index, row in enumerate(rows, start=1):
        user_id, username, first_name, total, math_count, crypto_count = row
        prefix = medals[index - 1] if index <= len(medals) else f"{index}."
        name = _display_name(username, first_name, user_id)
        text += (
            f"{prefix} <b>{name}</b> — <code>{total}</code> total "
            f"(🧮 <code>{math_count}</code> | 🪙 <code>{crypto_count}</code>)\n"
        )

    if current_user:
        user_stats = get_user_rank(current_user.id)
        if user_stats:
            text += (
                f"\n<b>Your rank:</b> <code>#{user_stats['rank']}</code> "
                f"with <code>{user_stats['total']}</code> total "
                f"(🧮 <code>{user_stats['math']}</code> | "
                f"🪙 <code>{user_stats['crypto']}</code>)"
            )
        else:
            text += "\n<b>Your rank:</b> Make a calculation to join the board!"

    return text
