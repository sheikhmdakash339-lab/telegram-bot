import os
import sqlite3
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("8765015803:AAECeSOYfstfBTam0p_Jjaer7Jefum89yTM")
ADMIN_ID = 8113624729

# ---------- DATABASE ----------
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0,
    gmail_done INTEGER DEFAULT 0
)
""")
conn.commit()

def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_user(user_id):
    cur.execute("SELECT balance, referrals, gmail_done FROM users WHERE user_id=?", (user_id,))
    return cur.fetchone()

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    keyboard = [
        ["💰 ব্যালেন্স", "👥 রেফারেল"],
        ["📤 টাকা তুলুন", "📧 জিমেইল"]
    ]

    await update.message.reply_text(
        "👋 স্বাগতম!\nBot চালু আছে ✔️",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------- HANDLE ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    add_user(user_id)
    data = get_user(user_id)

    if not data:
        await update.message.reply_text("⚠️ আবার /start দিন")
        return

    balance, refs, gmail_done = data

    if text == "💰 ব্যালেন্স":
        await update.message.reply_text(f"💰 Balance: {balance}\n👥 Ref: {refs}")

    elif text == "👥 রেফারেল":
        link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        await update.message.reply_text(f"🔗 Referral link:\n{link}")

    elif text == "📧 জিমেইল":
        await update.message.reply_text("📧 Gmail system demo mode")

    elif text == "📤 টাকা তুলুন":
        await update.message.reply_text("⏳ Withdraw request received")

# ---------- RUN ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot running...")
app.run_polling()
