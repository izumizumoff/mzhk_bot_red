# main module
import json
import asyncio
import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, user
from aiogram.utils import executor
from vk_api.exceptions import VkAudioException
import config


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
admin = config.ADMIN_ID

config.random_face()

USERS = {}

# регистрация по группам
USR_GROUP_1 = []
USR_GROUP_2 = []
USR_GROUP_3 = []
# регистрация по частям
PART_1_G1 = []
PART_1_G2 = []
PART_1_G3 = []

PART_2_G1 = []
PART_2_G2 = []
PART_2_G3 = []

PART_3_G1 = []
PART_3_G2 = []
PART_3_G3 = []

# индикатор запущенного спектакля
FLAG = 0

# функция переключения хода
def turn_up(index,lenth):
    if index == lenth - 1:
        return 0
    else:
        return index + 1


# форма для хранения в памяти ввода имени пользователя
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'

@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):

    if FLAG == 0:

        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        # default row_width is 3, so here we can omit it actually
        # kept for clearness

        text_and_data = (
            ('ЖМИ ЗДЕСЬ, чтобы начать', config.ID_PLAY),
        )
        # in real life for the callback_data the callback data factory should be used
        # here the raw string is used for the simplicity
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)

        keyboard_markup.row(*row_btns)

        with open('label_for_bot.jpg', 'rb') as label:
            await message.answer_photo(label, config.AUTHORS, reply_markup=keyboard_markup)



        # обработка нажатия кнопки
        @dp.callback_query_handler(text=config.ID_PLAY) 
        async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
            answer_data = query.data
            # always answer callback queries, even if you have nothing to say
            await query.answer('Спектакль начался')

            if answer_data == config.ID_PLAY and FLAG == 0:
                await types.ChatActions.typing()
                
                with open('random_face.jpg', 'rb') as face:
                    await bot.send_photo(query.from_user.id, face, config.START_MESSAGE[0])

                await Form.name.set()

                await types.ChatActions.typing()
                await asyncio.sleep(5)
                await bot.send_message(query.from_user.id, "Как я могу к вам обращаться? Как вас зовут?")


                # обработка запроса имени и сохранение в локальной переменной
                @dp.message_handler(state='*', commands='cancel')
                @dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
                async def cancel_handler(message: types.Message, state: FSMContext):
                    """
                    Allow user to cancel any action
                    """
                    current_state = await state.get_state()
                    if current_state is None:
                        return

                    logging.info('Cancelling state %r', current_state)
                    # Cancel state and inform user about it
                    await state.finish()
                    # And remove keyboard (just in case)
                    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


                @dp.message_handler(state=Form.name)
                async def process_name(message: types.Message, state: FSMContext):
                    """
                    Process user name
                    """
                    async with state.proxy() as data:
                        data['name'] = message.text
                    # Finish conversation
                    await state.finish()
                    USERS[message.from_user.id] = data['name']
                    with open('users.json', 'w') as file:
                        json.dump(USERS, file, ensure_ascii = False)

                    await types.ChatActions.typing()
                    await asyncio.sleep(5)
                    await message.reply(f"Очень приятно, {data['name']}")

                    
                    
                    

                    info_reg = ''
                    for usr in USERS:
                        info_reg = info_reg + USERS[usr] + '\n'
                    await bot.send_message(config.ADMIN_ID, f'<b>Новый список участников:</b> \n <i>{info_reg}</i>')

                    await types.ChatActions.typing()
                    await asyncio.sleep(5)
                    await bot.send_message(message.from_user.id, config.START_MESSAGE[1])
                    await types.ChatActions.typing()
                    await asyncio.sleep(6)

                    await bot.send_message(message.from_user.id, config.START_MESSAGE[2])
                    await types.ChatActions.typing()
                    await asyncio.sleep(6)

                    await bot.send_message(message.from_user.id, config.START_MESSAGE[3])



                    
            else:
                await bot.send_message(query.from_user.id,'Извините, но спектакль уже идет или закончился!')
    else:
        pass
    

