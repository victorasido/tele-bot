from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    waiting_for_hero_build = State()    # Fitur Build
    waiting_for_hero_counter = State()  # Fitur Counter & Recounter
    waiting_for_hero_gameplay = State() # Fitur Gameplay
    waiting_for_hero_comp = State()     # <--- TAMBAHKAN INI (Fitur Komposisi Tim)