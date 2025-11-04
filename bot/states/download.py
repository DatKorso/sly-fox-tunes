"""Download states for FSM."""

from aiogram.fsm.state import State, StatesGroup


class DownloadStates(StatesGroup):
    """States for download process."""

    waiting_for_format = State()  # User sent URL, waiting for format selection
