import telebot
from telebot import types
import json

# ========================
# 🔐 ТОКЕН ИЗ ФАЙЛА
# ========================
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

bot = telebot.TeleBot(TOKEN)

# ========================
# 📂 ЗАГРУЗКА БД
# ========================
with open("schedule.json", "r", encoding="utf-8") as f:
    data = json.load(f)

user_state = {}

# Классы: А–Г (кириллические)
CLASS_LETTERS = ["А", "Б", "В", "Г"]

# Алфавит учителей
ALPHABET = list("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ")


# ========================
# 🔧 STATE FIX
# ========================
def get_user(chat_id):
    if chat_id not in user_state:
        user_state[chat_id] = {}
    return user_state[chat_id]


# ========================
# 🔹 ГЛАВНОЕ МЕНЮ
# ========================
def main_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📍 Расписание звонков", callback_data="bells", style='primary'),
        types.InlineKeyboardButton("📍 Расписание уроков", callback_data="lessons", style='primary')
    )
    return markup


# ========================
# 🔤 АЛФАВИТ (2 страницы)
# ========================
def alphabet_page(page=0):
    markup = types.InlineKeyboardMarkup(row_width=6)

    half = len(ALPHABET) // 2
    pages = [ALPHABET[:half], ALPHABET[half:]]

    letters = pages[page]

    buttons = [
        types.InlineKeyboardButton(l, callback_data=f"letter_{l}")
        for l in letters
    ]
    markup.add(*buttons)

    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("⬅️", callback_data=f"alphabet_{page-1}"))
    if page < len(pages) - 1:
        nav.append(types.InlineKeyboardButton("➡️", callback_data=f"alphabet_{page+1}"))

    if nav:
        markup.row(*nav)

    markup.row(
        types.InlineKeyboardButton("⬅️ Назад", callback_data="lessons", style='success'),
        types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
    )

    return markup


# ========================
# 🚀 START (С КАРТИНКОЙ)
# ========================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "📚 Главное меню:", reply_markup=main_menu_markup())


# ========================
# 🔍 ПОИСК УЧИТЕЛЯ
# ========================
@bot.message_handler(func=lambda m: True)
def teacher_search(message):
    chat_id = message.chat.id
    user = get_user(chat_id)

    if user.get("mode") != "teacher":
        return

    text = message.text.strip().capitalize()

    matches = [t for t in data["teachers"] if t.startswith(text)]

    if not matches:
        bot.send_message(chat_id, "❌ Учитель не найден")
        return

    markup = types.InlineKeyboardMarkup()
    for t in matches:
        markup.add(types.InlineKeyboardButton(t, callback_data=f"teacher_{t}"))

    markup.row(
        types.InlineKeyboardButton("⬅️ Назад", callback_data="teacher", style='success'),
        types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
    )

    bot.send_message(chat_id, "🔎 Результаты поиска:", reply_markup=markup)


