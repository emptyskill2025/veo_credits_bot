# bot_commands.py
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, PaymentRequest
from db_setup import Session as DBSession

# -----------------------------
# Helper Functions
# -----------------------------
def get_badge(rank, total_credits):
    """Return badge emoji based on rank and total credits."""
    if rank == 1: 
        return "👑🥇"
    elif rank == 2: 
        return "🥈"
    elif rank == 3: 
        return "🥉"
    elif total_credits >= 1000: 
        return "💎"
    return ""

def format_user_entry(rank, username, total_credits):
    """Format user entry with rank, username, total credits, and badge."""
    badge = get_badge(rank, total_credits)
    if rank == 1:
        return f"⭐ <b>#1 {username} — {total_credits} credits {badge}</b>"
    elif rank == 2:
        return f"⚡ <b>#2 {username} — {total_credits} credits {badge}</b>"
    elif rank == 3:
        return f"🔥 <b>#3 {username} — {total_credits} credits {badge}</b>"
    elif total_credits >= 1000:
        return f"💎 #{rank} {username} — {total_credits} credits {badge}"
    else:
        return f"#{rank} {username} — {total_credits} credits"

# -----------------------------
# Telegram Command Handlers
# -----------------------------

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top 10 buyers leaderboard."""
    with DBSession() as session:
        # Get top 10 users by approved credits
        results = (
            session.query(User.username, func.sum(PaymentRequest.credits).label("total"))
            .join(PaymentRequest)
            .filter(PaymentRequest.status == "approved")
            .group_by(User.id)
            .order_by(func.sum(PaymentRequest.credits).desc())
            .limit(10)
            .all()
        )

        # Get full ranking to find user's rank
        ranked_users = (
            session.query(User.id, func.sum(PaymentRequest.credits).label("total"))
            .join(PaymentRequest)
            .filter(PaymentRequest.status == "approved")
            .group_by(User.id)
            .order_by(func.sum(PaymentRequest.credits).desc())
            .all()
        )

        user_rank, user_total = None, 0
        for idx, (uid, total) in enumerate(ranked_users, 1):
            if uid == update.effective_user.id:
                user_rank, user_total = idx, total
                break

    if not results:
        await update.message.reply_text("🏆 No buyers yet. Be the first!")
        return

    msg = "🏆 *Top Buyers Leaderboard*\n\n"
    for idx, (username, total) in enumerate(results, 1):
        msg += format_user_entry(idx, username or "Anonymous", total) + "\n"

    if user_rank:
        msg += f"\n⭐ You are ranked #{user_rank} with {user_total} credits"

    await update.message.reply_text(msg, parse_mode="HTML")


async def halloffame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all-time hall of fame."""
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
    """Show badge legend."""
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
