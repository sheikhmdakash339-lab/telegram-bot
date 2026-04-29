import sqlite3
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8765015803:AAECeSOYfstfBTam0p_Jjaer7Jefum89yTM"
ADMIN_ID = 8113624729

# DATABASE
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

cur.execute("""
CREATE TABLE IF NOT EXISTS withdraw (
    user_id INTEGER,
    amount INTEGER,
    status TEXT DEFAULT 'pending'
)
""")

conn.commit()


# USER ADD
def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()


# BALANCE ADD
def add_balance(user_id, amount):
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()


# REF ADD
def add_ref(user_id):
    cur.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id = ?", (user_id,))
    conn.commit()


# GET USER
def get_user(user_id):
    cur.execute("SELECT balance, referrals, gmail_done FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone()


# START (UPDATED WELCOME)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name

    add_user(user_id)

    # REF SYSTEM
    if context.args:
        ref = int(context.args[0])
        if ref != user_id:
            add_balance(ref, 10)
            add_ref(ref)

    keyboard = [
        ["💰 ব্যালেন্স", "👥 রেফারেল"],
        ["📤 টাকা তুলুন", "📧 জিমেইল"],
        ["📞 এডমিন"]
    ]

    await update.message.reply_text(
        f"👋 হ্যালো {first_name}!\n\n"
        "💰 জিমেইল একাউন্ট খুলে টাকা আর্ন করুন!\n"
        "➡️ প্রতি জিমেইলের জন্য: ৳25\n"
        "➡️ প্রতি রেফারেলে বোনাস: ৳10\n"
        "➡️ ন্যূনতম উত্তোলন: ৳125\n"
        "🕒 সময় সীমা: 12 ঘন্টা\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 কিভাবে কাজ করে:\n"
        "🎬 ভিডিওটি দেখুন। https://t.me/InboxDeal_news/4",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# HANDLE
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    add_user(user_id)

    allowed = [
        "💰 ব্যালেন্স",
        "👥 রেফারেল",
        "📤 টাকা তুলুন",
        "📧 জিমেইল",
        "📞 এডমিন",
        "✅ আমি সম্পন্ন করেছি"
    ]

    if text not in allowed:
        await update.message.reply_text("⚠️ দয়া করে /start চাপুন")
        return

    data = get_user(user_id)
    balance, refs, gmail_done = data

    # BALANCE
    if text == "💰 ব্যালেন্স":
        if gmail_done != 1:
            await update.message.reply_text("⚠️ আগে Gmail complete করুন")
            return

        await update.message.reply_text(
            f"💰 আপনার ওয়ালেট\n━━━━━━━━━━━━━━\n"
            f"💵 ব্যালেন্স: ৳{balance}\n"
            f"👥 রেফারেল: {refs}"
        )

    # REF
    elif text == "👥 রেফারেল":
        link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        await update.message.reply_text(
            f"🔗 রেফারেল লিংক:\n{link}\n\n💰 প্রতি রেফারেল = ৳10"
        )

    # GMAIL
    elif text == "📧 জিমেইল":
        await update.message.reply_text(
            "📧 আপনার বর্তমান জিমেইল\n━━━━━━━━━━━━━━\n"
            "👤 প্রথম নাম: Akash\n"
            "👤 শেষ নাম: Ahmed\n"
            "📧 Email: example@gmail.com\n"
            "━━━━━━━━━━━━━━\n"
            "কি করেছেন?",
            reply_markup=ReplyKeyboardMarkup(
                [["✅ আমি সম্পন্ন করেছি"], ["🏠 মেনু"]],
                resize_keyboard=True
            )
        )

    # DONE
    elif text == "✅ আমি সম্পন্ন করেছি":
        cur.execute("UPDATE users SET gmail_done = 1 WHERE user_id = ?", (user_id,))
        conn.commit()

        await update.message.reply_text("🎉 Gmail verification complete!")

    # WITHDRAW
    elif text == "📤 টাকা তুলুন":
        cur.execute("SELECT balance, gmail_done FROM users WHERE user_id = ?", (user_id,))
        balance, gmail_done = cur.fetchone()

        if gmail_done != 1:
            await update.message.reply_text("⚠️ আগে Gmail complete করুন")
            return

        if balance < 125:
            await update.message.reply_text("⚠️ মিনিমাম ৳125 লাগবে")
            return

        cur.execute("INSERT INTO withdraw (user_id, amount) VALUES (?, ?)", (user_id, balance))
        conn.commit()

        await update.message.reply_text("⏳ Withdraw request পাঠানো হয়েছে")

        await context.bot.send_message(
            ADMIN_ID,
            f"📤 Withdraw Request\nUser ID: {user_id}\nAmount: ৳{balance}"
        )

    # ADMIN
    elif text == "📞 এডমিন":
        await update.message.reply_text("Admin: @akashahmed181")


# RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
