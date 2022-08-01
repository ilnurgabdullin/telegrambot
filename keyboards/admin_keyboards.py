from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


moderation_admin_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
moderation_admin_keyboard.add(InlineKeyboardButton(text = 'Добавить',callback_data='add')).insert(InlineKeyboardButton(
    text = 'Перерегистрация',
    callback_data='again'))

main_admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin_kb.add('/admin_new_time').add('/admin_moderation').add('/delete_time')
back = InlineKeyboardButton(text='Назад',callback_data='back')


def create_delete_time(date: list) -> type(InlineKeyboardButton):
    delete_time = InlineKeyboardMarkup(row_width=1)
    for i in date:
        delete_time.add(InlineKeyboardButton(text = i[0] + ' ' + i[1],callback_data=i[0] + '_' + i[1]))
    delete_time.add(back)
    return delete_time
