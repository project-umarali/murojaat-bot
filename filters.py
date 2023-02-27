

from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP,
            # types.ChatType.SUPER_GROUP
        )

class IsPrivate(BoundFilter):
    async def check(self, message: types.Message):
        return message.chat.type == types.ChatType.PRIVATE

class Form(StatesGroup):
    question = State()
class Form2(StatesGroup):
    question_id = State()
    question = State()