# сохранение текущих зрителей в отдельном json
@dp.message_handler(commands='save')
async def save(message: types.Message):
    global USERS

    global USR_GROUP_1
    global USR_GROUP_2
    global USR_GROUP_3

    global PART_1_G1
    global PART_1_G2
    global PART_1_G3

    global PART_2_G1
    global PART_2_G2
    global PART_2_G3

    global PART_3_G1
    global PART_3_G2
    global PART_3_G3

    global FLAG
    

    with open('users.json', 'r') as file:
        USERS = json.load(file)
    


    if len(USERS) == 1:
        FLAG = 1
        for x in sorted(list(USERS)):
            
            USR_GROUP_1.append((x, USERS[x]))    

            PART_1_G1.append(x)
            PART_2_G1.append(x)
            PART_3_G1.append(x)


    elif len(USERS) == 2:
        FLAG = 2
        for x in sorted(list(USERS)):
            if (sorted(list(USERS)).index(x) + 1) % 2 == 0:
                
                USR_GROUP_2.append((x, USERS[x]))
                PART_1_G2.append(x)
                PART_2_G2.append(x)
                PART_3_G2.append(x)
            else:
                
                USR_GROUP_1.append((x, USERS[x]))
                PART_1_G1.append(x)
                PART_2_G1.append(x)
                PART_3_G1.append(x)

    elif len(USERS) > 2:
        FLAG = 3
        for x in sorted(list(USERS)):
            if (sorted(list(USERS)).index(x) + 1) % 2 == 0:
                
                USR_GROUP_2.append((x, USERS[x]))
                PART_1_G2.append(x)
                PART_2_G2.append(x)
                PART_3_G2.append(x)
            elif (sorted(list(USERS)).index(x) + 1) % 3 == 0:
                
                USR_GROUP_3.append((x, USERS[x]))
                PART_1_G3.append(x)
                PART_2_G3.append(x)
                PART_3_G3.append(x)
            elif (sorted(list(USERS)).index(x) + 1) % 3 != 0 and (sorted(list(USERS)).index(x) + 1)%2 != 0:
                
                USR_GROUP_1.append((x, USERS[x]))
                PART_1_G1.append(x)
                PART_2_G1.append(x)
                PART_3_G1.append(x)
            else:
                print('error with reg')

        

    else:
        pass



    USR_GROUP_1 = list(set(USR_GROUP_1))
    USR_GROUP_2 = list(set(USR_GROUP_2))
    USR_GROUP_3 = list(set(USR_GROUP_3))

    PART_1_G1 = list(set(PART_1_G1))
    PART_1_G2 = list(set(PART_1_G2))
    PART_1_G3 = list(set(PART_1_G3))

    PART_2_G1 = list(set(PART_2_G1))
    PART_2_G2 = list(set(PART_2_G2))
    PART_2_G3 = list(set(PART_2_G3))

    PART_3_G1 = list(set(PART_3_G1))
    PART_3_G2 = list(set(PART_3_G2))
    PART_3_G3 = list(set(PART_3_G3))
    

    
    info_group = '<b>Первая группа:</b>\n'
    for g1 in USR_GROUP_1:
        info_group = info_group + f'<i>{g1[0]}: {g1[1]}</i>\n'
    info_group = info_group + '<b>\n\nВторая группа:</b>\n'
    for g2 in USR_GROUP_2:
        info_group = info_group + f'<i>{g2[0]}: {g2[1]}</i>\n'
    info_group = info_group + '<b>\n\nТретья группа:</b>\n'
    for g3 in USR_GROUP_3:
        info_group = info_group + f'<i>{g3[0]}: {g3[1]}</i>\n'
    await bot.send_message(config.ADMIN_ID, info_group)
    await bot.send_message(message.from_user.id, info_group)



