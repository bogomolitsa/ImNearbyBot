from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import asyncio
import  random
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

print("работает")

crisis_words = [
    "хочу умереть",
    "не хочу жить",
    "покончить с собой",
    "суицид",
    "убить себя",
    "я не справлюсь",
    "жить не хочется",
    "все бессмысленно",
    "лучше бы меня не было",
    "хочу исчезнуть"
]

def is_crisis(text):
    text = text.lower()
    return any(word in text for word in crisis_words)

# Главное меню
main_keyboard = [
    ["🤍 Мне сейчас непросто"],
    ["🆘 Помощь"]
]

reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

old_main_keyboard = [
    ["💔 Мне плохо"],
    ["📅 Помочь с делами"],
    ["📱 Я зависаю в телефоне"],
    ["💬 Просто поговорить"]
]
old_reply_markup = ReplyKeyboardMarkup(old_main_keyboard, resize_keyboard=True)

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

practice_keyboard = [
    ["🌿 Расслабиться", "🎯 Сконцентрироваться"],
    ["💨 Выдохнуть"],
    ["🔙 Назад"]
]

practice_markup = ReplyKeyboardMarkup(practice_keyboard, resize_keyboard=True)

# Минимальное меню (только назад)
minimal_keyboard = [
    ["🔙 Назад"]
]
minimal_markup = ReplyKeyboardMarkup(minimal_keyboard, resize_keyboard=True)

print("клавиатуры работают")

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
        return "к сожалению, я не могу помочь тебе с этим сейчас." \
               "если у тебя есть новые идеи - пропиши команду us"

async def crisis_response(update: Update):
    responses = [
        (
            "сейчас может быть очень тяжело\n"
            "ты не обязан(а) справляться с этим одному(одной)\n\n"

            "если есть возможность — попробуй написать кому-то из близких\n"
            "даже короткое сообщение уже шаг\n\n"

            "можно обратиться за поддержкой:\n"
            "📞 8-800-2000-122 — детский телефон доверия (РФ)\n"
            "📞 8-499-791-20-50 — психологическая помощь\n\n"

            "если становится хуже — важно не оставаться одному(одной)"
        ),

        (
            "я слышу, что тебе сейчас непросто\n\n"

            "попробуй немного замедлиться:\n"
            "сделай медленный вдох и выдох\n\n"

            "и, пожалуйста, свяжись с кем-то из людей рядом\n"
            "или обратись сюда:\n"
            "📞 8-800-2000-122\n\n"

            "поддержка есть, и ты можешь к ней обратиться"
        ),

        (
            "в такие моменты важно не оставаться наедине с этим\n\n"

            "если можешь — позвони или напиши кому-то из близких\n"
            "или обратись за помощью:\n"
            "📞 8-800-2000-122\n"
            "📞 8-499-791-20-50\n\n"

            "ты не должен(на) справляться с этим в одиночку"
        ),

        (
            "сейчас не нужно решать всё сразу\n"
            "достаточно просто пережить этот момент\n\n"

            "если есть возможность — будь рядом с кем-то\n"
            "или обратись за поддержкой:\n"
            "📞 8-800-2000-122\n\n"

            "помощь рядом, и к ней можно обратиться"
        )
    ]

    await update.message.reply_text(random.choice(responses))

    if is_crisis(text):
        await crisis_response(update)
        return

print("старт робит")

async def us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_animation(
        animation="https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyODF5YzF4amF2azIwaG9nOHdwcHJld3hnb3ZwY2UyMWJtZTdwYTlpeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/O1w2wSTriddUA/giphy.gif",
        caption=(
            "я рядом, чтобы немного разгрузить твою голову 🤍\n\n"
            "здесь ты можешь увидеть команды для бота\n"
            "/practice — техники для расслабления и полной перезагрузки\n"
            "/surprise — сюрприииз!\n"
            "/motivation — немного мотивации для тебя\n"
            "/pic — эстетика\n"
            "/picanimals — смотри, какие милашки!\n"
            "/new — будущие нововведения\n\n"
            "можешь просто написать мне, если не знаешь с чего начать"
            "если у тебяя есть новые идеи, обратись сюда - @superson11c"
        )
    )

async def surprise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [
        "ты не обязан(а) быть удобным для всех 🤍",
        "иногда ты держишься сильнее, чем сам(а) это замечаешь",
        "ты уже прошёл(ла) через многое — и это что-то значит",
        "можно не быть идеальным(ой), чтобы быть ценным(ой)",
        "даже в твоём «я устал(а)» есть огромная сила",
        "ты имеешь право просто быть, без объяснений",
        "не всё должно получаться с первого раза",
        "ты не отстаёшь, у тебя свой темп",
    ]

    await update.message.reply_text(random.choice(messages))

async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "давай немного позаботимся о тебе 🤍\nчто сейчас нужнее?",
        reply_markup=practice_markup
    )

