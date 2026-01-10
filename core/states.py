from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    waiting_for_hero_build = State()    # Menunggu input nama hero untuk fitur Build
    waiting_for_hero_counter = State()  # Menunggu input nama hero untuk fitur Counter
    waiting_for_hero_gameplay = State() # Menunggu input nama hero untuk fitur Gameplay