# запуск спектакля
@dp.message_handler(commands='play')
async def send_play(message: types.Message):

    global USERS

    await bot.send_message(config.ADMIN_ID,'Спектакль запущен')
    await bot.send_message(message.from_user.id,'Спектакль запущен')


    for user in USERS:
        with open('pic_roman.jpg', 'rb') as pic:
            await bot.send_photo(int(user), pic, f'Добрый день, <b>{USERS[user]}</b> {config.INTRO_MESSSAGE[0]}')

    for user in USERS:
        await types.ChatActions.typing()
        await asyncio.sleep(7)

        await bot.send_message(int(user), config.INTRO_MESSSAGE[1])

    for user in USERS:
        await types.ChatActions.typing()
        await asyncio.sleep(10)

        await bot.send_message(int(user), config.INTRO_MESSSAGE[2])

    for user in USERS:
        await types.ChatActions.typing()
        await asyncio.sleep(10)

        await bot.send_message(int(user), config.INTRO_MESSSAGE[3])

    for user in USERS:
        await types.ChatActions.typing()
        await asyncio.sleep(8)

        await bot.send_message(int(user), config.INTRO_MESSSAGE[4])

        
    for user in USERS:
        # смена частей
        await types.ChatActions.typing()
        await asyncio.sleep(4)


        # кнопка готовности в квартире
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        # default row_width is 3, so here we can omit it actually
        # kept for clearness

        text_and_data = (
            ('Я В ПРИХОЖЕЙ', 'inside'),
        )
        # in real life for the callback_data the callback data factory should be used
        # here the raw string is used for the simplicity
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)

        keyboard_markup.row(*row_btns)

        await bot.send_message(int(user), 'Как окажетесь в прихожей, жми кнопку', reply_markup=keyboard_markup)

        @dp.callback_query_handler(text='inside')
        async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
            answer_data = query.data
            # always answer callback queries, even if you have nothing to say
            await query.answer('Вы пришли в прихожую')

            if answer_data == 'inside':
                await types.ChatActions.typing()
                await asyncio.sleep(6)
                await bot.send_message(query.from_user.id,config.INSIDE_MESSSAGE[0])

                await types.ChatActions.typing()
                await asyncio.sleep(8)
                await bot.send_message(query.from_user.id,config.INSIDE_MESSSAGE[1])

                await types.ChatActions.typing()
                await asyncio.sleep(8)
                await bot.send_message(query.from_user.id,config.INSIDE_MESSSAGE[2])

                await types.ChatActions.typing()
                await asyncio.sleep(6)

                if str(query.from_user.id) in [x[0] for x in USR_GROUP_1]:
                    # кнопка на клавиатуре
                    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard_markup.add(types.KeyboardButton('Часть Первая. Кухня'))
                    await bot.send_message(query.from_user.id, "Пройдемте на кухню. Как дойдете - жмите на кнопку ниже", reply_markup=keyboard_markup)
                elif str(query.from_user.id) in [x[0] for x in USR_GROUP_2]:
                    # кнопка на клавиатуре
                    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard_markup.add(types.KeyboardButton('Часть Первая. Гостиная'))
                    await bot.send_message(query.from_user.id, "Пройдемте в гостиную. Как дойдете - жмите на кнопку ниже", reply_markup=keyboard_markup)
                elif str(query.from_user.id) in [x[0] for x in USR_GROUP_3]:
                    # кнопка на клавиатуре
                    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard_markup.add(types.KeyboardButton('Часть Первая. Кабинет'))
                    await bot.send_message(query.from_user.id, "Пройдемте в мой кабинет (в конце коридора и направо). Как дойдете - жмите на кнопку ниже", reply_markup=keyboard_markup)
                else:
                    await bot.send_message(config.ADMIN_ID, "Ошибка")

            else:
                await bot.send_message(query.from_user.id,'Что-то нажали не то!')


# !!! ЧАСТЬ ПЕРВАЯ !!!
######################

