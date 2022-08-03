import psycopg2
import datetime
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connect_args = {
    'user':'postgres',
    'password':'123',
    "host":"127.0.0.1",
    'port':"5432",
    'dbname':'first'
}


def decrement_priority(trainid: int)-> int:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT priority FROM training WHERE trainid=%s',(trainid,))
            x = cursor.fetchone()[0] - 1
            if x >= 0:
                cursor.execute("UPDATE training SET priority = %s WHERE trainid = %s", (x,trainid))
                return x
            return 0


def binded_reserve(data: list) -> bool:
    for i in data:
        if i[4] != 0 and i[5] == True:
            return True
    return False


def write_new(data: list) -> None: # Записывает нового пользователя
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data)
        connection.commit()


def is_exists(tgid: int) -> int: # Проверяет есть ли позьзователь в базе
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE tgid=%s;',(tgid,))
            info = cursor.fetchone()

            if info is None:
                return 0
            elif not(info[7]):
                if info[6]:
                    return 1
                    # если пользователь модерирован и не удалён
                else:
                    return -1
                    # пользователь не модерирован


def chek_aboniment(tgid: int) -> int:  # возвращает количество занятий пользователя
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT sub FROM users WHERE tgid = %s;""", (tgid,))
            x = cursor.fetchone()[0]
            return x


def take_name_by_id(tgid: int) -> str: # возвращает имя пользователя по его id
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT name FROM users WHERE tgid = %s;""", (tgid,))
            x = str(cursor.fetchone()[0]).replace('_',' ')
            return x


def write_transaktion(tgid: int,kolvo: int): # записывает транзакцию в таблицу
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            type = str(kolvo)
            date = datetime.datetime.now().strftime('%H:%M %d/%m/%y')
            cursor.execute("INSERT INTO transactions (tgid, type, date) VALUES (%s, %s, %s)", (tgid,type,date))


def update_tiket(tgid: int, kolvo: int = 0) -> None:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
    # если передать параметр колво то на баланс будет зачисленно такое
    # количество тренировок, иначе будет списана одна тренировка
            if kolvo != 0:
                cursor.execute("""UPDATE users SET sub = %s WHERE tgid = %s""", (chek_aboniment(tgid) + kolvo, tgid))
            else:
                cursor.execute("""UPDATE users SET sub = %s WHERE tgid = %s""", (chek_aboniment(tgid) - 1 , tgid))


def view_new_user() -> list: # возваращает список немодерированных юзеров
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE moder=False AND deleted=False')
            data = []
            for i in cursor.fetchall():
                data.append(i)
            return data


def create_new_training(date: str, time: str, type: str, person: int, rezerve: int = 0 ) -> None:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            for i in range(person):
                cursor.execute('INSERT INTO training (date, time, type, priority) VALUES (%s, %s, %s, %s)',(date, time, type, 0))
            if rezerve > 0:
                for i in range(rezerve):
                    cursor.execute('INSERT INTO training (date, time, type, priority) VALUES (%s, %s, %s, %s)', (date, time, type, i+1))


def look_free_trains(date: str = None) -> list:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            if date is None:
                cursor.execute('SELECT * FROM training WHERE binded=False')
            else:
                cursor.execute('SELECT * FROM training WHERE binded=False and date=%s;',(date,))
            return cursor.fetchall()


def bind_train(date: str, time: str, tgid: int) -> str:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM training RIGHT JOIN used_slots ON used_slots.trainid=training.trainid WHERE date=%s AND time=%s;',(date,time))
            for i in cursor.fetchall():
                if i[7] == tgid:
                    return 'Вы уже записаны на тренировку в это время'
            cursor.execute('SELECT * FROM training WHERE binded=False AND date=%s AND time=%s ORDER BY priority;',(date,time,))
            try:
                id = cursor.fetchone()[0]
            except TypeError:
                return 'Извините, это время уже занято'
            cursor.execute('UPDATE training SET binded=True WHERE trainid=%s',(id,))
            cursor.execute('INSERT INTO used_slots (userid, trainid) VALUES (%s, %s)',(tgid,id))
            update_tiket(tgid)
            return 'Вы записаны на тренировку'