# ========================
# 🔹 CALLBACK
# ========================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    user = get_user(chat_id)

    # 🏠 ГЛАВНАЯ
    if call.data == "home":
        bot.edit_message_text(
            "📚 Главное меню:",
            chat_id,
            call.message.message_id,
            reply_markup=main_menu_markup()
        )

    # 🔔 ЗВОНКИ
    elif call.data == "bells":
        text = "🔔 Расписание звонков:\n\n"
        for i, time in enumerate(data["bells"]["Понедельник"], 1):
            text += f"{i}. {time}\n"

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger'))

        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
        return

    # 📚 УРОКИ
    elif call.data == "lessons":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("☀️ Класс", callback_data="class", style='primary'),
            types.InlineKeyboardButton("👩‍🏫 Учитель", callback_data="teacher", style='success')
        )
        markup.row(types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger'))

        bot.edit_message_text("Выберите:", chat_id, call.message.message_id, reply_markup=markup)

    # 🏫 КЛАССЫ
    elif call.data == "class":
        user["mode"] = "class"

        markup = types.InlineKeyboardMarkup(row_width=4)
        buttons = [
            types.InlineKeyboardButton(str(i), callback_data=f"class_{i}")
            for i in range(1, 12)
        ]
        markup.add(*buttons)

        markup.row(
            types.InlineKeyboardButton("⬅️ Назад", callback_data="lessons", style='success'),
            types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
        )

        bot.edit_message_text("Выберите класс:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("class_"):
        cls = call.data.split("_")[1]
        user["class_num"] = cls

        markup = types.InlineKeyboardMarkup(row_width=4)

        buttons = [
            types.InlineKeyboardButton(f"{cls}{l}", callback_data=f"classfull_{cls}{l}")
            for l in CLASS_LETTERS
        ]
        markup.add(*buttons)

        markup.row(
            types.InlineKeyboardButton("⬅️ Назад", callback_data="class", style='success'),
            types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
        )

        bot.edit_message_text("Выберите букву:", chat_id, call.message.message_id, reply_markup=markup)
        return

    elif call.data.startswith("classfull_"):
        user["class"] = call.data.split("_")[1]
        send_days(call)
        return

    # 👩‍🏫 УЧИТЕЛЯ
    elif call.data == "teacher":
        user["mode"] = "teacher"

        bot.edit_message_text(
            "✍️ Введите фамилию или выберите букву:",
            chat_id,
            call.message.message_id,
            reply_markup=alphabet_page(0)
        )

    elif call.data.startswith("alphabet_"):
        page = int(call.data.split("_")[1])

        bot.edit_message_text(
            "Выберите букву:",
            chat_id,
            call.message.message_id,
            reply_markup=alphabet_page(page)
        )

    elif call.data.startswith("letter_"):
        letter = call.data.split("_")[1]

        teachers = [t for t in data["teachers"] if t.startswith(letter)]

        markup = types.InlineKeyboardMarkup()
        for t in teachers:
            markup.add(types.InlineKeyboardButton(t, callback_data=f"teacher_{t}"))

        markup.row(
            types.InlineKeyboardButton("⬅️ Назад", callback_data="teacher", style='success'),
            types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
        )

        bot.edit_message_text("Выберите учителя:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("teacher_"):
        user["teacher"] = call.data.split("_")[1]
        send_days(call)
        return

    # 📅 ДНИ
    elif call.data.startswith("day_"):
        day = call.data.split("_")[1]

        if user.get("mode") == "class":
            cls = user.get("class")
            lessons = data["classes"].get(cls, {}).get(day, [])

            text = f"📚 {cls} — {day}\n\n"
            for l in lessons:
                text += f"{l['lesson']}. {l['time']}\n{l['subject']} ({l['room']})\n👨‍🏫 {l['teacher']}\n\n"

        else:
            teacher = user.get("teacher")
            lessons = data["teachers"].get(teacher, {}).get(day, [])

            text = f"👩‍🏫 {teacher} — {day}\n\n"
            for l in lessons:
                text += f"{l['lesson']}. {l['time']}\n{l['class']} — {l['subject']} ({l['room']})\n\n"

        back = "class" if user.get("mode") == "class" else "teacher"

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️ Назад", callback_data=back, style='success'),
            types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
        )

        bot.edit_message_text(text, chat_id, call.message.message_id, reply_markup=markup)
        return


# ========================
# 📅 ДНИ
# ========================
def send_days(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

    buttons = [
        types.InlineKeyboardButton(d, callback_data=f"day_{d}")
        for d in days
    ]
    markup.add(*buttons)

    user = get_user(call.message.chat.id)
    back = "class" if user.get("mode") == "class" else "teacher"

    markup.row(
        types.InlineKeyboardButton("⬅️ Назад", callback_data=back, style='success'),
        types.InlineKeyboardButton("🏠 Главная", callback_data="home", style='danger')
    )

    bot.edit_message_text(
        "Выберите день недели:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )
    return


# ========================
print("Бот запущен")
bot.remove_webhook()
bot.polling(none_stop=True)