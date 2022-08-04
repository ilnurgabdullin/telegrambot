from aiogram import types, Dispatcher

from create_bot import dp,bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import towar
# from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from keyboards import client_keyboards
from aiogram_calendar import dialog_cal_callback, DialogCalendar, SimpleCalendar, simple_cal_callback
from aiogram.dispatcher.filters import Text

dialod = towar.get_dialog()


class FSMClient(StatesGroup):
    register_name = State()
    register_gender = State()
    register_ok = State()
    register_date = State()
    register_phone = State()
    main_client = State()
    read_rules = State()
    choose_ticket = State()
    choose_date = State()
    choose_time = State()
    send_contact = State()
    cansel_ticket = State()


# =================>>>>>>>>>> REGISRTRATION <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> REGISRTRATION <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> REGISRTRATION <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> REGISRTRATION <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> REGISRTRATION <<<<<<<<<<<<<<========================


async def command_start(message: types.Message):
    if towar.is_exists(message.from_user.id) == 1: # проверяем есть клиент в базе
        await FSMClient.main_client.set()
        if dialod.get('start').count('{}') == 1:
            await message.answer(('Hello {}' if dialod.get('start') == '' else dialod.get('start')).format(towar.chek_aboniment(message.from_user.id)),
                             reply_markup=client_keyboards.main_menu_client
                             )
        else:
            await message.answer(
                text = dialod.get('start') if dialod.get('start') != '' else f'Hello {towar.chek_aboniment(message.from_user.id)}',
                reply_markup=client_keyboards.main_menu_client
                )
    elif towar.is_exists(message.from_user.id) == 0:
        await FSMClient.register_name.set()
        photo = open('brig.png', 'rb')
        if not (dialod.get('photo_caption') is None):
            await bot.send_photo(chat_id=message.from_user.id,photo = photo, caption=dialod.get('photo_caption'))
        await message.answer(dialod.get('ask_name','Шаг 1/4 \nНапишите Фамилию Имя Отчество (полностью)'))
    else:
        await message.answer(dialod.get('not_moder','Ваш аккаунт ещё не прошёл модерацию, это произойдёт в близжайшее время, извиняемся за задержку'))


async def wait_for_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data: # записываем имя нового пользователя в оперативную память
        data['name'] = message.text.replace(' ', '_')
        data['tgid'] = message.from_user.id
    await message.answer(dialod.get('ask_gender','Шаг 2/4 \nУкажите свой пол'),
                         reply_markup=client_keyboards.choose_gender_kb)
    await FSMClient.register_gender.set()


async def wait_for_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data: # сохраняем пол в оперативку
        data['gender'] = message.text.replace(' ', '_')
    await message.answer(dialod.get('ask_birthday','Шаг 3/4 \nУкажите свой день рождения'),
                         reply_markup=await DialogCalendar().start_calendar())
    await FSMClient.register_date.set()


async def wait_for_phone(message: types.Message, state: FSMContext):
    if message.content_type == types.ContentType.CONTACT:
        # получает от клиента номер телефона в виде контакта или строки
        phone = message.contact.phone_number
    else:
        phone = message.text.replace(' ', '_')
    async with state.proxy() as data:
        data['phone'] = phone
        # await message.edit_reply_markup(reply_markup=None)
        await message.answer(
                            'Уточним',
                            reply_markup=ReplyKeyboardRemove())
        await message.answer('Всё верно?\nВас зовут {}\nВы родились {}\nВаш номер телефона {}\n'.format(data.get('name').replace('_',' '),data.get('date'),data.get('phone')),
                             reply_markup=client_keyboards.ok_reg_kb)
        await FSMClient.register_ok.set()


async def back(message: types.Message,state:FSMContext):
    await state.reset_state()
    await state.reset_data()
    await message.answer("Очищено. Чтобы посмотреть каталог нажми на кнопки внизу",
                         reply_markup=client_keyboards.main_menu_client)
    await FSMClient.main_client.set()


