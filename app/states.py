from aiogram.fsm.state import StatesGroup, State

class ReminderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_birthday = State()
