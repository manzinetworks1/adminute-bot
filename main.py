import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import sqlite3
import asyncio

BOT_TOKEN = "8474064038:AAGp3XloJeNRMCLPFujAH36CJF8aMpOzACg"
ADMIN_ID = 647566363   # your admin ID
DEFAULT_TIMER_MIN = 3  # you can change this later

# --------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("ads.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            the_text TEXT,
            media TEXT,
            campaign_type TEXT,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# --------- Bot Commands ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to AdMinute! Send me your advertisement details.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/postad - Submit new ad\n/settimer - Change timer\n/latest - See last ads")

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DEFAULT_TIMER_MIN

    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("Only admin can change timer!")

    try:
        mins = int(context.args[0])
        DEFAULT_TIMER_MIN = mins
        await update.message.reply_text(f"Timer updated to {mins} minutes.")

    except:
        await update.message.reply_text("Usage: /settimer 5")

async def post_ad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    chat_id = update.message.chat_id

    conn = sqlite3.connect("ads.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (the_text, user_id, campaign_type) VALUES (?, ?, ?)",
              (text, user.id, "text"))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Your ad is saved.\nIt will post in {DEFAULT_TIMER_MIN} minutes!")

async def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("postad", post_ad))
    app.add_handler(CommandHandler("settimer", set_timer))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), post_ad))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