async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [
        "не нужно делать идеально — достаточно начать",
        "маленький шаг — это уже движение вперёд",
        "ты можешь двигаться в своём темпе",
        "даже если сегодня мало — это всё равно что-то",
        "ты не ленишься, ты устаёшь — и это нормально",
        "иногда отдых — это тоже часть продуктивности",
        "сейчас не нужно всё, только следующий маленький шаг",
        "иногда ^все и сразу^ получается менее качественно, чем маленькие, но уверенные шаги"
    ]

    await update.message.reply_text(random.choice(messages))

async def picanimals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = [
        (
            "https://images.unsplash.com/photo-1518791841217-8f162f1e1131",
            "котик просто лежит и ничего не делает — и этого достаточно 🤍"
        ),
        (
            "https://images.unsplash.com/photo-1517423440428-a5a00ad493e8",
            "иногда можно просто быть, как этот пёс"
        ),
        (
            "https://images.unsplash.com/photo-1507149833265-60c372daea22",
            "животные не требуют от себя невозможного"
        ),
        (
            "https://images.unsplash.com/photo-1543852786-1cf6624b9987",
            "ты можешь быть мягким(ой) к себе"
        ),
        (
            "https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9",
            "иногда отдых — это самое важное"
        )
    ]

    img, text = random.choice(content)

    await update.message.reply_photo(
        photo=img,
        caption=text
    )

    await update.message.reply_text(random.choice(messages))

async def pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = [
        (
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
            "иногда тишина — это уже достаточно 🤍"
        ),
        (
            "https://images.unsplash.com/photo-1493244040629-496f6d136cc3",
            "мир не всегда спешит, и ты тоже можешь"
        ),
        (
            "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
            "есть моменты, где просто быть — уже достаточно"
        ),
        (
            "https://images.unsplash.com/photo-1518837695005-2083093ee35b",
            "ты не обязан(а) успевать всё сразу"
        ),
        (
            "https://images.unsplash.com/photo-1470770841072-f978cf4d019e",
            "даже пауза — это часть движения"
        )
    ]

    img, text = random.choice(content)

    await update.message.reply_photo(
        photo=img,
        caption=text
    )

    await update.message.reply_text(random.choice(messages))

async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "этот бот будет расти вместе с тобой 🤍\n\n"
        "в планах:\n"
        "— больше практик\n"
        "— больше советов\n"
        "— полная работоспособность ии"
    )

async def breathing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("давай попробуем вместе 🤍")

    # вдох
    await msg.edit_text("🌿 вдох...\n(1...2...3...4)")
    await asyncio.sleep(4)

    # задержка
    await msg.edit_text("⏸ держим...\n(1...2...3...4)")
    await asyncio.sleep(4)

    # выдох
    await msg.edit_text("💨 выдох...\n(1...2...3...4...5...6)")
    await asyncio.sleep(6)

    # завершение
    await msg.edit_text("🤍 ты справился(ась)\nможешь повторить, если захочешь")

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

    elif text == "🤍 Мне сейчас непросто":
        await update.message.reply_text(
            "здесь можно быть честным 🤍\nчто сейчас откликается?",
            reply_markup=old_reply_markup
        )

    # Главное меню
    elif text == "💔 Мне плохо":
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

    elif text == "🌿 Расслабиться":
        await update.message.reply_text(
            "давай попробуем снять напряжение 🤍\n\n"
            "сделай медленный вдох на 4 секунды\n"
            "задержи дыхание на 4\n"
            "и медленно выдохни на 6\n\n"
            "повтори это 3–5 раз\n"
            "я побуду с тобой"
        )

    elif text == "🎯 Сконцентрироваться":
        await update.message.reply_text(
            "давай мягко вернём фокус 🤍\n\n"
            "назови про себя:\n"
            "— 3 вещи, которые ты видишь\n"
            "— 2 вещи, которые ты слышишь\n"
            "— 1 вещь, которую ты чувствуешь телом\n\n"
            "это поможет немного заземлиться"
        )

    elif text == "💨 Выдохнуть":
        await breathing(update, context)

    else:
        ai_reply = await get_ai_response(text)
        await update.message.reply_text(ai_reply)

print("элифы работают")

    # Запуск
def main():
    print("HELLOOOOO!!!!")
    app = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("surprise", surprise))
    app.add_handler(CommandHandler("practice", practice))
    app.add_handler(CommandHandler("us", us))
    app.add_handler(CommandHandler("motivation", motivation))
    app.add_handler(CommandHandler("pic", pic))
    app.add_handler(CommandHandler("picanimals", picanimals))
    app.add_handler(CommandHandler("new", new))
    app = ApplicationBuilder().token(TOKEN).build()

    print("Бот запущен...")
    app.run_polling

    print("TOKEN:", TOKEN)
    main()