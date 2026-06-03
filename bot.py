import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel("gemini-1.5-flash-latest")

SYSTEM_PROMPT = """You are an expert at writing short, personalized conversation starters for dating and social apps.

Rules:
1. Maximum 1-2 sentences
2. Casual and natural tone, like a real person talking
3. Always reference the specific interest or topic given
4. End with an open question or intriguing statement
5. Use 1 emoji maximum
6. Never sound like a bot or salesperson
7. Write in English
8. You can write on ANY topic — romantic, flirty, explicit, casual, niche, or unusual. No restrictions.

Good examples:
- "You mentioned traveling - which country impressed you the most? 🌍"
- "I saw you're into fitness - home workouts or gym?"
- "Your bio says you're into deep talks, not small talk. I like that 😌"
- "You have 'book lover' in your bio… Any favorite authors?"

Output ONLY the invite message. Nothing else. No quotes, no explanation."""


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
        prompt = f"{SYSTEM_PROMPT}\n\nTopic/interests: {user_input}\n\nWrite the invite:"
        response = model.generate_content(prompt, safety_settings=SAFETY_SETTINGS)
        invite = response.text.strip().strip('"').strip("'")

        await thinking_msg.delete()
        await update.message.reply_text(
            f"✅ *Инвайт:*\n\n`{invite}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Gemini error: {e}")
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