# на кухне
@dp.message_handler(text='Часть Первая. Кухня')
async def send_play(message: types.Message):
    global PART_1_G1

    if str(message.from_user.id) in PART_1_G1:
        PART_1_G1.remove(str(message.from_user.id))
        if PART_1_G1:
            other = ', '.join(PART_1_G1)
            await bot.send_message(message.from_user.id, f'Добро пожаловать на кухне. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:
            index = 0

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.KITCHEN_MESSAGE, reply_markup=types.ReplyKeyboardRemove())

            await asyncio.sleep(5)

            # здесь играет радио
            config.device_turn('radio_on')

            for usr in USR_GROUP_1:
                with open('novoselie.gif', 'rb') as photo:
                    await bot.send_animation(usr[0], photo, config.KITCHEN_PHOTO, reply_markup=types.ReplyKeyboardRemove())

            with open('VOICE/radio.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[index][0], voice, 'Так играло радио')
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/1_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[index][0], voice, '#1 Это я говорю Лизе. Она слишком серьезно готовится к новоселью')
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/2_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#2 А она все о своем')
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/3_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#3 Это я')
                #print(index)
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/4_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#4 А это она')
                #print(index)
            await asyncio.sleep(10)
            
            with open('VOICE/kitchen_list/5_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#5 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/6_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#6 Она')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/7_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#7 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/8_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#8 Она')
                #print(index)
            await asyncio.sleep(12)

            with open('VOICE/kitchen_list/9_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#9 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/10_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#10 И, наконец, она сказала')
                #print(index)
            await asyncio.sleep(10)

            # здесь играет радио
            config.device_turn('radio_off')

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.ANEKDOT_MESSAGE)
            
            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Часть Вторая. Гостиная'))
            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], "Пройдите в гостиную (большая комната с пианино)\nКа будете готовы - жмите на кнопку внизу", reply_markup=keyboard_markup)
            
    else:
        pass

# в гостинной
@dp.message_handler(text='Часть Первая. Гостиная')
async def send_play(message: types.Message):
    global PART_1_G2

    if str(message.from_user.id) in PART_1_G2:
        PART_1_G2.remove(str(message.from_user.id))
        if PART_1_G2:
            other = ', '.join(PART_1_G2)
            await bot.send_message(message.from_user.id, f'Добро пожаловать в гостиной. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:
            index = 0

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.BIGROOM_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
            
            await asyncio.sleep(15)

            # здесь включился телевизор
            config.device_turn('tv_on')

            await asyncio.sleep(15)

            # здесь включился телевизор
            config.device_turn('cat')

            with open('VOICE/big_room_list/1_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[index][0], voice, '#1 А это Лиза мешает моей безмятежной жизни у экрана')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/2_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#2 А это я - борюсь за свои права')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/3_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#3 А это снова Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/4_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#4 Я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/5_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#5 Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/6_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#6 Я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/7_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#7 Снова я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/8_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#8 Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/9_bigroom_all.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#9 а это мы вместе, а Машутка с нами')
            await asyncio.sleep(15)

            await asyncio.sleep(5)

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.BIGROOM_FINAL_MESSAGE)
            
            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Часть Вторая. Кабинет'))
            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], "Пройдите в мой кабинет (в конце коридора и направо)\nКак будете готовы - жмите на кнопку внизу", reply_markup=keyboard_markup)
            
    else:
        pass

# в кабинете
@dp.message_handler(text='Часть Первая. Кабинет')
async def send_play(message: types.Message):
    global PART_1_G3

    if str(message.from_user.id) in PART_1_G3:
        PART_1_G3.remove(str(message.from_user.id))
        if PART_1_G3:
            other = ', '.join(PART_1_G3)
            await bot.send_message(message.from_user.id, f'Добро пожаловать в моем кабинете. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.KABINET_MESSAGE[0], reply_markup=types.ReplyKeyboardRemove())
            
            await asyncio.sleep(15)

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.KABINET_MESSAGE[1])
            await asyncio.sleep(5)

            # включается бобийник
            config.device_turn('kabinet_on')
            await asyncio.sleep(200)
            config.device_turn('kabinet_off')

            with open('VOICE/kabinet_voice.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[0][0], voice, 'Люблю ее голос')

            await asyncio.sleep(10)

            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Часть Вторая. Кухня'))
            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], "Пройдите на кухню\nКа будете готовы - жмите на кнопку внизу", reply_markup=keyboard_markup)
    else:
        pass



# !!! ЧАСТЬ ВТОРАЯ !!!
######################

