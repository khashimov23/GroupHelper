import os
import logging
import asyncio
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.environ.get("BOT_TOKEN", "")

WELCOME_MESSAGES = [
    "👋 Xush kelibsiz, {name}! Guruhimizga xush kelibsiz!",
    "🎉 {name} qo'shildi! Salom, yangi do'st!",
    "🚀 {name} poyezdga chiqdi! Xush kelibsiz!",
    "👀 {name} kirib keldi. Salom!",
    "🌟 {name} — guruhimizning yangi yulduzi!",
]

GOODBYE_MESSAGES = [
    "👋 {name} ketdi. Xayr, ko'rishguncha!",
    "🚪 {name} chiqib ketdi. Eshik ochiq qoldi...",
    "😢 {name} bizni tark etdi. Qaytib keling!",
    "✈️ {name} uchib ketdi. Xayr!",
]

AUTO_DELETE_DELAY = 40  # sekundda


async def auto_delete(message, delay: int):
    """Xabarni ma'lum vaqtdan keyin o'chiradi."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.new_chat_members:
        return

    # Service xabarni o'chir
    try:
        await msg.delete()
    except Exception as e:
        logging.warning(f"Service msg delete failed: {e}")

    for member in msg.new_chat_members:
        if member.is_bot:
            continue

        name = member.mention_html()
        text = random.choice(WELCOME_MESSAGES).format(name=name)

        sent = await msg.chat.send_message(text, parse_mode="HTML")
        asyncio.create_task(auto_delete(sent, delay=AUTO_DELETE_DELAY))


async def handle_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.left_chat_member:
        return

    # Service xabarni o'chir
    try:
        await msg.delete()
    except Exception as e:
        logging.warning(f"Service msg delete failed: {e}")

    member = msg.left_chat_member
    if member.is_bot:
        return

    name = member.mention_html()
    text = random.choice(GOODBYE_MESSAGES).format(name=name)

    sent = await msg.chat.send_message(text, parse_mode="HTML")
    asyncio.create_task(auto_delete(sent, delay=AUTO_DELETE_DELAY))

SALOM_PATTERNS = [
    "ассалому алейкум",
    "ассаламу алайкум",
    "ассалому алайкум",
    "ассаламу алейкум",
    "assalomu alaykum",
    "assalomu aleykum",
    "salom aleykum",
    "salom alaykum",
    "салом алейкум",
    "salom",
    "салом",
]

SALOM_REPLIES = [
    "Ва алайкум ассалом, {name}! ☺️",
    "Валайкум ассалом, {name}! ☺️",
    "Va alaykum assalom, {name}! ☺️",
]

async def handle_salom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    text = msg.text.lower().strip()

    for pattern in SALOM_PATTERNS:
        if pattern in text:
            name = msg.from_user.mention_html()
            reply = random.choice(SALOM_REPLIES).format(name=name)
            await msg.reply_text(reply, parse_mode="HTML")
            return


def main():
    if not TOKEN:
        print("❌ BOT_TOKEN environment variable topilmadi!")
        return

    import asyncio

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member)
    )
    app.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_left_member)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_salom)
    )


    print("✅ Bot ishga tushdi!")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