def delete_binded_time(trainid: int):
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM used_slots WHERE trainid=%s',(trainid,))
            data = cursor.fetchone()
            now_time = datetime.datetime.now()
            cursor.execute('SELECT * FROM training WHERE trainid=%s', (trainid,))
            train_data = cursor.fetchone()
            train_time = datetime.datetime.strptime(str(train_data[1])+' '+ str(train_data[2]), '%d.%m.%Y %H:%M')
            if train_time > now_time:
                update_tiket(data[0], 1)
                cursor.execute('SELECT * FROM training WHERE date=%s AND time=%s', (train_data[1],train_data[2]))
                all_trains = cursor.fetchall()
                max_priority = 0
                if binded_reserve(all_trains):# Проверить заняты ли строки с резервом ok
                    for i in all_trains:
                        max_priority = max(decrement_priority(i[0]),max_priority) # Если они заняты то уменьшить в них поле priopity на 1
                    cursor.execute('UPDATE training SET priority=%s WHERE trainid=%s', (max_priority+1,data[1],))
                cursor.execute('DELETE FROM used_slots WHERE trainid=%s',(trainid,))# Удалить привязку в таблице used_slots ok
                cursor.execute('UPDATE training SET binded=False WHERE trainid=%s', (data[1],)) # Поменять поле биндед на false ok


def look_user_info(tgid: int) -> list:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT * FROM training 
            JOIN used_slots 
            ON used_slots.trainid=training.trainid
            JOIN users
            ON used_slots.userid=users.tgid
            WHERE tgid=%s;
            ''',(tgid,))
            return cursor.fetchall()


def delete_time(date: str, time: str, type: str = None):
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            if type is None:
                cursor.execute('DELETE FROM training WHERE date=%s AND time=%s',(date,time))
            else:
                cursor.execute('DELETE FROM training WHERE date=%s AND time=%s AND type=%s', (date, time, type))


def get_name(trainid: int) -> str:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT userid FROM used_slots WHERE trainid=%s;',(trainid,))

            id = cursor.fetchone()

            if type(id) != type(None):
                name = take_name_by_id(*id)
                return name
            return ''


def look_all_trains(date: str = None) -> list:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            if date is None:
                cursor.execute('SELECT * FROM training WHERE passed=False')
            else:
                cursor.execute('SELECT * FROM training WHERE date=%s AND passed=False;',(date,))
            trains = []
            for i in cursor.fetchall():
                cursor.execute('''SELECT userid FROM used_slots WHERE trainid=%s''',(i[0],))
                ids = cursor.fetchall()
                x = (i[1], i[2], ids)
                if x not in trains:
                    trains.append(x)
            return trains


def take_type_by_time(date: str, time: str):
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''SELECT type FROM training WHERE date=%s AND time=%s;''', (date,time))
            return str(*cursor.fetchone())


def delete_trainig(date: str, time: str) -> None:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                    SELECT * FROM training
                    LEFT JOIN used_slots
                    ON training.trainid=used_slots.trainid
                    WHERE date=%s AND time=%s;
                    ''',(date,time)
                    )
            for i in cursor.fetchall():
                if not (i[7] is None):
                    update_tiket(i[7],1)
                    cursor.execute('DELETE FROM used_slots WHERE trainid=%s',(i[0],))
                cursor.execute('DELETE FROM training WHERE date=%s AND time=%s;', (date,time))


def get_dialog() -> dict:
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            dialog = {}
            cursor.execute('''SELECT * FROM dialogue;''')
            for phrase in cursor.fetchall():
                dialog[phrase[1]] = phrase[2]
            return dialog


def set_dialog(phrase: str,pattern: str):
    with psycopg2.connect(**connect_args) as connection:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE dialogue SET phrase = %s WHERE pattern = %s''',(phrase, pattern))

if __name__ == '__main__':
    print(take_type_by_time('04.08.2022','12:00'))
