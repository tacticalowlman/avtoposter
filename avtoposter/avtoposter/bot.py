
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
import json

import api
from data import telegram



def redacted(text):
    array_of_dates = api.Settings.get_ar()
    text_redacted = text.format(*array_of_dates)
    return text_redacted

class DataConn:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise

class Editing(StatesGroup):
    main = State()
    date = State()
    text = State()


class AdminFilter(BoundFilter):
    key = 'is_admin'
    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        return message.from_user.id in telegram.admins


edit_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
edit_kb.add(types.KeyboardButton(text='Изменить текст'))
edit_kb.add(types.KeyboardButton(text='Изменить время постинга (глобально)'))

bot = Bot(token=telegram.token, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

dp.filters_factory.bind(AdminFilter)


@dp.message_handler(commands=['start'], is_admin=True)
async def start(msg: types.Message):
    m = [
        f'Добро пожаловать в админ-панель, {msg.from_user.full_name}',
    ]
    last_post = api.Posts.get_last_saved()
    print(last_post)
    if last_post is not None:
        m.extend([
            f'Пост будет на канале {last_post.post_time}',
            'Текст поста: \n',
            last_post.text
        ])
    else:
        m.extend([
            'Сейчас нет запланированных постов'
        ])
    await msg.reply('\n'.join(m), reply_markup=edit_kb)


@dp.message_handler(commands=['cancel'], is_admin=True, state='*')
async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    m = [
        'Действие отменено'
    ]
    await msg.reply('\n'.join(m))


@dp.message_handler(lambda msg: msg.text == 'Изменить текст', is_admin=True)
async def edit_text_start(msg: types.Message):
    await Editing.text.set()
    m = [
        'Следующее ваше сообщение заменит текст следующего поста',
        'Для отмены нажмите на команду /cancel'
    ]
    await msg.reply('\n'.join(m))


@dp.message_handler(lambda msg: msg.text == 'Изменить время постинга (глобально)', is_admin=True)
async def edit_time_start(msg: types.Message):
    await Editing.date.set()
    m = [
        'Напишите час, в который пост должен быть опубликован (от 0 до 23)',
        'Для отмены нажмите на команду /cancel'
    ]
    await msg.reply('\n'.join(m))


@dp.message_handler(state=Editing.date, is_admin=True)
async def edit_time(msg: types.Message, state: FSMContext):
    if msg.text.isdigit():
        v = int(msg.text)
        if 0 <= v <= 23:
            api.Settings.set_time(v - 1)
            m = [
                f'Время изменено. Теперь посты будут выходить в {v}:00'
            ]
            await state.finish()
        else:
            m = [
                'Число указано неверно'
                'От 0 до 23'
            ]
    else:
        m = [
            'Время - число от 0 до 23'
        ]
    await msg.reply('\n'.join(m))


@dp.message_handler(state=Editing.text, is_admin=True)
async def edit_text(msg: types.Message, state: FSMContext):
    api.Posts.edit_last_post_text(redacted(msg.html_text))
    api.Settings.chngtxt(msg.html_text)
    last_post = api.Posts.get_last_saved()
    m = [
        f'Пост будет на канале {last_post.post_time}',
        'Текст поста: \n',
        last_post.text
    ]
    await msg.reply('\n'.join(m))
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp)
