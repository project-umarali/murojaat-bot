import psycopg2
from config import *

try:
    connection = psycopg2.connect(
        dbname=PGDATABASE,
        host=PGHOST,
        user=PGUSER,
        password=PGPASSWORD ,
        port=PGPORT
    )
    connection.autocommit = True
    # cursor = connection.cursor()
    # with connection.cursor() as cursor:
    #     cursor.execute("""SELECT version()""")
    #     print(cursor.fetchall())
except Exception as ex:
    print('[INFO] error', ex)





import os
from aiogram import Dispatcher, Bot, executor
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# import sqlite3
load_dotenv()

from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup


from filters import IsGroup, IsPrivate, Form

from pathlib import Path
from aiogram.types.input_file import InputFile


def keybuttons():
    markup = ReplyKeyboardMarkup([[
        KeyboardButton(text='Savol_berish')]], resize_keyboard=True
    )
    return markup


TOKEN = os.getenv('TOKEN')
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(IsPrivate(), commands='start')
async def start(message: Message):
    chat_id = message.chat.id

    await bot.send_message(chat_id, f'Assalomu alaykum va rahmatullohi va barokatuh! \n@Husayn_Buxoriy rasmiy sahifasining savol-javoblar botiga xush kelibsiz!\nSavol berish uchun pastdagi <b>"Savol berish"</b> tugmasini bosing', reply_markup=keybuttons(), parse_mode='HTML')

@dp.message_handler(IsPrivate(), commands='admin')
async def statistik(message: Message):
    if message.chat.id == 659237008:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT * FROM user_question''')
            data = cursor.fetchall()

        activ_users = set()
        answered = []
        dont_answered = []

        for i in data:
            activ_users.add(i[1])
            if i[-1] == 1:
                answered.append(i[-1])
            elif i[-1] == 0:
                dont_answered.append(str(i[0]) + '-savol')

        answer_sum = sum(answered)

        text = f'Foydalanuvchilar soni: {len(activ_users)} ta\n' \
               f'Faol foydalanuvchilar: {len(activ_users)} ta\n' \
               f'Umumiy berilgan savollar soni: {len(data)} ta\n' \
               f'Javob berilgan savollar: {answer_sum} ta\n' \
               f'Javob berilmagan savollar: {dont_answered}'

        await bot.send_message(message.chat.id, text)
#


@dp.message_handler(IsGroup(), commands='statistika')
async def statistika(message: Message):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT * FROM user_question''')
        data = cursor.fetchall()

    activ_users = set()
    answered = []
    dont_answered = []

    for i in data:
        activ_users.add(i[3])
        if i[-1] == 1:
            answered.append(i[-1])
        elif i[-1] == 0:
            dont_answered.append(str(i[0])+'-savol')
    print(len(activ_users))
    answer_sum = sum(answered)

    text = f'Foydalanuvchilar soni: {len(activ_users)} ta\n' \
           f'Faol foydalanuvchilar: {len(activ_users)} ta\n' \
           f'Umumiy berilgan savollar soni: {len(data)} ta\n' \
           f'Javob berilgan savollar: {answer_sum} ta\n' \
           f'Javob berilmagan savollar: {dont_answered}'

    await bot.send_message(message.chat.id, text)

