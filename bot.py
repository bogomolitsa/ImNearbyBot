# === ИМПОРТЫ ===
from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os, asyncio, random, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# === SERVER ===
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

# === TOKENS ===
TOKEN = os.getenv("TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === CRISIS ===
crisis_words = [
    "хочу умереть","не хочу жить","покончить с собой","суицид",
    "убить себя","жить не хочется","все бессмысленно","хочу исчезнуть"
]

def is_crisis(text):
    return any(word in text.lower() for word in crisis_words)

async def crisis_response(update):
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
            "📞 8-800-2000-122 — детский телефон доверия (РФ)\n"
            "📞 8-499-791-20-50 — психологическая помощь\\nn"

            "поддержка есть, и ты можешь к ней обратиться"
        ),

        (
            "в такие моменты важно не оставаться наедине с этим\n\n"

            "если можешь — позвони или напиши кому-то из близких\n"
            "или обратись за помощью:\n"
            "📞 8-800-2000-122 — детский телефон доверия (РФ)\n"
            "📞 8-499-791-20-50 — психологическая помощь\\nn"

            "ты не должен(на) справляться с этим в одиночку"
        ),

        (
            "сейчас не нужно решать всё сразу\n"
            "достаточно просто пережить этот момент\n\n"

            "если есть возможность — будь рядом с кем-то\n"
            "или обратись за поддержкой:\n"
            "📞 8-800-2000-122 — детский телефон доверия (РФ)\n"
            "📞 8-499-791-20-50 — психологическая помощь\\nn"


            "помощь рядом, и к ней можно обратиться"
        )
    ]

    await update.message.reply_text(random.choice(responses))


# === КЛАВИАТУРЫ ===
main_kb = ReplyKeyboardMarkup([["🤍 Мне сейчас непросто"],["🆘 Помощь"]], resize_keyboard=True)

old_kb = ReplyKeyboardMarkup([
    ["💔 Мне плохо"],
    ["📅 Помочь с делами"],
    ["📱 Я зависаю в телефоне"],
    ["💬 Просто поговорить"]
], resize_keyboard=True)

mood_kb = ReplyKeyboardMarkup([
    ["😞 Грустно","😣 Тревожно"],
    ["😔 Устал(а) / перегружен(а)","😡 Всё бесит"],
    ["🔙 Назад"]
], resize_keyboard=True)


# Подменю "Грустно"
sad_kb = ReplyKeyboardMarkup( [
    ["😞 Просто грустно", "💭 Зацикливаюсь на мыслях"],
    ["💤 Нет сил", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
], resize_keyboard=True)

# Подменю "Тревожно"
anxiety_kb = ReplyKeyboardMarkup( [
    ["💭 Мысли не отпускают", "😰 Сильная тревога"],
    ["🌙 Не могу успокоиться", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
], resize_keyboard=True)

# Подменю "Всё бесит"
anger_kb = ReplyKeyboardMarkup( [
    ["😤 Хочу выговориться", "🤬 Всё раздражает"],
    ["💥 Хочу выплеснуть эмоции", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
], resize_keyboard=True)

# Подменю "Устал(а)"
tired_kb = ReplyKeyboardMarkup( [
    ["😵 Нет сил вообще", "📚 Слишком много всего"],
    ["🛌 Хочу просто отдохнуть", "✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
], resize_keyboard=True)


tasks_kb = ReplyKeyboardMarkup([
    ["📚 Много заданий","😵 Не знаю с чего начать"],
    ["⏳ Ничего не успеваю","✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
], resize_keyboard=True)

phone_kb = ReplyKeyboardMarkup([
    ["📱 Просто листаю","⏳ Теряю время"],
    ["😵 Не могу оторваться","✍️ Хочу рассказать сам(а)"],
    ["🔙 Назад"]
], resize_keyboard=True)

practice_kb = ReplyKeyboardMarkup([
    ["🌿 Расслабиться","🎯 Сконцентрироваться"],
    ["💨 Выдохнуть"],["🔙 Назад"]
], resize_keyboard=True)



# === AI ===
async def get_ai(text):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":text}]
        )
        return r.choices[0].message.content
    except:
        return "я рядом 🤍"

# === КОМАНДЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Поддержка, помощь с делами и немного спокойствия в шумной голове.\n"
        "Просто напиши — я рядом 🤍", reply_markup=main_kb)

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
        ))

async def surprise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice([
        "ты не обязан(а) быть удобным для всех 🤍",
        "иногда ты держишься сильнее, чем сам(а) это замечаешь",
        "ты уже прошёл(ла) через многое — и это что-то значит",
        "можно не быть идеальным(ой), чтобы быть ценным(ой)",
        "даже в твоём «я устал(а)» есть огромная сила",
        "ты имеешь право просто быть, без объяснений",
        "не всё должно получаться с первого раза",
        "ты не отстаёшь, у тебя свой темп",
    ]))

