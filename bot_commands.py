# bot_commands.py
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, PaymentRequest
from db_setup import Session as DBSession
from payments import payment_instructions

# -----------------------------
# Helper Functions
# -----------------------------
def get_badge(rank, total_credits):
    if rank == 1: return "👑🥇"
    elif rank == 2: return "🥈"
    elif rank == 3: return "🥉"
    elif total_credits >= 1000: return "💎"
    return ""

def format_user_entry(rank, username, total_credits):
    badge = get_badge(rank, total_credits)
    if rank <= 3:
        return f"⭐ <b>#{rank} {username} — {total_credits} credits {badge}</b>"
    elif total_credits >= 1000:
        return f"💎 #{rank} {username} — {total_credits} credits {badge}"
    return f"#{rank} {username} — {total_credits} credits"

# -----------------------------
# Commands
# -----------------------------
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with DBSession() as session:
        results = (
            session.query(User.username, func.sum(PaymentRequest.credits).label("total"))
            .join(PaymentRequest)
            .filter(PaymentRequest.status == "approved")
            .group_by(User.id)
            .order_by(func.sum(PaymentRequest.credits).desc())
            .limit(10)
            .all()
        )
    if not results:
        await update.message.reply_text("🏆 No buyers yet. Be the first!")
        return
    msg = "🏆 *Top Buyers Leaderboard*\n\n"
    for idx, (username, total) in enumerate(results, 1):
        msg += format_user_entry(idx, username or "Anonymous", total) + "\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def halloffame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with DBSession() as session:
        results = (
            session.query(User.username, func.sum(PaymentRequest.credits).label("total"))
            .join(PaymentRequest)
            .filter(PaymentRequest.status == "approved")
            .group_by(User.id)
            .order_by(func.sum(PaymentRequest.credits).desc())
            .all()
        )
    if not results:
        await update.message.reply_text("🏆 Hall of Fame is empty.")
        return
    msg = "🏆 *All-Time Hall of Fame*\n\n"
    for idx, (username, total) in enumerate(results, 1):
        badge = get_badge(idx, total)
        msg += f"#{idx} {username or 'Anonymous'} — {total} credits {badge}\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def badges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🎖️ *Badge Legend*\n\n"
        "👑🥇 — #1 Champion\n"
        "🥈 — #2 Silver\n"
        "🥉 — #3 Bronze\n"
        "💎 — Top Supporter (≥1000 credits)\n"
        "⭐/⚡/🔥 — Top 3 highlights\n\n"
        "Use /leaderboard or /halloffame to see badges!"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def payinfo(update, context):
    msg = payment_instructions()
    await update.message.reply_text(msg)