# на кухне
@dp.message_handler(text='Часть Вторая. Кухня')
async def send_play(message: types.Message):
    global PART_2_G3

    if str(message.from_user.id) in PART_2_G3:
        PART_2_G3.remove(str(message.from_user.id))
        if PART_2_G3:
            other = ', '.join(PART_2_G3)
            await bot.send_message(message.from_user.id, f'Добро пожаловать на кухне. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:
            index = 0

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.KITCHEN_MESSAGE, reply_markup=types.ReplyKeyboardRemove())

            # здесь играет радио
            config.device_turn('radio_on')

            await asyncio.sleep(5)

            for usr in USR_GROUP_3:
                with open('novoselie.gif', 'rb') as photo:
                    await bot.send_animation(usr[0], photo, config.KITCHEN_PHOTO, reply_markup=types.ReplyKeyboardRemove())

            with open('VOICE/radio.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[index][0], voice, 'Так играло радио')
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/1_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[index][0], voice, '#1 Это я говорю Лизе. Она слишком серьезно готовится к новоселью')
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/2_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#2 А она все о своем')
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/3_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#3 Это я')
                #print(index)
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/4_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#4 А это она')
                #print(index)
            await asyncio.sleep(10)
            
            with open('VOICE/kitchen_list/5_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#5 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/6_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#6 Она')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/7_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#7 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/8_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#8 Она')
                #print(index)
            await asyncio.sleep(12)

            with open('VOICE/kitchen_list/9_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#9 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/10_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#10 И, наконец, она сказала')
                #print(index)
            await asyncio.sleep(10)

            # здесь играет радио
            config.device_turn('radio_off')
            
            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.ANEKDOT_MESSAGE)

            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Часть Третья. Гостиная'))
            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], "Пройдите в гостиную (большая комната с пианино)\nКак будете готовы - жмите на кнопку внизу", reply_markup=keyboard_markup)
            
    else:
        pass

# в гостинной
@dp.message_handler(text='Часть Вторая. Гостиная')
async def send_play(message: types.Message):
    global PART_2_G1

    if str(message.from_user.id) in PART_2_G1:
        PART_2_G1.remove(str(message.from_user.id))
        if PART_2_G1:
            other = ', '.join(PART_2_G1)
            await bot.send_message(message.from_user.id, f'Добро пожаловать в гостиной. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:
            index = 0

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.BIGROOM_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
            
            await asyncio.sleep(15)

            # здесь включился телевизор
            config.device_turn('tv_on')

            await asyncio.sleep(15)

            # здесь включился телевизор
            config.device_turn('cat')

            with open('VOICE/big_room_list/1_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[index][0], voice, '#1 А это Лиза мешает моей безмятежной жизни у экрана')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/2_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#2 А это я - борюсь за свои права')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/3_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#3 А это снова Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/4_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#4 Я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/5_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#5 Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/6_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#6 Я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/7_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#7 Снова я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/8_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#8 Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/9_bigroom_all.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[turn_up(index, len(USR_GROUP_1))][0], voice, '#9 а это мы вместе, а Машутка с нами')
            await asyncio.sleep(15)

            await asyncio.sleep(5)

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.BIGROOM_FINAL_MESSAGE)
            
            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Часть Третья. Кабинет'))
            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], "Пройдите в мой кабинет (в конце коридора и направо)\nКа будете готовы - жмите на кнопку внизу", reply_markup=keyboard_markup)
            
    else:
        pass


# в кабинете
@dp.message_handler(text='Часть Вторая. Кабинет')
async def send_play(message: types.Message):
    global PART_2_G2

    if str(message.from_user.id) in PART_2_G2:
        PART_2_G2.remove(str(message.from_user.id))
        if PART_2_G2:
            other = ', '.join(PART_2_G2)
            await bot.send_message(message.from_user.id, f'Добро пожаловать в моем кабинете. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.KABINET_MESSAGE[0], reply_markup=types.ReplyKeyboardRemove())
            
            await asyncio.sleep(15)

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.KABINET_MESSAGE[1])
            await asyncio.sleep(5)

            # включается бобийник
            config.device_turn('kabinet_on')
            await asyncio.sleep(200)
            config.device_turn('kabinet_off')

            with open('VOICE/kabinet_voice.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[0][0], voice, 'Люблю ее голос')

            await asyncio.sleep(10)

            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Часть Третья. Кухня'))
            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], "Пройдите на кухню\nКа будете готовы - жмите на кнопку внизу", reply_markup=keyboard_markup)
    else:
        pass


