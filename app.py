# app.py
import os
import asyncio
from flask import Flask, render_template
from telegram.ext import ApplicationBuilder, CommandHandler
from bot_commands import leaderboard, halloffame, badges, payinfo
from payments import request_payment, approve_payment, reject_payment, list_pending_payments
from db_setup import Session as DBSession
from models import User

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "").split(",")))
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

# -----------------------------
# Flask Admin Routes
# -----------------------------
@app.route("/")
def home():
    return "✅ VEO Credits Bot Admin Panel is running."

@app.route("/admin/halloffame")
def admin_halloffame():
    with DBSession() as session:
        results = session.query(User.username, User.id).all()
    return render_template("hall_of_fame.html", results=results)

@app.route("/admin/top-supporters")
def admin_top_supporters():
    with DBSession() as session:
        results = session.query(User.username, User.id).all()
    return render_template("top_supporters.html", results=results)

@app.route("/admin/badges")
def admin_badges():
    return render_template("admin_badges.html")

# -----------------------------
# Telegram Bot Setup
# -----------------------------
async def start_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # User Commands
    app_bot.add_handler(CommandHandler("leaderboard", leaderboard))
    app_bot.add_handler(CommandHandler("halloffame", halloffame))
    app_bot.add_handler(CommandHandler("badges", badges))
    app_bot.add_handler(CommandHandler("payinfo", payinfo))

    async def pay(update, context):
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /pay <credits> <GCASH Reference>")
            return
        try:
            credits = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Credits must be a number.")
            return
        reference = context.args[1]
        with DBSession() as session:
            user = session.query(User).filter_by(id=update.effective_user.id).first()
            if not user:
                user = User(id=update.effective_user.id, username=update.effective_user.username)
                session.add(user)
                session.commit()
        msg = request_payment(update.effective_user.id, credits, reference)
        await update.message.reply_text(msg)

    async def admin_approve(update, context):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized.")
            return
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /approve <payment_id>")
            return
        payment_id = int(context.args[0])
        msg = approve_payment(payment_id)
        await update.message.reply_text(msg)

    async def admin_reject(update, context):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized.")
            return
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /reject <payment_id>")
            return
        payment_id = int(context.args[0])
        msg = reject_payment(payment_id)
        await update.message.reply_text(msg)

    async def pending(update, context):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ You are not authorized.")
            return
        pending_list = list_pending_payments()
        if not pending_list:
            await update.message.reply_text("No pending payments.")
            return
        msg = "📌 Pending Payments:\n"
        for p in pending_list:
            msg += f"ID: {p.id}, User: {p.user_id}, Credits: {p.credits}, Ref: {p.reference}\n"
        await update.message.reply_text(msg)

    # Admin Command Handlers
    app_bot.add_handler(CommandHandler("approve", admin_approve))
    app_bot.add_handler(CommandHandler("reject", admin_reject))
    app_bot.add_handler(CommandHandler("pending", pending))
    # User payment handler
    app_bot.add_handler(CommandHandler("pay", pay))

    await app_bot.run_polling()

# -----------------------------
# Run Flask + Telegram Bot
# -----------------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    app.run(host="0.0.0.0", port=PORT)