@dp.message_handler(IsGroup(), content_types=('voice', 'text'))
async def reply_message(message: Message):
    try:
        if message.text:
            memeber_id = message.reply_to_message.text.split()
            chat_id = memeber_id[0]
            question_id, _ = memeber_id[1].split('-')
            print(chat_id)
            answer = message.text

            await bot.send_message(chat_id, f'{question_id}-savol javobi: \n\n{answer}',
                                   reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='Qabul qildim',
                                                                                                callback_data=f'accept_{question_id}')))

        else:
            # Ниже пытаемся вычленить имя файла, да и вообще берем данные с мессагиv
            file_id = message.voice.file_id
            file_info = await bot.get_file(file_id)
            path = file_info.file_path  # Вот тут-то и полный путь до файла (например: voice/file_2.oga)
            fname = os.path.basename(path)  # Преобразуем путь в имя файла (например: file_2.oga)
            #
            file_on_disk = Path("", f"{file_id}.tmp")
            await bot.download_file(path, destination=file_on_disk)
            memeber_id = message.reply_to_message.text.split()
            chat_id = memeber_id[0]
            question_id = memeber_id[1]
            # await bot.send_voice(chat_id,voice=fname, caption='javob')
            # path = Path("", message.voice)
            voice = InputFile(file_on_disk)
            await bot.send_voice(chat_id, voice,
                                 caption=f"{question_id} javobi")
    except:
        pass

@dp.message_handler(lambda message: 'Savol_berish' in message.text)
async def savolbering(message: Message):
    await bot.send_message(message.chat.id, 'Savol, taklif va shikoyatlaringizni bitta xabarga jamlab yuborishingizni so\'rab qolamiz.')
    await Form.question.set()

@dp.message_handler(state=Form.question)
async def savol_qabul_qilish(message: Message, state: FSMContext):
    chat_id = message.chat.id
    question = message.text
    user = message.from_user.full_name
    username = message.from_user.username

    async with state.proxy() as data:
        data['question'] = message.text
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO user_question(question, chat_id)
                    VALUES ('{question}', {chat_id})""")
                connection.commit()
        except:
            pass
    with connection.cursor() as cursor:
        cursor.execute('''SELECT message_id FROM user_question''')
        question_d = cursor.fetchall()[-1][0]


    await bot.send_message('-1001871700017', f'{chat_id}\n{question_d}-savol:\n{question}\n\nSavol beruvchi: {user}  @{username}', reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text='javob berish', callback_data=f'javob_{chat_id}_{question_d}')))
    await bot.send_message(chat_id, f'Sizning savolingiz raqami: {question_d}-savol\nMurojaatlar ko\'pligi sababidan javoblar kechikishi mumkin. Biroq imkon qadar tezroq javob berishga harakat qilamiz!')
    await state.finish()



@dp.callback_query_handler(lambda call: 'javob' in call.data)
async def javobber(call: CallbackQuery):
    a = call.data.split('_')[-1]
    print(call.data, a)

    with connection.cursor() as cursor:
        cursor.execute(f'''SELECT answer FROM user_question WHERE message_id = {a}''')
        b = cursor.fetchone()
        print(b[0])
        try:
            if b[0] == 0:
                await call.answer('Javob berildi ✅\nJavobingiz uchun raxmat', show_alert=True)
                await bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    # text=response,
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Javob berildi ✅', callback_data=f'javob_{a}'))
                )

                with connection.cursor() as cursor:
                    cursor.execute(f'''
                                UPDATE user_question
                                SET answer = 1
                                WHERE message_id = {a};
                                ''')
                    connection.commit()

            elif b[0] == 1:
                await call.answer('Javob bekor qilindi ❌\nJavobingiz uchun raxmat', show_alert=True)
                await bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    # text=response,
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Javob berish', callback_data=f'javob_{a}'))
                )

                with connection.cursor() as cursor:
                    cursor.execute(f'''
                                           UPDATE user_question
                                           SET answer = 0
                                           WHERE message_id = {a};
                                           ''')
                    connection.commit()
        except:
            pass
@dp.callback_query_handler(lambda call: 'accept' in call.data)
async def accept_aanswer(call: CallbackQuery):
    a = call.data.split('_')[-1]
    await call.answer('Qabul qilindi ✅\nJavobingiz uchun raxmat', show_alert=True)
    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        # text=response,
        reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Qabul qilindi ✅', callback_data='qabul'))
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'''UPDATE user_question
                            SET qabul = 1
                            WHERE message_id = {a}
                ''')
            connection.commit()

    except:
        pass

executor.start_polling(dp, skip_updates=True)