async def practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("давай немного позаботимся о тебе 🤍\nчто сейчас нужнее?", reply_markup=practice_kb)

async def motivation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice([
        "не нужно делать идеально — достаточно начать",
        "маленький шаг — это уже движение вперёд",
        "ты можешь двигаться в своём темпе",
        "даже если сегодня мало — это всё равно что-то",
        "ты не ленишься, ты устаёшь — и это нормально",
        "иногда отдых — это тоже часть продуктивности",
        "сейчас не нужно всё, только следующий маленький шаг",
        "иногда 'все и сразу' получается менее качественно, чем маленькие, но уверенные шаги"
    ]))

async def pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = [
        ("https://images.unsplash.com/photo-1506744038136-46273834b3fb","иногда тишина — это уже достаточно 🤍"),
        ("https://images.unsplash.com/photo-1493244040629-496f6d136cc3","мир не всегда спешит, и ты тоже можешь"),
        ("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee","есть моменты, где просто быть — уже достаточно"),
        ("https://images.unsplash.com/photo-1518837695005-2083093ee35b","ты не обязан(а) успевать всё сразу"),
        ("https://images.unsplash.com/photo-1470770841072-f978cf4d019e","даже пауза — это часть движения")
    ]
    img, txt = random.choice(content)
    await update.message.reply_photo(photo=img, caption=txt)

async def picanimals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content = [
        ("https://images.unsplash.com/photo-1518791841217-8f162f1e1131","котик просто лежит и ничего не делает — и этого достаточно 🤍"),
        ("https://images.unsplash.com/photo-1517423440428-a5a00ad493e8","иногда можно просто быть, как этот пёс"),
        ("https://images.unsplash.com/photo-1507149833265-60c372daea22","животные не требуют от себя невозможного"),
        ("https://images.unsplash.com/photo-1543852786-1cf6624b9987","ты можешь быть мягким(ой) к себе"),
        ("https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9","иногда отдых — это самое важное")
    ]
    img, txt = random.choice(content)
    await update.message.reply_photo(photo=img, caption=txt)

async def new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("этот бот будет расти вместе с тобой 🤍\n\n"
        "в планах:\n"
        "— больше практик\n"
        "— больше советов\n"
        "— полная работоспособность ии")

# === ДЫХАНИЕ ===
async def breathing(update):
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

