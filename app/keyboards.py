from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Установить напоминание')],
    [KeyboardButton(text='следующий др'), KeyboardButton(text='Изменить интервал')]
],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню"
)
clear = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отмена')],
], resize_keyboard=True,
)