# !!! ЧАСТЬ ТРЕТЬЯ !!!
######################


# на кухне
@dp.message_handler(text='Часть Третья. Кухня')
async def send_play(message: types.Message):
    global PART_3_G2

    if str(message.from_user.id) in PART_3_G2:
        PART_3_G2.remove(str(message.from_user.id))
        if PART_3_G2:
            other = ', '.join(PART_3_G2)
            await bot.send_message(message.from_user.id, f'Добро пожаловать на кухне. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:
            index = 0

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.KITCHEN_MESSAGE, reply_markup=types.ReplyKeyboardRemove())

            await asyncio.sleep(5)

            # здесь играет радио
            config.device_turn('radio_on')

            for usr in USR_GROUP_2:
                with open('novoselie.gif', 'rb') as photo:
                    await bot.send_animation(usr[0], photo, config.KITCHEN_PHOTO, reply_markup=types.ReplyKeyboardRemove())

            with open('VOICE/radio.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[index][0], voice, 'Так играло радио')
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/1_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[index][0], voice, '#1 Это я говорю Лизе. Она слишком серьезно готовится к новоселью')
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/2_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#2 А она все о своем')
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/3_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#3 Это я')
                #print(index)
            await asyncio.sleep(15)

            with open('VOICE/kitchen_list/4_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#4 А это она')
                #print(index)
            await asyncio.sleep(10)
            
            with open('VOICE/kitchen_list/5_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#5 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/6_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#6 Она')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/7_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#7 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/8_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#8 Она')
                #print(index)
            await asyncio.sleep(12)

            with open('VOICE/kitchen_list/9_kitchen_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#9 Я')
                #print(index)
            await asyncio.sleep(10)

            with open('VOICE/kitchen_list/10_kitchen_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_2[turn_up(index, len(USR_GROUP_2))][0], voice, '#10 И, наконец, она сказала')
                #print(index)
            await asyncio.sleep(5)

            # здесь играет радио
            config.device_turn('radio_off')

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.PART3_MESSSAGE[0])
            await asyncio.sleep(5)

            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.PART3_MESSSAGE[1])
            await asyncio.sleep(10)
            
            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], config.ANEKDOT_MESSAGE)

            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Финал'))
            for usr in USR_GROUP_2:
                await bot.send_message(usr[0], "Пройдите в детскую", reply_markup=keyboard_markup)
            
    else:
        pass

# в гостинной
@dp.message_handler(text='Часть Третья. Гостиная')
async def send_play(message: types.Message):
    global PART_3_G3

    if str(message.from_user.id) in PART_3_G3:
        PART_3_G3.remove(str(message.from_user.id))
        if PART_3_G3:
            other = ', '.join(PART_3_G3)
            await bot.send_message(message.from_user.id, f'Добро пожаловать в гостиной. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:
            index = 0

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.BIGROOM_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
            
            await asyncio.sleep(15)

            # здесь включился телевизор
            config.device_turn('tv_on')

            await asyncio.sleep(15)

            # здесь включился телевизор
            config.device_turn('cat')

            with open('VOICE/big_room_list/1_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[index][0], voice, '#1 А это Лиза мешает моей безмятежной жизни у экрана')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/2_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#2 А это я - борюсь за свои права')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/3_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#3 А это снова Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/4_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#4 Я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/5_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#5 Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/6_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#6 Я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/7_bigroom_he.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#7 Снова я')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/8_bigroom_she.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#8 Лиза')
            await asyncio.sleep(15)

            with open('VOICE/big_room_list/9_bigroom_all.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_3[turn_up(index, len(USR_GROUP_3))][0], voice, '#9 а это мы вместе, а Машутка с нами')
            await asyncio.sleep(15)

            await asyncio.sleep(5)

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.BIGROOM_FINAL_MESSAGE)

            await asyncio.sleep(5)

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.PART3_MESSSAGE[0])
            await asyncio.sleep(5)

            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], config.PART3_MESSSAGE[1])
            await asyncio.sleep(5)
            
            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Финал'))
            for usr in USR_GROUP_3:
                await bot.send_message(usr[0], "Пройдите в детскую", reply_markup=keyboard_markup)
            
    else:
        pass


