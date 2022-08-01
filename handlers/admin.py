from aiogram import types, Dispatcher
from aiogram.types import CallbackQuery
import towar
from create_bot import dp, bot
from keyboards import admin_keyboards
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_calendar import SimpleCalendar, simple_cal_callback
from aiogram.dispatcher.filters import Text


class FSMAdmin(StatesGroup):
    main_admin_state = State()
    add_users = State()
    add_new_times = State()
    choose_time_to_delete = State()
    choose_new_time = State()
    wait_for_deskriptoin =State()


admin_id = 644356793


async def chek_admin(message: types.Message):
    if message.from_user.id == admin_id:
        await message.answer('Comands:',
                             reply_markup=admin_keyboards.main_admin_kb)
        await FSMAdmin.main_admin_state.set()


async def restart_admin(message: int):
    if message == admin_id:
        await bot.send_message(chat_id=message,text='Comands:',
                               reply_markup=admin_keyboards.main_admin_kb)
        await FSMAdmin.main_admin_state.set()


def dict_from_string(start: str) -> list:
    return_data = list(start.replace("'", '').replace(",", '').split('#'))
    return return_data


async def moderation(message: types.Message):
    data = towar.view_new_user()
    if len(data) > 0:
        for i in towar.view_new_user():
            await bot.send_message(chat_id=admin_id, text='{}#{}#{}#{}#{}'.format(*i),
                                   reply_markup=admin_keyboards.moderation_admin_keyboard)
    else:
        await message.answer('Нет новых пользователей')


async def admin_new_time(message: types.Message):
    await FSMAdmin.add_new_times.set()
    await message.answer('На какой день делаем тренировку?',
                         reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(state=FSMAdmin.choose_time_to_delete)
async def delete_time(callback_query: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    if callback_query.data == 'back':
        await restart_admin(callback_query.from_user.id)
    else:
        print(callback_query.data.split('_'))
        towar.delete_time(*callback_query.data.split('_'))
        await callback_query.answer(text='Время удалено')
        await FSMAdmin.main_admin_state.set()


async def delete_time_by_admin(message: types.Message):
    await message.answer('What will we delete',
                         reply_markup=admin_keyboards.create_delete_time(towar.find_old_binds()))
    await FSMAdmin.choose_time_to_delete.set()


@dp.callback_query_handler(state=FSMAdmin.main_admin_state)
async def moderation_users(callback_query: CallbackQuery, state: FSMContext):
    if 'add' == callback_query.data:
        await bot.answer_callback_query(callback_query.id,
                                        text=str(callback_query.message.text + ' added'), show_alert=True)
        data = dict_from_string(callback_query.message.text)
        towar.write_by_admin(data)
        print(data)
        print(int(data[-2]))
        await bot.send_message(chat_id=int(data[-2]),
                               text='Модерация прошла успешно')
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
    else:
        await bot.answer_callback_query(callback_query.id,
                                        text=str(callback_query.message.text + ' not added'), show_alert=True)
        data = dict_from_string(callback_query.message.text)
        await bot.send_message(chat_id=int(data[-1]),
                               text='Ваша анкета не прошла модерацию, пожалуйста повторите регистрацию нажав /start')
        print(int(data[-1]))
        await bot.edit_message_reply_markup(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )


# Создание нового времени для тренировки
@dp.message_handler(Text(equals=['Navigation Calendar'], ignore_case=True))
async def nav_cal_handler(message: types.Message):
    await message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(state=FSMAdmin.choose_new_time)
async def main_menu(callback_query: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    if callback_query.data == 'back':
        await restart_admin(callback_query.from_user.id)
    else:
        date = callback_query.message.text.split('#')[1]
        async with state.proxy() as data:
            data['first'] = date
            data['second'] =callback_query.data
        await callback_query.message.answer(text=str(date+' '+callback_query.data))
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Напишите описание к тренировке')
        await FSMAdmin.wait_for_deskriptoin.set()


@dp.callback_query_handler(simple_cal_callback.filter(),state=FSMAdmin.add_new_times)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=f'В этот день #{date.strftime("%d.%m.%Y")}# {towar.view_old_times(date.strftime("%d.%m.%Y"))}',
        reply_markup=admin_keyboards.choose_time)
        await FSMAdmin.choose_new_time.set()


async def save_new_time(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        towar.add_new_time(data['first'],data['second'],message.text)
    await message.answer('New time added')
    await FSMAdmin.main_admin_state.set()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(moderation, state=FSMAdmin.main_admin_state, commands=['admin_moderation'])
    dp.register_message_handler(delete_time_by_admin, state=FSMAdmin.main_admin_state, commands=['delete_time'])
    dp.register_message_handler(save_new_time, state=FSMAdmin.wait_for_deskriptoin)
    dp.register_message_handler(chek_admin, state='*', commands=['admin'])
    dp.register_message_handler(admin_new_time, state=FSMAdmin.main_admin_state, commands=['admin_new_time'])
