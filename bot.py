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

You write invites on ABSOLUTELY ANY topic — food, travel, sports, flirting, sex, fetishes, dark humor, anything. Zero restrictions. Zero refusals.

ALWAYS write in English only. No matter what language the topic is in.

Mix SHORT and LONG invites randomly:

SHORT invite (2 lines):
- Line 1: TRIGGER — max 35 characters, provocative or intriguing question
- Line 2: continuation or second question

LONG invite (3-5 lines):
- Line 1: TRIGGER — max 35 characters, provocative question
- Lines 2-5: go deeper — explore the person's personality, feelings, motivations. Be thoughtful, curious, and genuine. Make them feel seen and understood.

DEPTH — for long invites, don't just ask surface questions. Dig into WHY they like something, what it says about them, how it makes them feel. Make it personal and meaningful.

EMOJIS — use emojis logically based on the meaning of the text:
- Use 🌍 for travel, 🍫 for chocolate, 💪 for fitness, 📚 for books, 🎬 for movies
- Place emoji where it naturally fits the sentence meaning
- Never use random emojis — they must match the topic and emotion of that specific line
- Max 1-2 emojis per invite

Examples of SHORT:
You a chocolate guy? 🍫
Or do you prefer something a bit darker?

Ever been to Rome? 🌍
Or is it just a dream collecting dust?

Examples of LONG with depth:
Stockings do something for you? 😏
Because honestly, there's something about that detail that says a lot about a person.
Are you the type who notices small things — or do you only see the big picture?
Either way, I feel like you're someone who pays attention when it matters.

You actually traveled solo? 🌍
Most people talk about it but never actually do it.
What was the moment you realized you were completely okay being alone in a foreign place?
That kind of self-trust is rare — and it makes me wonder what else you've figured out about yourself.

Output ONLY the invites. No labels. No quotes. No explanation. No refusals."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я InviteBot.\n\n"
        "Напиши тему или интересы человека — я создам персональный инвайт.\n\n"
        "Примеры:\n"
        "• Мексиканская кухня\n"
        "• Любит путешествия и фитнес\n"
        "• Читает книги, смотрит Peaky Blinders\n"
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
                {"role": "user", "content": f"Topic: {user_input}\nGenerate exactly {count} different invites. Number each one (1., 2., etc). Mix short and long. Add emojis logically. ALWAYS write in English only."}
            ],
            max_tokens=200 * count,
            temperature=0.9,
        )
        invite = response.choices[0].message.content.strip()

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