@dp.callback_query_handler(state=FSMClient.register_ok)
async def ok_register_or_not_ok(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == 'ok':
        await bot.answer_callback_query(
                                        callback_query.id,
                                        text='Спасибо за регистрацию', show_alert=True)
        async with state.proxy() as data:
            towar.write_new([data.get('name'),data.get('date'),data.get('gender'),data.get('phone'),data.get('tgid'),0,False,False])
        await bot.send_message(chat_id=data.get('tgid'), text='Добро пожаловать в бригаду. Moderation, please wait, click /start to learn more')
        await bot.send_message(chat_id=644356793, text='новый пользователь')
        await state.reset_state()
        await state.reset_data()
        await callback_query.message.delete()
    else:
        await FSMClient.register_name.set()
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.delete()
        await callback_query.message.answer('Начнем заново, шаг 1/4 \nНапишите Фамилию Имя Отчество (полностью)')


@dp.callback_query_handler(dialog_cal_callback.filter(),state=FSMClient.register_date)
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['date'] = date.strftime("%d.%m.%Y")
        await callback_query.message.delete()
        await callback_query.message.answer(
            dialod.get('ask_phone', 'Шаг 4/4 \nУкажите свой номер телефона'),
            reply_markup=client_keyboards.phone_kb)
        await FSMClient.register_phone.set()


# =================>>>>>>>>>> ГЛАВНОЕ МЕНЮ <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> ГЛАВНОЕ МЕНЮ <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> ГЛАВНОЕ МЕНЮ <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> ГЛАВНОЕ МЕНЮ <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> ГЛАВНОЕ МЕНЮ <<<<<<<<<<<<<<========================


@dp.callback_query_handler(state=FSMClient.main_client)
async def main_menu(callback_query: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    if callback_query.data == 'bind_time':
        await callback_query.message.answer('Выберите время:',
                                reply_markup=await SimpleCalendar().start_calendar())
        await FSMClient.choose_date.set()
    elif callback_query.data == 'buy_ticket':
        await callback_query.message.answer(
            'Какой абонимент вам подойдёт:', reply_markup=client_keyboards.buy_ticket_kb)
        await FSMClient.choose_ticket.set()
    elif callback_query.data == 'cancel_record':
        reply_keyboard = client_keyboards.cancel_ticket_kb(towar.look_user_info(callback_query.from_user.id))
        if reply_keyboard !=False:
            await callback_query.message.answer(
                'Какую запись удалить:', reply_markup=reply_keyboard)
            await FSMClient.cansel_ticket.set()
        else:
            await callback_query.answer(
                'Вы ещё не записались на занятия',show_alert=True)
            await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                                                reply_markup=client_keyboards.main_menu_client
                                                )
            await FSMClient.main_client.set()
    elif callback_query.data == 'rules':
        file = open('rules.pdf','rb')
        await bot.send_document(chat_id=callback_query.from_user.id,
                                document=file,
                                caption='Правила нашего клуба',
                                reply_markup=client_keyboards.rules_kb)
        await FSMClient.read_rules.set()
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)


# =================>>>>>>>>>> КУПИТЬ АБОНИМЕНТ <<<<<<<<<<<<<<========================


@dp.callback_query_handler(state=FSMClient.choose_ticket)
async def main_menu(callback_query: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id
    )
    if 'buy_tiket' in callback_query.data:
        colwo = int(callback_query.data.split('#')[-1])
        await bot.answer_callback_query(callback_query.id,show_alert=True)
        await bot.send_message(chat_id=callback_query.from_user.id, text='Вам начисленно '+str(colwo)+' занятий')
        towar.update_tiket(tgid=callback_query.from_user.id, kolvo=colwo)
        towar.write_transaktion(tgid=callback_query.from_user.id, kolvo=colwo)
    dialod = towar.get_dialog()
    if '{}' in dialod.get('start'):
        await callback_query.message.answer(dialod.get('start', 'Hello {}').format(towar.chek_aboniment(callback_query.from_user.id)),
                             reply_markup=client_keyboards.main_menu_client
                             )
    else:
        await callback_query.message.answer(
            dialod.get('start', f'Hello {towar.chek_aboniment(callback_query.from_user.id)}'),
            reply_markup=client_keyboards.main_menu_client
        )

    await FSMClient.main_client.set()


# =================>>>>>>>>>> ВЫБРАТЬ ВРЕМЯ ДЛЯ ЗАПИСИ <<<<<<<<<<<<<<================


@dp.message_handler(Text(equals=['Navigation Calendar'], ignore_case=True))
async def nav_cal_handler(message: types.Message):
    await message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())