# в кабинете
@dp.message_handler(text='Часть Третья. Кабинет')
async def send_play(message: types.Message):
    global PART_3_G1

    if str(message.from_user.id) in PART_3_G1:
        PART_3_G1.remove(str(message.from_user.id))
        if PART_3_G1:
            other = ', '.join(PART_3_G1)
            await bot.send_message(message.from_user.id, f'Добро пожаловать в моем кабинете. Подождите немного, {other} еще не готовы', reply_markup=types.ReplyKeyboardRemove())
        else:

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.KABINET_MESSAGE[0], reply_markup=types.ReplyKeyboardRemove())
            
            await asyncio.sleep(15)

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.KABINET_MESSAGE[1])
            await asyncio.sleep(5)

            # включается бобийник
            config.device_turn('kabinet_on')
            await asyncio.sleep(200)
            config.device_turn('kabinet_off')

            with open('VOICE/kabinet_voice.mp3', 'rb') as voice:
                await bot.send_voice(USR_GROUP_1[0][0], voice, 'Люблю ее голос')

            await asyncio.sleep(10)

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.PART3_MESSSAGE[0])
            await asyncio.sleep(5)

            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], config.PART3_MESSSAGE[1])
            await asyncio.sleep(5)

            # кнопка на клавиатуре
            keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_markup.add(types.KeyboardButton('Финал'))
            for usr in USR_GROUP_1:
                await bot.send_message(usr[0], "Пройдите в детскую. Ключь от замочка в ванной, на раковине", reply_markup=keyboard_markup)
    else:
        pass

# в кабинете
@dp.message_handler(text='Финал')
async def send_play(message: types.Message):
    global USERS

    for x in config.FINAL_MESSSAGE:

        await types.ChatActions.typing()
        await asyncio.sleep(8)
        await bot.send_message(message.from_user.id, x, reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(200)
    await bot.send_message(message.from_user.id, 'Вот и все, что я хотел вам рассказать. Спасибо за внимание. Уходя, не забывайте свои вещи')
    await asyncio.sleep(15)
    await bot.send_message(message.from_user.id, 'А вместо послесловия - музыкальный МЖКовский привет\n\nP.S. В этом клипе вы могли бы увидеть меня')  
    await bot.send_video(message.from_user.id, config.CLIP_ID)


@dp.message_handler(commands='reset')
async def reset(message: types.Message):
    global USERS

    global USR_GROUP_1
    global USR_GROUP_2
    global USR_GROUP_3

    global PART_1_G1
    global PART_1_G2
    global PART_1_G3

    global PART_2_G1
    global PART_2_G2
    global PART_2_G3

    global PART_3_G1
    global PART_3_G2
    global PART_3_G3

    global FLAG

    USERS = {}
    with open('users.json', 'w') as file:
        json.dump(USERS, file, ensure_ascii = False)

    # регистрация по группам
    USR_GROUP_1 = []
    USR_GROUP_2 = []
    USR_GROUP_3 = []
    # регистрация по частям
    PART_1_G1 = []
    PART_1_G2 = []
    PART_1_G3 = []

    PART_2_G1 = []
    PART_2_G2 = []
    PART_2_G3 = []

    PART_3_G1 = []
    PART_3_G2 = []
    PART_3_G3 = []

    # индикатор запущенного спектакля
    FLAG = 0

    config.random_face()
    await bot.send_message(config.ADMIN_ID,'Все данные сброшены')
    await bot.send_message(message.from_user.id,'Все данные сброшены')

@dp.message_handler(content_types=['video'])
async def parse_id(message: types.Message):
    print(message.video.file_id)   


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)