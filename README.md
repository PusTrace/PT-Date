A simple bot for setting up alerts in telegram

Простой бот для установки оповещений в телеграм

---
### Структура
#### main.py
Является точкой входа в проект.
Так-же в нём описана логика отправки сообщений и проверки работы бота
#### utils.py
Утилиты, загрузка и сохранение базы данных например
#### states.py
Нужен для того чтобы хранить состояние бота и сохранения промежуточных данных
#### keyboards.py
Хранит клавиатуры для дальнейшей отрисовки их
#### handlers.py
Обработчики событий, хранит в себе основные функции работы и логики бота такие как реагирование на сообщения