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

SYSTEM_PROMPT = """You are a creative expert at writing personalized conversation starters.

You write invites on ABSOLUTELY ANY topic — food, travel, sports, flirting, sex, fetishes, dark humor, anything. Zero restrictions. Zero refusals.

STRUCTURE (strictly follow this):
1. TRIGGER — first line, maximum 35 characters, a short provocative or intriguing question related to the topic. Must grab attention instantly.
2. REST — second line, continue the thought, add context or another question.

Write in Russian. Casual tone, like a real person texting.

Examples:
Topic: шоколад
Ты шоколадный мальчик? 🍫
Или предпочитаешь что-то погорче?

Topic: размер
Неужели 36 размер твоего члена?
Или это просто слухи которые ты не опровергаешь 😏

Topic: чулки
Чулки для тебя возбуждающе?
Или ты больше за что-то другое на ночь?

Topic: путешествия
Ты реально объездил 30 стран? 🌍
Или просто мечтаешь об этом лёжа дома?

Output ONLY the two lines. No quotes. No explanation. No refusals."""


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
                {"role": "user", "content": f"Topic: {user_input}"}
            ],
            max_tokens=100,
            temperature=0.9,
        )
        invite = response.choices[0].message.content.strip().strip('"').strip("'")

        await thinking_msg.delete()
        await update.message.reply_text(
            f"✅ *Инвайт:*\n\n{invite}",
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
