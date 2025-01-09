from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Установить напоминание')],
    [KeyboardButton(text='настройки'), KeyboardButton(text='следующий др')]
],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)
clear = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True,
)
settings = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='изменить интервал')],
    [KeyboardButton(text='о нас')],
    [KeyboardButton(text='Отмена')]
],
    resize_keyboard=True,
    input_field_placeholder="Настройки..."
)