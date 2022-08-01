from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import datetime
client_main_board = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard= True)
client_main_board.add(KeyboardButton('/Машины')).add(KeyboardButton('/Ароматы')).add('/Отмена')

choose_gender_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard= True)
choose_gender_kb.add(KeyboardButton('Мужской')).add(KeyboardButton('Женский'))

ok = InlineKeyboardButton(text='Да, отлично',callback_data='ok')
not_ok = InlineKeyboardButton(text='Нет, я ошибся',callback_data='not_ok')
ok_reg_kb = InlineKeyboardMarkup(row_width=1).add(ok).add(not_ok)


phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)
phone_kb.add(KeyboardButton('Отправить номер телефона', request_contact= True))


but1 = InlineKeyboardButton(text='Выбрать время',callback_data='bind_time')
but2 = InlineKeyboardButton(text='Купить абонемент',callback_data='buy_ticket')
but3 = InlineKeyboardButton(text='Отменить запись',callback_data='cancel_record')
but4 = InlineKeyboardButton(text='Правила клуба',callback_data='rules')
back = InlineKeyboardButton(text='Назад',callback_data='back')
main_menu_client = InlineKeyboardMarkup(row_width=1).add(but1).add(but2).add(but3).add(but4)


buy_ticket_kb = InlineKeyboardMarkup(row_width=3)
ticket_kolvo = InlineKeyboardButton(text = 'Занятий',callback_data='ignore')
ticket_price = InlineKeyboardButton(text = 'Цена',callback_data='ignore')
buttons = [
    [InlineKeyboardButton(text = '1',callback_data='buy_tiket#1'),InlineKeyboardButton(text = '100',callback_data='buy_tiket#1')],
    [InlineKeyboardButton(text = '3',callback_data='buy_tiket#3'),InlineKeyboardButton(text = '290',callback_data='buy_tiket#3')],
    [InlineKeyboardButton(text = '5',callback_data='buy_tiket#5'),InlineKeyboardButton(text = '450',callback_data='buy_tiket#5')],
    [InlineKeyboardButton(text = '7',callback_data='buy_tiket#7'),InlineKeyboardButton(text = '600',callback_data='buy_tiket#7')],
    [InlineKeyboardButton(text = '10',callback_data='buy_tiket#10'),InlineKeyboardButton(text = '850',callback_data='buy_tiket#10')]
]

buy_ticket_kb.add(ticket_kolvo).insert(ticket_price)
for i in buttons:
    buy_ticket_kb.row(*i)

buy_ticket_kb.add(back)
rules_kb = InlineKeyboardMarkup()
rules_kb.add(back)


def create_choose_time_kb(data: list, lift : bool = True):
    if len(data) == 0:
        return False
    else:
        choose_time = InlineKeyboardMarkup(row_width=1)
        times = []
        for i in data:
            a = i[1]+' '+i[2]
            if a not in times:
                choose_time.add(InlineKeyboardButton(text=a, callback_data= a))
                times.append(a)
    if lift:
        choose_time.add(InlineKeyboardButton(text='Смотреть участников', callback_data='list'+data[0][1]))
    choose_time.add(back)
    return choose_time


def cancel_ticket_kb(data: list):
    # cursor.execute('SELECT * FROM used_slots WHERE trainid=%s', (trainid,))
    # data = cursor.fetchone()
    # now_time = datetime.datetime.now()
    # cursor.execute('SELECT * FROM training WHERE trainid=%s', (trainid,))
    # train_data = cursor.fetchone()
    # train_time = datetime.datetime.strptime(str(train_data[1]) + ' ' + str(train_data[2]), '%d.%m.%Y %H:%M')
    # if train_time > now_time:
    buttons = []
    if len(data) == 0:
        return False
    else:
        cancel_ticket = InlineKeyboardMarkup(row_width=1)
        for i in data:
            print(i)
            train_time = datetime.datetime.strptime(str(i[1]) + ' ' + str(i[2]), '%d.%m.%Y %H:%M')
            now_time = datetime.datetime.now()
            if train_time > now_time:
                buttons.append(InlineKeyboardButton(text=str(i[2])+' '+str(i[1]), callback_data=str(i[0])))
    if len(buttons) == 0:
        return False
    for i in buttons:
        cancel_ticket.add(i)
    cancel_ticket.add(back)
    return cancel_ticket
