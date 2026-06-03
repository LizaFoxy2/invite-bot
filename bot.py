import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """You are an expert at writing short, personalized conversation starters for dating and social apps.

Rules:
1. Maximum 1-2 sentences
2. Casual and natural tone, like a real person
3. Reference the specific interest or topic given
4. End with an open question or intriguing statement
5. Use 1 emoji maximum
6. Never sound like a bot or salesperson
7. Write in English

Good examples:
- "You mentioned traveling - which country impressed you the most? 🌍"
- "I saw you're into fitness - home workouts or gym?"
- "Your bio says you're into deep talks, not small talk. I like that 😌"
- "You have 'book lover' in your bio… I love that. Any favorite authors?"

Output ONLY the invite message. Nothing else. No quotes, no explanation."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я InviteBot.\n\n"
        "Напиши тему или интересы человека — я создам персональный инвайт.\n\n"
        "Примеры запросов:\n"
        "• Мексиканская кухня\n"
        "• Любит путешествия и фитнес\n"
        "• Читает книги, смотрит Peaky Blinders\n"
        "• В био написано что ценит честность"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Как пользоваться:\n\n"
        "Просто напиши интересы или тему — бот сгенерирует инвайт.\n\n"
        "Можно писать:\n"
        "• На русском: *мексиканская кухня*\n"
        "• Подробно: *парень любит готовить, путешествует, смотрит аниме*\n"
        "• Кратко: *фитнес*\n\n"
        "Бот автоматически напишет инвайт на английском.",
        parse_mode="Markdown"
    )


async def generate_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if len(user_input) < 2:
        await update.message.reply_text("Напиши чуть подробнее — тему или интересы человека.")
        return

    thinking_msg = await update.message.reply_text("⏳ Генерирую...")

    try:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Topic/interests: {user_input}\n\n"
            f"Write the invite:"
        )
        response = model.generate_content(prompt)
        invite = response.text.strip().strip('"').strip("'")

        await thinking_msg.delete()
        await update.message.reply_text(
            f"✅ *Инвайт готов:*\n\n`{invite}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error generating invite: {e}")
        await thinking_msg.delete()
        await update.message.reply_text(
            "❌ Ошибка при генерации. Попробуй ещё раз или измени запрос."
        )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_invite))

    logger.info("Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
