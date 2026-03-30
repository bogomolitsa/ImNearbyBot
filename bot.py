from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Главное меню
main_keyboard = [
    ["💔 Мне плохо"],
    ["📅 Помочь с делами"],
    ["📱 Я зависаю в телефоне"],
    ["💬 Просто поговорить"]
]
reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

# Меню "Мне плохо"
mood_keyboard = [
    ["😞 Грустно", "😣 Тревожно"],
    ["😔 Устал(а) / перегружен(а)", "😡 Всё бесит"],
    ["🔙 Назад"]
]
mood_markup = ReplyKeyboardMarkup(mood_keyboard, resize_keyboard=True)

# Подменю "Грустно"
sad_keyboard = [
    ["😞 Просто грустно", "💭 Зацикливаюсь на мыслях"],
    ["💤 Нет сил", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
]
sad_markup = ReplyKeyboardMarkup(sad_keyboard, resize_keyboard=True)

# Подменю "Тревожно"
anxiety_keyboard = [
    ["💭 Мысли не отпускают", "😰 Сильная тревога"],
    ["🌙 Не могу успокоиться", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
]
anxiety_markup = ReplyKeyboardMarkup(anxiety_keyboard, resize_keyboard=True)

# Подменю "Всё бесит"
anger_keyboard = [
    ["😤 Хочу выговориться", "🤬 Всё раздражает"],
    ["💥 Хочу выплеснуть эмоции", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
]
anger_markup = ReplyKeyboardMarkup(anger_keyboard, resize_keyboard=True)

# Подменю "Устал(а)"
tired_keyboard = [
    ["😵 Нет сил вообще", "📚 Слишком много всего"],
    ["🛌 Хочу просто отдохнуть", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
]
tired_markup = ReplyKeyboardMarkup(tired_keyboard, resize_keyboard=True)

tasks_keyboard = [
    ["📚 Много заданий", "😵 Не знаю с чего начать"],
    ["⏳ Ничего не успеваю", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
]

tasks_markup = ReplyKeyboardMarkup(tasks_keyboard, resize_keyboard=True)

phone_keyboard = [
    ["📱 Просто листаю", "⏳ Теряю много времени"],
    ["😵 Не могу оторваться", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
]

phone_markup = ReplyKeyboardMarkup(phone_keyboard, resize_keyboard=True)

# Минимальное меню (только назад)
minimal_keyboard = [
    ["🔙 Назад"]
]
minimal_markup = ReplyKeyboardMarkup(minimal_keyboard, resize_keyboard=True)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Поддержка, помощь с делами и немного спокойствия в шумной голове.\n"
        "Просто напиши — я рядом 🤍",
        reply_markup=reply_markup
    )

async def get_ai_response(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print(e)
        return "ошибка 🤍 смотри консоль"

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Назад
    if text == "🔙 Назад":
        await update.message.reply_text(
            "я рядом 🤍",
            reply_markup=reply_markup
        )
        return

    # Главное меню
    if text == "💔 Мне плохо":
        await update.message.reply_text(
            "я рядом 🤍\n"
            "что сейчас больше всего откликается?",
            reply_markup=mood_markup
        )

    elif text == "📅 Помочь с делами":
        await update.message.reply_text(
            "знакомое чувство, когда дел слишком много и всё наваливается сразу…\n"
            "давай разберёмся с этим без перегруза 🤍",
            reply_markup=tasks_markup
        )

    elif text == "📱 Я зависаю в телефоне":
        await update.message.reply_text(
            "знакомое состояние… иногда телефон просто затягивает\n"
            "хочешь попробовать немного это изменить без давления?",
            reply_markup=phone_markup
        )

    elif text == "💬 Просто поговорить":
        await update.message.reply_text(
            "я всегда тут)\n"
            "можешь написать всё, что хочешь и как оно есть, без фильтор и преукрас :)"
        )

    # "Мне плохо" → ветки
    elif text == "😞 Грустно":
        await update.message.reply_text(
            "хочешь попробовать чуть облегчить это состояние?\n"
            "можно начать с чего-то совсем простого — например, просто сделать паузу или немного отвлечься 🤍",
            reply_markup=sad_markup
        )

    elif text == "😣 Тревожно":
        await update.message.reply_text(
            "знакомое чувство, когда внутри всё напряжено и не отпускает…\n"
            "хочешь попробовать немного это разгрузить?",
            reply_markup=anxiety_markup
        )

    elif text == "😔 Устал(а) / перегружен(а)":
        await update.message.reply_text(
            "знакомое состояние, когда слишком много всего сразу…\n"
            "давай немного это разгрузим?",
            reply_markup=tired_markup
        )

    elif text == "😡 Всё бесит":
        await update.message.reply_text(
            "иногда правда всё начинает раздражать…\n"
            "хочешь немного это выпустить?",
            reply_markup=anger_markup
        )

    # Подменю "Грустно"
    elif text == "😞 Просто грустно":
        await update.message.reply_text(
            "иногда такие моменты просто накрывают…\n"
            "я рядом, если захочешь написать 🤍",
            reply_markup=minimal_markup
        )

    elif text == "💭 Зацикливаюсь на мыслях":
        await update.message.reply_text(
            "знакомое чувство, когда мысли крутятся по кругу…\n"
            "можешь попробовать просто выписать их сюда 🤍",
            reply_markup=minimal_markup
        )

    elif text == "💤 Нет сил":
        await update.message.reply_text(
            "похоже, ты сильно устал(а)…\n"
            "ты можешь не решать всё прямо сейчас\n"
            "давай просто проживём этот момент вместе 🤍",
            reply_markup=minimal_markup
        )

    elif text == "✍️ Хочу рассказать сам(а)":
        await update.message.reply_text(
            "я рядом и слушаю тебя 🤍",
            reply_markup=minimal_markup
        )

    # Тревога
    elif text == "😰 Сильная тревога":
        await update.message.reply_text(
            "сейчас может быть очень тяжело…\n"
            "ты можешь не справляться идеально\n"
            "давай просто побудем здесь вместе 🤍",
            reply_markup=minimal_markup
        )

    elif text == "🌙 Не могу успокоиться":
        await update.message.reply_text(
            "иногда тревога не даёт остановиться даже на минуту…\n"
            "можно попробовать медленный вдох и выдох\n"
            "я рядом 🤍",
            reply_markup=minimal_markup
        )

    # Злость
    elif text == "😤 Хочу выговориться":
        await update.message.reply_text(
            "можешь написать всё как есть, без фильтров\n"
            "я выдержу 🤍",
            reply_markup=minimal_markup
        )

    elif text == "🤬 Всё раздражает":
        await update.message.reply_text(
            "когда всё бесит подряд — это правда выматывает…\n"
            "можешь выплеснуть это сюда",
            reply_markup=minimal_markup
        )

    elif text == "💥 Хочу выплеснуть эмоции":
        await update.message.reply_text(
            "давай, выплесни это\n"
            "можно не сдерживаться здесь 🤍",
            reply_markup=minimal_markup
        )

    # Усталость
    elif text == "😵 Нет сил вообще":
        await update.message.reply_text(
            "похоже, ты на пределе…\n"
            "можно не делать ничего прямо сейчас\n"
            "это нормально 🤍",
            reply_markup=minimal_markup
        )

    elif text == "📚 Слишком много всего":
        await update.message.reply_text(
            "когда задач слишком много — это давит…\n"
            "давай разберём это по чуть-чуть 🤍",
            reply_markup=minimal_markup
        )

    elif text == "🛌 Хочу просто отдохнуть":
        await update.message.reply_text(
            "это очень понятное желание\n"
            "ты правда имеешь право на паузу 🤍",
            reply_markup=minimal_markup
        )

    elif text == "📚 Много заданий":
        await update.message.reply_text(
            "когда заданий много — это правда давит…\n"
            "давай попробуем выбрать что-то одно и начать с малого 🤍",
            reply_markup=minimal_markup
        )

    elif text == "😵 Не знаю с чего начать":
        await update.message.reply_text(
            "это очень знакомое состояние…\n"
            "можно просто назвать одно самое простое дело\n"
            "и начать с него 🤍",
            reply_markup=minimal_markup
        )

    elif text == "⏳ Ничего не успеваю":
        await update.message.reply_text(
            "ощущение, что времени не хватает, может сильно давить…\n"
            "ты можешь не успевать всё идеально\n"
            "это нормально 🤍",
            reply_markup=minimal_markup
        )

    elif text == "📱 Просто листаю":
        await update.message.reply_text(
            "иногда это просто способ немного отвлечься…\n"
            "можно не ругать себя за это 🤍",
            reply_markup=minimal_markup
        )

    elif text == "⏳ Теряю много времени":
        await update.message.reply_text(
            "когда время уходит незаметно — это может расстраивать…\n"
            "можно попробовать сделать маленькую паузу прямо сейчас 🤍",
            reply_markup=minimal_markup
        )

    elif text == "😵 Не могу оторваться":
        await update.message.reply_text(
            "это правда бывает сложно остановить…\n"
            "можно начать с очень маленького шага\n"
            "например, просто отложить телефон на пару минут 🤍",
            reply_markup=minimal_markup
        )

    else:
        ai_reply = await get_ai_response(text)
        await update.message.reply_text(ai_reply)

    # Запуск
def main():
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling(poll_interval=0.2, timeout=20)


if __name__ == "__main__":
    print("TOKEN:", TOKEN)
    main()