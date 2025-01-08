from datetime import datetime

from aiogram import types, Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.keyboards import clear
from app.states import ReminderStates
from app.utils import load_reminders, save_reminders

# consts
reminders = load_reminders()
birthday = []

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "Привет! Я бот-напоминалка.\n",
        reply_markup=kb.main,
    )

@router.message(F.text == 'Установить напоминание')
async def start_set_reminder(message: types.Message, state: FSMContext):
    await state.set_state(ReminderStates.waiting_for_name)
    await message.answer("Введите имя кого хотите добавить", reply_markup=clear)

@router.message(ReminderStates.waiting_for_name)
async def enter_name(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Установка напоминания отменена.", reply_markup=kb.main)
        return

    # Сохраняем имя во временное хранилище состояния
    await state.update_data(name=message.text)
    await state.set_state(ReminderStates.waiting_for_birthday)
    await message.answer("Введите дату рождения в формате ДД.ММ.ГГГГ")


@router.message(ReminderStates.waiting_for_birthday)
async def enter_birthday(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Установка напоминания отменена.", reply_markup=kb.main)
        return

    try:
        birthday = datetime.strptime(message.text, "%d.%m.%Y")
        user_data = await state.get_data()

        # Сохраняем напоминание
        user_id = str(message.from_user.id)
        if user_id not in reminders:
            reminders[user_id] = {"reminders": []}

        reminders[user_id]["reminders"].append({
            "name": user_data["name"],
            "birthday": birthday.strftime("%d.%m.%Y"),
            "intervals": [1, 7, 30]
        })

        # Завершаем процесс и возвращаем главную клавиатуру
        save_reminders(reminders)
        await state.clear()
        await message.answer(
            f"Напоминание для {user_data['name']} на {birthday.strftime('%d.%m.%Y')} успешно установлено!",
            reply_markup=kb.main
        )
    except ValueError:
        await message.answer("Ошибка: введите дату в формате ДД.ММ.ГГГГ")

@router.message(F.text.casefold() == 'отмена'.casefold())
async def cancel_anywhere(message: types.Message, state: FSMContext):
    if await state.get_state():
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=kb.main)
    else:
        await message.answer("Вы не находитесь в процессе настройки.")


# Команда для отображения следующего дня рождения с напоминанием
@router.message(F.text == 'следующий др')
async def info(message: types.Message):
    now = datetime.now()
    user_id = str(message.from_user.id)

    if user_id not in reminders or not reminders[user_id]["reminders"]:
        await message.answer("У вас нету напоминаний.")
        return

    # Ищем ближайший день рождения
    user_reminders = reminders[user_id]["reminders"]
    next_birthday = None

    for reminder in user_reminders:
        birthday = datetime.strptime(reminder["birthday"], "%d.%m.%Y")
        current_year_birthday = birthday.replace(year=now.year)

        # Если день рождения в текущем году уже прошёл, переносим его на следующий год
        if current_year_birthday < now:
            current_year_birthday = current_year_birthday.replace(year=now.year + 1)

        # Обновляем ближайший день рождения
        if not next_birthday or current_year_birthday < next_birthday["date"]:
            next_birthday = {"name": reminder["name"], "date": current_year_birthday}

    # Если нашли ближайший день рождения
    if next_birthday:
        time_left = next_birthday["date"] - now
        days_left = time_left.days
        hours_left = time_left.seconds // 3600
        minutes_left = (time_left.seconds // 60) % 60

        await message.answer(
            f"Следующий день рождения у : {next_birthday['name']} через {days_left} дня, {hours_left} часов и {minutes_left} минут.")
    else:
        await message.answer("У вас нет предстоящих дней рождения.")


# # Команда изменения интервала напоминания
# @router.message(F.text.casefold() == 'изменить интервал'.casefold())
# async def cmd_setinterval(message: types.Message):
#     try:
#         args = message.text.split(maxsplit=2)
#         if len(args) < 3:
#             raise ValueError("Недостаточно аргументов.")
#
#         name_of_human = args[1]
#         action = args[2].lower()
#
#         # Находим напоминание для данного пользователя и изменяем интервал
#         updated = False
#         for reminder in reminders:
#             if reminder["user_id"] == message.from_user.id and reminder["name"] == name_of_human:
#                 if action == "add":
#                     new_interval = int(args[3]) if len(args) > 3 else None
#                     if new_interval not in reminder_intervals:
#                         raise ValueError(f"Интервал должен быть одним из: {', '.join(map(str, reminder_intervals))}.")
#                     reminder["intervals"].append(new_interval)
#                     updated = True
#                     await message.answer(f"Интервал {new_interval} дней добавлен для {name_of_human}.")
#                     break
#                 elif action == "remove":
#                     interval_to_remove = int(args[3]) if len(args) > 3 else None
#                     if interval_to_remove in reminder["intervals"]:
#                         reminder["intervals"].remove(interval_to_remove)
#                         updated = True
#                         await message.answer(f"Интервал {interval_to_remove} дней удалён для {name_of_human}.")
#                     else:
#                         await message.answer(f"Интервал {interval_to_remove} дней не найден для {name_of_human}.")
#                     break
#                 elif action == "set":
#                     new_interval = int(args[3]) if len(args) > 3 else None
#                     if new_interval not in reminder_intervals:
#                         raise ValueError(f"Интервал должен быть одним из: {', '.join(map(str, reminder_intervals))}.")
#                     reminder["intervals"] = [new_interval]
#                     updated = True
#                     await message.answer(f"Интервал напоминания для {name_of_human} изменён на {new_interval} дней.")
#                     break
#
#         if not updated:
#             await message.answer(f"Не найдено напоминания для {name_of_human}.")
#
#     except ValueError as e:
#         await message.answer(
#             f"Ошибка: {str(e)}\nИспользуй /setinterval <имя> <add/remove/set> <интервал>.\nПример: /setinterval Серёжа add 7.")
