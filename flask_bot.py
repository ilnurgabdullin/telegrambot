from flask import Flask, render_template, request, redirect
import psycopg2

import towar

connect_args = {
    'user': 'postgres',
    'password': '123',
    "host": "127.0.0.1",
    'port': "5432",
    'dbname': 'first'
}


app = Flask(__name__)


@app.route('/', methods=['post', 'get'])
def index():
    name = ''
    if request.method == 'POST':
        id = request.form.get('id')  # запрос к данным формы
        if id != '':
            name = str(towar.take_name_by_id(int(id)))
    return render_template('index.html', name = name)


@app.route('/about')
def about():
    d = towar.view_new_user()
    if len(d) == 0:
        return redirect('/')
    return render_template('about.html', users = towar.view_new_user())


@app.route('/about/<int:tgid>')
def moder_user(tgid: int):
    towar.moder_user_by_tgid(tgid)
    return redirect('/about')


@app.route('/delete/<int:tgid>')
def delete_user(tgid: int):
    towar.moder_user_by_tgid(tgid,True)
    return redirect('/about')


@app.route('/create_train',  methods=['post', 'get'])
def create_train():
    if request.method == 'POST':
        date = request.form.get('date')  # запрос к данным формы
        time = request.form.get('time')
        type = request.form.get('type')
        person = request.form.get('person')
        rezerve = request.form.get('rezerve')
        try:
            towar.create_new_training(date,time,type,int(person),int(rezerve))
        except Exception as ex:
            print(ex)
    return render_template('create_train.html')


@app.route('/delete_train',  methods=['post', 'get'])
def delete_train():
    return render_template('delete_train.html',trains = towar.look_all_trains())


@app.route('/delete_train/<string:date>/<string:time>')
def delete_train_by_id(date: str, time: str):
    import telebot
    bot = telebot.TeleBot(token='')
    for i in towar.delete_trainig(date,time):
        bot.send_message(i,f'Тренировка {date} {time} была отменена')
    del bot
    return redirect('/')


@app.route('/edit_dialog',  methods=['post', 'get'])
def edit_dialog():
    if request.method == 'POST':
        for i in request.form:
            towar.set_dialog(request.form.get(i), i)
    return render_template('edit_dialog.html',phrases = towar.get_dialog())


if __name__ == '__main__':
    app.run(debug=True)