# simple calendar usage
@dp.callback_query_handler(simple_cal_callback.filter(),state=FSMClient.choose_date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        data = towar.look_free_trains(date.strftime("%d.%m.%Y"))
        keybord = client_keyboards.create_choose_time_kb(data)
        if keybord == False:
            await callback_query.message.answer(
            f'You selected {date.strftime("%d.%m.%Y")} на этот день нет свободного времени',
                reply_markup=await SimpleCalendar().start_calendar()
        )
        else:
            await callback_query.message.answer(
                f'You selected {date.strftime("%d.%m.%Y")}',
                reply_markup= keybord
            )
            await FSMClient.choose_time.set()
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)


@dp.callback_query_handler(state=FSMClient.read_rules)
async def bind_time_client(callback_query: CallbackQuery):
    if callback_query.data == 'back':
        await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                                            reply_markup=client_keyboards.main_menu_client
                                            )
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
        await FSMClient.main_client.set()


@dp.callback_query_handler(state=FSMClient.choose_time)
async def bind_time_client(callback_query: CallbackQuery):
    if callback_query.data == 'back':
        await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                                            reply_markup=client_keyboards.main_menu_client
                                            )
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await FSMClient.main_client.set()
    elif towar.chek_aboniment(callback_query.from_user.id) <= 0:
        await bot.answer_callback_query(
            callback_query.id,
            text='Нет абонимента, преобретите его')
        await FSMClient.main_client.set()
        await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                                            reply_markup=client_keyboards.main_menu_client
                                            )
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
    elif 'list' in callback_query.data:
        data = towar.look_free_trains(callback_query.data[4:])
        data_all = towar.look_all_trains(callback_query.data[4:])
        reply = f'Записи на сегодня {callback_query.data[4:]}:'
        times = []
        for t in data_all:
            for i in t[2]:
                name = towar.take_name_by_id(int(*i))
                if name != '':
                    if not(t[1] in times):
                        times.append(t[1])
                        reply +='\n' + str(t[1]) +' '+ towar.take_type_by_time(callback_query.data[4:],str(t[1])) + ':\n' + name + '\n'
                    else:
                        reply += name + '\n'
        keybord = client_keyboards.create_choose_time_kb(data,False)
        await bot.send_message(
                               chat_id=callback_query.from_user.id,
                               text = reply,
                               reply_markup=keybord
        )
    else:
        text = towar.bind_train(*callback_query.data.split(),callback_query.from_user.id)
        await bot.answer_callback_query(
            callback_query.id,
            text=text)
        await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                                            reply_markup=client_keyboards.main_menu_client
                                            )
        await callback_query.message.answer(f'Вы записаны на занятие в {callback_query.data.split()[0]}, {callback_query.data.split()[1]}')
        await FSMClient.main_client.set()
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
# =================>>>>>>>>>> ОТМЕНИТЬ ЗАПИСЬ <<<<<<<<<<<<<<========================


@dp.callback_query_handler(state=FSMClient.cansel_ticket)
async def cansel_ticket(callback_query: CallbackQuery):
    if callback_query.data == 'back':
        await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                                            reply_markup=client_keyboards.main_menu_client
                                            )
    else:
        towar.delete_binded_time(callback_query.data)
        await callback_query.message.answer(f'Привет друг, что будем делать?\nУ вас ещё {towar.chek_aboniment(callback_query.from_user.id)} занятий',
                             reply_markup=client_keyboards.main_menu_client
                                            )
    await FSMClient.main_client.set()
    await bot.delete_message(callback_query.from_user.id,callback_query.message.message_id)

# =================>>>>>>>>>> КУПИТЬ АБОНИМЕНТ <<<<<<<<<<<<<<========================
# =================>>>>>>>>>> КУПИТЬ АБОНИМЕНТ <<<<<<<<<<<<<<========================


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start,state='*',commands=['start','help'])
    dp.register_message_handler(wait_for_name,state=FSMClient.register_name)
    dp.register_message_handler(wait_for_gender,state=FSMClient.register_gender)
    dp.register_message_handler(wait_for_phone,state=FSMClient.register_phone,content_types=[types.ContentType.CONTACT,types.ContentType.TEXT])
