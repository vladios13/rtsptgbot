import logging
import os
import socket

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ChatActions

import ffmpeg
from ffmpeg import Error as FFmpegError

from datetime import datetime
from pytz import timezone

from config import TOKEN, CAM_1, RTSP_PING

logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
logger.info("Starting bot")


# Чекаем доступность ip-адреса
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)      #2 Second Timeout
result = sock.connect_ex((RTSP_PING, 558))


# Snap клавиатура
def get_snap_keyboard():
    kb_contents = [
        [
            types.InlineKeyboardButton(text="Камера № 1", callback_data="snap1"),
        ]
            
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=kb_contents)


# Gif клавиатура
def get_gif_keyboard():
    kb_contents = [
        [
            types.InlineKeyboardButton(text="Камера № 1", callback_data="gif1"),
        ]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=kb_contents)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer("👋")
    await message.answer(
        f"ℹ <i> Telegram-бот для работы с <b>RTSP</b>-камерами.</i>\n"
        f"Для справки наберите команду /help. \n\n"
        f"🧑‍💻 Разработчик: @vladios13blog\n🔧 Библиотека бота: <a href='https://github.com/aiogram/aiogram'>Aiogram</a>.",
        disable_web_page_preview=True)


# команда "help"
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(
        f"<b>Краткая справка для команд бота:</b> \n\n"
        f"📷 <b>Получить скриншот:</b> /s\n"
        f"📹 <b>Получить Gif:</b> /g\n"
        f"🌐 <b>Проверить доступность порта:</b> /p"
    )


# пингуем порт
@dp.message_handler(commands=['ping', 'p'])
async def process_ping_command(message: types.Message):
    if result == 0:
        await message.answer('✅ Ping успешен')
    else:
        await message.answer('❌ Ping не успешен')


# команда для получения скриншотов
@dp.message_handler(commands=['snap', 's'])
async def process_snap_command(message: types.Message):
    text_info = ("📷 Нажми на нужную кнопку что бы получить скриншот с камеры:")
    await message.reply(text_info, reply_markup=get_snap_keyboard())


# команда для получение Gif файлов
@dp.message_handler(commands=['gif', 'g'])
async def process_gif_command(message: types.Message):
    text_info = ("📹 Нажми на нужную кнопку что бы получить запись GIF:\n\n<i>Длительность составляет 5 сек.</i>")
    await message.reply(text_info, reply_markup=get_gif_keyboard())


@dp.callback_query_handler(text="snap1")
async def send_snap_1_value(call: types.CallbackQuery):
    try:
        nowMSK = datetime.now(timezone('Europe/Moscow'))
        caption = datetime.now().strftime('%H:%M:%S')
        nowOut = nowMSK.strftime("snap-%d-%m-%Y-%H-%M-%S.jpg")
        process = (
            ffmpeg
            .input(CAM_1, rtsp_transport="tcp", vsync="2")
            .output(nowOut, vframes="1")
            .run(capture_stderr=True)
        )
        await call.answer()
        await call.message.answer_photo(types.InputFile(nowOut), caption="<b>Фото сделано:</b> " + str(caption), reply_markup=get_snap_keyboard())
    except FFmpegError as _ex:
        if "Connection refused" in _ex.stderr.decode('utf8'):
            await call.message.reply(f"❌ Ошибка подключения к камере:\n\n<code>Connection refused</code>")
        elif "401" in _ex.stderr.decode('utf8'):
            await call.message.reply(f"❌ Ошибка подключения к камере:\n\n<code>Неправильный логин или пароль</code>")
    os.remove(nowOut)


@dp.callback_query_handler(text="gif1")
async def send_gif_1_value(call: types.CallbackQuery):
    try:
        await bot.send_chat_action(call.from_user.id, ChatActions.RECORD_VIDEO)
        text_gif = ("⏳ <b>Подключаюсь к камере:</b> \n<i>Запись GIF может занять некоторое время....</i>")
        msg = await call.message.answer(text_gif)
        nowMSK = datetime.now(timezone('Europe/Moscow'))
        caption = datetime.now().strftime('%H:%M:%S')
        nowOut = nowMSK.strftime("gif-%d-%m-%Y-%H-%M-%S.mp4")
        process = (
            ffmpeg
            .input(CAM_1, rtsp_transport="tcp", vsync="2")
            .output(nowOut, crf=40, pix_fmt='yuv420p', preset='ultrafast', vcodec='copy', t=5)
            .run(capture_stderr=True)
        )
        await msg.delete()
        await call.message.answer_animation(types.InputFile(nowOut), caption="GIF записан: " + str(caption), reply_markup=get_gif_keyboard())
        await call.answer()
    except FFmpegError as _ex:
        if "Connection refused" in _ex.stderr.decode('utf8'):
            await call.message.reply(f"❌ Ошибка подключения к камере:\n\n<code>Connection refused</code>")
        elif "401" in _ex.stderr.decode('utf8'):
            await call.message.reply(f"❌ Ошибка подключения к камере:\n\n<code>Неправильный логин или пароль</code>")
    os.remove(nowOut)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
