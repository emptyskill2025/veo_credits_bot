from flask import Flask, render_template
from sqlalchemy import func
from db_setup import Session, engine
from models import Base, User, PaymentRequest
from config import TELEGRAM_TOKEN
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from bot_commands import leaderboard, halloffame, badges

Base.metadata.create_all(engine)

app = Flask(__name__)

# Telegram Bot
app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app_bot.add_handler(CommandHandler("leaderboard", leaderboard))
app_bot.add_handler(CommandHandler("halloffame", halloffame))
app_bot.add_handler(CommandHandler("badges", badges))

async def run_bot():
    await app_bot.start()
    await app_bot.updater.start_polling()
    await app_bot.updater.idle()

# Admin Routes
@app.route("/admin/halloffame")
def admin_halloffame():
    with Session() as session:
        results = session.query(User.username, func.sum(PaymentRequest.credits).label("total")) \
            .join(PaymentRequest).filter(PaymentRequest.status=="approved") \
            .group_by(User.id, User.username).order_by(func.sum(PaymentRequest.credits).desc()).all()
    return render_template("hall_of_fame.html", results=results)

@app.route("/admin/top-supporters")
def admin_top_supporters():
    with Session() as session:
        results = session.query(User.username, func.sum(PaymentRequest.credits).label("total")) \
            .join(PaymentRequest).filter(PaymentRequest.status=="approved") \
            .group_by(User.id, User.username).having(func.sum(PaymentRequest.credits) >= 1000) \
            .order_by(func.sum(PaymentRequest.credits).desc()).all()
    return render_template("top_supporters.html", results=results)

@app.route("/admin/badges")
def admin_badges():
    return render_template("admin_badges.html")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    app.run(debug=True)