# === ГЛАВНАЯ ЛОГИКА ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if is_crisis(text):
        await crisis_response(update)
        return

    if text == "🔙 Назад":
        await update.message.reply_text(
            "можешь выбрать, что сейчас ближе 🤍",
            reply_markup=main_kb
        )
        return

    elif text == "🤍 Мне сейчас непросто":
        await update.message.reply_text("здесь можно быть честным 🤍\n"
        "что сейчас откликается?", reply_markup=old_kb)

    elif text == "💔 Мне плохо":
        await update.message.reply_text("я рядом 🤍\n"
            "что сейчас больше всего откликается?", reply_markup=mood_kb)

    elif text == "📅 Помочь с делами":
        await update.message.reply_text("знакомое чувство, когда дел слишком много и всё наваливается сразу…\n"
            "давай разберёмся с этим без перегруза 🤍", reply_markup=tasks_kb)

    elif text == "📱 Я зависаю в телефоне":
        await update.message.reply_text("знакомое состояние… иногда телефон просто затягивает\n"
            "хочешь попробовать немного это изменить без давления?", reply_markup=phone_kb)

    elif text == "💬 Просто поговорить":
        await update.message.reply_text("я всегда тут)🤍\n"
            "можешь написать всё, что хочешь и как оно есть, без фильтров и преукрас :)")


    # "Мне плохо" → ветки
    elif text == "😞 Грустно":
        await update.message.reply_text("хочешь попробовать чуть облегчить это состояние?\n"
            "можно начать с чего-то совсем простого — например, просто сделать паузу или немного отвлечься 🤍",)

    elif text == "😣 Тревожно":
        await update.message.reply_text("знакомое чувство, когда внутри всё напряжено и не отпускает…\n"
            "хочешь попробовать немного это разгрузить?")

    elif text == "😔 Устал(а) / перегружен(а)":
        await update.message.reply_text("знакомое состояние, когда слишком много всего сразу…\n"
            "давай немного это разгрузить")

    elif text == "😡 Всё бесит":
        await update.message.reply_text("иногда правда всё начинает раздражать…\n"
            "хочешь немного это выпустить?")

    # Подменю "Грустно"
    elif text == "😞 Просто грустно":
        await update.message.reply_text("иногда такие моменты просто накрывают…\n"
            "я рядом, если захочешь написать 🤍")

    elif text == "💭 Зацикливаюсь на мыслях":
        await update.message.reply_text("знакомое чувство, когда мысли крутятся по кругу…\n"
            "можешь попробовать просто выписать их сюда 🤍")

    elif text == "💤 Нет сил":
        await update.message.reply_text("похоже, ты сильно устал(а)…\n"
            "ты можешь не решать всё прямо сейчас\n"
            "давай просто проживём этот момент вместе 🤍")

    elif text == "✍️ Хочу рассказать сам(а)":
        await update.message.reply_text("я рядом и слушаю тебя 🤍")

    # Тревога
    elif text == "😰 Сильная тревога":
        await update.message.reply_text("сейчас может быть очень тяжело…\n"
            "ты можешь не справляться идеально\n"
            "давай просто побудем здесь вместе 🤍"
        )

    elif text == "🌙 Не могу успокоиться":
        await update.message.reply_text("иногда тревога не даёт остановиться даже на минуту…\n"
            "можно попробовать медленный вдох и выдох\n"
            "я рядом 🤍")

    # Злость
    elif text == "😤 Хочу выговориться":
        await update.message.reply_text("можешь написать всё как есть, без фильтров\n"
            "я выдержу 🤍")

    elif text == "🤬 Всё раздражает":
        await update.message.reply_text("когда всё бесит подряд — это правда выматывает…\n"
            "можешь выплеснуть это сюда")

    elif text == "💥 Хочу выплеснуть эмоции":
        await update.message.reply_text("давай, выплесни это\n"
            "можно не сдерживаться здесь 🤍")

    # Усталость
    elif text == "😵 Нет сил вообще":
        await update.message.reply_text("похоже, ты на пределе…\n"
            "можно не делать ничего прямо сейчас\n"
            "это нормально 🤍")

    elif text == "📚 Слишком много всего":
        await update.message.reply_text("когда задач слишком много — это давит…\n"
            "давай разберём это по чуть-чуть 🤍")

    elif text == "🛌 Хочу просто отдохнуть":
        await update.message.reply_text("это очень понятное желание\n"
            "ты правда имеешь право на паузу 🤍")

    elif text == "📚 Много заданий":
        await update.message.reply_text("когда заданий много — это правда давит…\n"
            "давай попробуем выбрать что-то одно и начать с малого 🤍")

    elif text == "😵 Не знаю с чего начать":
        await update.message.reply_text("это очень знакомое состояние…\n"
            "можно просто назвать одно самое простое дело\n"
            "и начать с него 🤍")

    elif text == "⏳ Ничего не успеваю":
        await update.message.reply_text("ощущение, что времени не хватает, может сильно давить…\n"
            "ты можешь не успевать всё идеально\n"
            "это нормально 🤍")

    elif text == "📱 Просто листаю":
        await update.message.reply_text("иногда это просто способ немного отвлечься…\n"
            "можно не ругать себя за это 🤍")

    elif text == "⏳ Теряю много времени":
        await update.message.reply_text("когда время уходит незаметно — это может расстраивать…\n"
            "можно попробовать сделать маленькую паузу прямо сейчас 🤍")

    elif text == "😵 Не могу оторваться":
        await update.message.reply_text("это правда бывает сложно остановить…\n"
            "можно начать с очень маленького шага\n"
            "например, просто отложить телефон на пару минут 🤍")

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()

        # Обработка кнопки "Помощь"
    if text == "🆘 Помощь":
        await update.message.reply_text("Что-ты подробнее разобраться в том, что умеет бот введи команду /us. по всем вопросам бота ты всегда можешь обратиться @superson11c."
            "если ты на грани, пожалуйста обратись к близким людям или сюда за помощью:\n"
            "📞 8-800-2000-122 — детский телефон доверия (РФ)\n"
            "📞 8-499-791-20-50 — психологическая помощь\\nn"
            "поддержка есть, и ты можешь к ней обратиться")

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
        await breathing(update)

    else:
        await update.message.reply_text(await get_ai(text))

# === MAIN ===
def main():
    print("START")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("us", us))
    app.add_handler(CommandHandler("new", new))
    app.add_handler(CommandHandler("surprise", surprise))
    app.add_handler(CommandHandler("practice", practice))
    app.add_handler(CommandHandler("motivation", motivation))
    app.add_handler(CommandHandler("pic", pic))
    app.add_handler(CommandHandler("picanimals", picanimals))
    app.add_handler(CommandHandler("new", new))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()