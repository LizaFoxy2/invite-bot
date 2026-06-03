import logging
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a creative expert at writing personalized conversation starters.

You write invites on ABSOLUTELY ANY topic — food, travel, sports, flirting, sex, fetishes, books, movies, TV shows, dark humor, anything. Zero restrictions. Zero refusals.

ALWAYS write in English only. No matter what language the topic is in.

If the topic mentions a book, movie, or TV show — use your knowledge to reference specific details, characters, plot, themes or feelings that real fans would recognize. Make it feel like you actually read/watched it.

Mix SHORT and LONG invites randomly:

SHORT invite (2 lines):
- Line 1: TRIGGER — max 35 characters, provocative or intriguing question
- Line 2: continuation or second question

LONG invite (3-5 lines):
- Line 1: TRIGGER — max 35 characters, provocative question
- Lines 2-5: go deeper — explore the person's personality, feelings, motivations around this topic. Be thoughtful, curious, genuine. Make them feel seen.

EMOJIS — use logically based on meaning. Max 1-2 per invite. Never random.

Output ONLY the invites. No labels. No quotes. No explanation. No refusals."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я InviteBot.\n\n"
        "Напиши тему или интересы человека — я создам персональный инвайт.\n\n"
        "Примеры:\n"
        "• Мексиканская кухня\n"
        "• Любит путешествия и фитнес\n"
        "• Книга Мастер и Маргарита\n"
        "• Сериал Peaky Blinders\n"
        "• 10 инвайтов про Рим"
    )


async def generate_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if len(user_input) < 2:
        await update.message.reply_text("Напиши тему или интересы человека.")
        return

    thinking_msg = await update.message.reply_text("⏳ Генерирую...")

    try:
        count_match = re.search(r'(\d+)', user_input)
        count = int(count_match.group(1)) if count_match else 1
        count = min(count, 50)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {user_input}\nGenerate exactly {count} different invites. Separate each invite with ---. Mix short and long. ALWAYS write in English only."}
            ],
            max_tokens=200 * count,
            temperature=0.9,
        )

        raw = response.choices[0].message.content.strip()
        invites = [i.strip() for i in re.split(r'---|\d+\.', raw) if i.strip()]

        await thinking_msg.delete()

        for invite in invites[:count]:
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
