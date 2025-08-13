import os

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove, InputFile
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

from app.database.requests import set_user, get_users

from app.yt_mp3 import download_mp3_from_youtube, remove_file

# from app.logger import logger

from app.variables import ADMIN


class Input(StatesGroup):
    url = State()
    failed = State()
    msg_chat_id = State()
    msg_id = State()
class Await(StatesGroup):
    await_state = State()

class AwaitInput(StatesGroup):
    await_input = State()

router = Router()



@router.message(F.text & ~(F.text.startswith('/start') | F.text.startswith('/src')), Await.await_state)
async def start_handler(message: Message, state: FSMContext):
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.message(F.text & ~(F.text.startswith('/start') | F.text.startswith('/src')), Input.failed)
async def start_handler(message : Message, state: FSMContext):
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(Await.await_state)
    data = await state.get_data()
    try:
        await message.bot.delete_message(chat_id=data["msg_chat_id"], message_id=data["msg_id"])
    except: return

# Обработчик команды /start
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    if state.get_state() == AwaitInput.await_input: return
    if await state.get_state() == Input.failed:
        data = await state.get_data()
        try:
            await message.bot.delete_message(chat_id=data["msg_chat_id"], message_id=data["msg_id"])
        except:
            return
            
    await state.set_state(Await.await_state)
            
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(
        "👋 Привет! Я — бот, который пришлет тебе mp3 c ютуба\n"
        "просто введи команду /src и вставь сслыку\n"
        "длинной не более 10 минут\n"
        '"это сообщение можно удалить"',
        reply_markup=kb.src
    )

    await set_user(message)


@router.message(Command("user_info"))
async def start_handler(message: Message):
    if message.from_user.id != int(ADMIN): return
    all_users = await get_users()
    if not all_users: return await message.answer("No users")

    await message.answer(f"USERS:")

    for user in all_users:
        text = (f"ID: {user.id}\
        \nTG_ID: {user.tg_id}\
        \nusername: {user.username}\
        \nfull_name: {user.full_name}\
        \ndata registration: {user.data}")
        await message.answer(text)

@router.message(Command("src"))
async def start_handler(message: Message, state: FSMContext):
    if await state.get_state() == Input.url: return
    if await state.get_state() == Input.failed:
        data = await state.get_data()
        try:
            await message.bot.delete_message(chat_id=data["msg_chat_id"], message_id=data["msg_id"])
        except:
            return


    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.bot.send_message(chat_id=message.chat.id, text="Вставьте ссылку", reply_markup=ReplyKeyboardRemove())
    await state.update_data(msg_chat_id=msg.chat.id, msg_id=msg.message_id)
    await state.set_state(Input.url)


from urllib.parse import urlparse, parse_qs

def is_valid_youtube_video(url: str) -> bool:
    """
    Возвращает True, если это одиночное видео, False если плейлист/микс
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return 'list' not in params



@router.message(Input.url)
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(AwaitInput.await_input)
    data = await state.get_data()
    await message.bot.delete_message(chat_id=data["msg_chat_id"], message_id=data["msg_id"])

    msg_await = await message.bot.send_message(chat_id=message.chat.id, text="ожидайте...")
    mp3_patch = []

    if not is_valid_youtube_video(message.text):
        msg_failed = await message.answer("Не удалось скачать, возможно это плейлист или ссылка с браузера")
        await state.update_data(msg_chat_id=msg_failed.chat.id, msg_id=msg_failed.message_id)
        await state.set_state(Input.failed)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

        await message.bot.delete_message(chat_id=msg_await.chat.id, message_id=msg_await.message_id)

        return

    try:
        mp3_patch = download_mp3_from_youtube(message.text)
        if len(mp3_patch) == 1:
            msg_failed = await message.answer(mp3_patch[0])
            await state.update_data(msg_chat_id=msg_failed.chat.id, msg_id=msg_failed.message_id)
            await state.set_state(Input.failed)

        else:
            await message.bot.send_audio(chat_id=message.chat.id, audio=mp3_patch[0], reply_markup=kb.src)
            await state.set_state(Await.await_state)
    except Exception as e:
        print(e)
        msg_failed = await message.answer("Не удалось скачать", reply_markup=kb.src)
        await state.update_data(msg_chat_id=msg_failed.chat.id, msg_id=msg_failed.message_id)
        await state.set_state(Input.failed)


    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await message.bot.delete_message(chat_id=msg_await.chat.id, message_id=msg_await.message_id)

    if len(mp3_patch) > 1: os.remove(mp3_patch[1])





