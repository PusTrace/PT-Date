from datetime import datetime

from aiogram import types, Router, F
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.keyboards import clear
from app.states import ReminderStates
from app.utils import load_reminders, save_reminders


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
        await message.answer("Вы не находитесь в процессе настройки.", reply_markup=kb.main)



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



@router.message(F.text.casefold() == 'настройки'.casefold())
async def settings(message: types.Message):
    await message.answer("настройки", reply_markup=kb.settings)

@router.message(F.text.casefold() == 'изменить интервал'.casefold())
async def settings_interval(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Установка интервала отменено.", reply_markup=kb.main)
        return
    await state.set_state(ReminderStates.waiting_for_name_settings)
    await message.answer("Введите имя для кого хотите изменить интервал", reply_markup=clear)

@router.message(ReminderStates.waiting_for_name_settings)
async def enter_name(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Изменение интервала отменено.", reply_markup=kb.main)
        return

    await state.update_data(name=message.text)
    await state.set_state(ReminderStates.waiting_for_interval_settings)
    await message.answer("Введите интервал на который хотите изменить в днях.\n"
                         "Пример: 1, 7, 30\n"
                         "Это изменит интервал так что оповещения придут за 1, 7, 30 дней")

@router.message(ReminderStates.waiting_for_interval_settings)
async def enter_interval(message: types.Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Изменение интервала отменено.", reply_markup=kb.main)
        return

    try:
        user_interval_str = str(message.text)
        user_interval = [item.strip() for item in user_interval_str.split(",")] #нужно превращать строки в числа перед добавлением в список
        user_data = await state.get_data()

        # Сохраняем напоминание
        user_id = str(message.from_user.id)
        if user_id not in reminders:
            reminders[user_id] = {"reminders": []}

        reminders[user_id]["reminders"].append({
            "name": user_data["name"],
            "intervals": user_interval["intervals"]
        })

        # Завершаем процесс и возвращаем главную клавиатуру
        save_reminders(reminders)
        await state.clear()
        await message.answer(
            f"Интервал для {user_data['name']} на {user_interval_str} успешно изменён!",
            reply_markup=kb.main
        )
    except ValueError:
        await message.answer("Ошибка: введите интервал в формате [1, 7, 30]")


@router.message(F.text.casefold() == 'о нас'.casefold())
async def about_us(message: types.Message):
    await message.answer(
        "Разработчик: Вавилин Сергей\n"
        "Контакты:\n"
        "https://t.me/PusTrace\n"
        "sergeivavilin2005@mail.ru\n"
        "\n"
        "Системный администратор, а так же владелец сервера и бота: Вавилин Дмитрий\n"
        "Контакты:\n"
        "https://t.me/VDmitriiyM\n", reply_markup=kb.main)