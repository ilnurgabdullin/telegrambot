from flask import Flask, render_template, request
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
    return render_template('about.html')


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
def dalete_train():
    if request.method == 'POST':
        date = request.form.get('date')  # запрос к данным формы
        time = request.form.get('time')
        type = request.form.get('type')

        try:
            towar.delete_trainig(date,time)
        except Exception as ex:
            print(ex)
    return render_template('delete_train.html')



if __name__ == '__main__':
    app.run(debug=True)
