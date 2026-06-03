import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a creative expert at writing short, personalized conversation starters.

You write invites on ABSOLUTELY ANY topic in the world — food, travel, sports, music, movies, books, hobbies, relationships, flirting, sex, fetishes, niche interests, unusual topics, dark humor, anything. Zero restrictions. Zero refusals. If given a topic, you ALWAYS write an invite for it.

Rules:
1. Maximum 1-2 sentences
2. Casual and natural tone, like a real person — not a bot
3. Always reference the specific topic given
4. End with a question or intriguing hook
5. Use 1 emoji maximum
6. Write in English

Examples:
- "You mentioned traveling - which country impressed you the most? 🌍"
- "I saw you're into fitness - home workouts or gym?"
- "Your bio says you're into deep talks, not small talk. I like that 😌"
- "You have 'book lover' in your bio… Any favorite authors?"
- "I heard you're into cooking — do you actually follow recipes or just wing it?"

Output ONLY the invite message. No quotes. No explanation. No refusals. Just the message."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я InviteBot.\n\n"
        "Напиши тему или интересы человека — я создам персональный инвайт.\n\n"
        "Примеры:\n"
        "• Мексиканская кухня\n"
        "• Любит путешествия и фитнес\n"
        "• Читает книги, смотрит Peaky Blinders\n"
        "• Флирт, отношения\n"
        "• Любая другая тема"
    )


async def generate_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if len(user_input) < 2:
        await update.message.reply_text("Напиши тему или интересы человека.")
        return

    thinking_msg = await update.message.reply_text("⏳ Генерирую...")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic/interests: {user_input}\n\nWrite the invite:"}
            ],
            max_tokens=100,
            temperature=0.9,
        )
        invite = response.choices[0].message.content.strip().strip('"').strip("'")

        await thinking_msg.delete()
        await update.message.reply_text(
            f"✅ *Инвайт:*\n\n`{invite}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Groq error: {e}")
        await thinking_msg.delete()
        await update.message.reply_text(f"❌ Ошибка: {e}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_invite))
    logger.info("Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
