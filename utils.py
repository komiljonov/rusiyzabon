from typing import Sequence

from telegram import ReplyKeyboardMarkup as ReplyKeyboardMarkupImp
from telegram._keyboardbutton import KeyboardButton
from telegram._utils.types import JSONDict

from constants import BACK


class ReplyKeyboardMarkup(ReplyKeyboardMarkupImp):
    def __init__(
        self,
        keyboard: Sequence[Sequence[str | KeyboardButton]] = [],
        back: bool = True,
        resize_keyboard: bool | None = True,
        one_time_keyboard: bool | None = None,
        selective: bool | None = None,
        input_field_placeholder: str | None = None,
        is_persistent: bool | None = None,
        *,
        api_kwargs: JSONDict | None = None,
    ):
        super().__init__(
            [*keyboard, [BACK if back else ""]],
            resize_keyboard,
            one_time_keyboard,
            selective,
            input_field_placeholder,
            is_persistent,
            api_kwargs=api_kwargs,
        )


def fixNumber(number: str):
    if len(number) == 13:
        return number
    if len(number) == 10 and number.startswith("+"):
        return f"+998{number[1:]}"
    if len(number) == 9:
        return f"+998{number}"
