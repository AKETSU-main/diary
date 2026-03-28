import json
import random

# Классы от 1 до 11, буквы А-Г
CLASS_LETTERS = ["А", "Б", "В", "Г"]

# Предметы
SUBJECTS = [
    "Математика",
    "Русский язык",
    "Литература",
    "История",
    "География",
    "Биология",
    "Физика",
    "Химия",
    "Английский язык",
    "Физкультура",
    "Информатика",
    "ОБЖ",
    "Музыка",
    "ИЗО",
    "Технология"
]

# Учителя (фамилии)
TEACHERS = [
    "Иванова", "Петрова", "Сидорова", "Кузнецова", "Попова",
    "Васильева", "Смирнова", "Козлова", "Новикова", "Морозова",
    "Лебедева", "Семенова", "Егорова", "Павлова", "Козлов",
    "Алексеев", "Борисов", "Владимиров", "Григорьев", "Дмитриев"
]

# Кабинеты
ROOMS = ["101", "102", "103", "104", "105", "201", "202", "203", "204", "205"]

# Дни недели
DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

# Расписание звонков (5 уроков по 45 мин, перемены по 5 мин)
# Урок 1: 08:00-08:45
# Урок 2: 08:50-09:35
# Урок 3: 09:40-10:25
# Урок 4: 10:30-11:15
# Урок 5: 11:20-12:05
BELL_TIMES = [
    "08:00-08:45",
    "08:50-09:35",
    "09:40-10:25",
    "10:30-11:15",
    "11:20-12:05"
]

def generate_schedule():
    data = {
        "classes": {},
        "teachers": {teacher: {day: [] for day in DAYS} for teacher in TEACHERS},
        "bells": {day: BELL_TIMES.copy() for day in DAYS}
    }

    # Генерируем расписание для каждого класса
    for grade in range(1, 12):  # 1-11 классы
        for letter in CLASS_LETTERS:
            class_name = f"{grade}{letter}"
            data["classes"][class_name] = {day: [] for day in DAYS}

            # Для каждого дня недели
            for day in DAYS:
                # Выбираем 5 предметов на день (можно с повторами)
                used_teachers = set()

                for lesson_num in range(1, 6):  # 5 уроков
                    subject = random.choice(SUBJECTS)

                    # Выбираем учителя (не повторяющегося в этот день по возможности)
                    available_teachers = [t for t in TEACHERS if t not in used_teachers]
                    if not available_teachers:
                        available_teachers = TEACHERS
                    teacher = random.choice(available_teachers)
                    used_teachers.add(teacher)

                    room = random.choice(ROOMS)
                    time = BELL_TIMES[lesson_num - 1]

                    # Добавляем урок в расписание класса
                    lesson_data = {
                        "lesson": lesson_num,
                        "time": time,
                        "subject": subject,
                        "room": room,
                        "teacher": teacher
                    }
                    data["classes"][class_name][day].append(lesson_data)

                    # Добавляем урок в расписание учителя
                    teacher_lesson = {
                        "lesson": lesson_num,
                        "time": time,
                        "class": class_name,
                        "subject": subject,
                        "room": room
                    }
                    data["teachers"][teacher][day].append(teacher_lesson)

    return data

if __name__ == "__main__":
    random.seed(42)  # Для воспроизводимости
    schedule_data = generate_schedule()

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=2)

    print("База данных успешно заполнена!")
    print(f"Классов: {len(schedule_data['classes'])}")
    print(f"Учителей: {len(schedule_data['teachers'])}")
    print(f"Дней в расписании звонков: {len(schedule_data['bells'])}")