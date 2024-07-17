from flask import Flask, request, session, redirect, url_for, render_template, flash, Response
import psycopg2
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
import io
from functools import wraps
import xlwt
from datetime import datetime, date, timedelta
from waitress import serve
from flask_mail import Mail
from random import randint
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
mail = Mail(app)

DATABASE_URL = "postgresql://postgres:XQxUlhHceLGYULtBXwFIhsmzrYBjlVDJ@viaduct.proxy.rlwy.net:48461/railway"
DATABASE_URL2 = ""



app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'Analstasia.Sholokhova@yandex.ru'
app.config['MAIL_PASSWORD'] = 'xyanueciccoxachh'
app.config['MAIL_USE_TLS'] = 1
app.config['MAIL_USE_SSL'] = False

conn = psycopg2.connect(DATABASE_URL, sslmode = "require")
conn2 = psycopg2.connect(DATABASE_URL2, sslmode="require")


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'phone_number' in request.form:
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_number = request.form['phone_number']
        role = request.form['role']
    
        _hashed_password = generate_password_hash(password)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM users WHERE email=%s', (email,))
        email_exists = cursor.fetchone()
        if account:
            flash('Аккаунт уже зарегистрирован!')
        if email_exists:
            flash('Этот адрес электронной почты уже используется!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Некорректный адрес электронной почты!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Имя пользователя должно содержать только буквы и цифры!')
        elif not re.match(r"^(?:\+?(?:[0-9] ?){6,14}[0-9])$", phone_number):
            flash('Некорректный номер телефона!')
        elif not username or not password or not email or not phone_number or not role:
            flash('Пожалуйста, заполните форму!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email, phone_number, role) VALUES (%s,%s,%s,%s,%s,%s)", (fullname, username, _hashed_password, email, phone_number, role))
            conn.commit()
            cursor.execute('SELECT LASTVAL() AS id;')
            user_id = cursor.fetchone()
            session['loggedin'] = True
            session['id'] = user_id
            session['username'] = username
            session['role'] = role
            flash('Вы были успешно зарегистрированы!')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        flash('Пожалуйста, заполните форму!')
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                selected_role = account['role']
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                session['role'] = selected_role
                session['email'] = account['email']
                if selected_role == 'editor':
                    return redirect(url_for('home_editor'))
                elif selected_role == 'support':
                    return redirect(url_for('home_support'))
                else:
                    return redirect(url_for('home'))
            else:
                flash('Неверное имя пользователя/пароль')
        else:
            flash('Неверное имя пользователя/пароль')
 
    return render_template('login.html')

@app.route('/login_ad', methods=['GET', 'POST'])
def login_ad():
    pass

def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' in session and session['role'] in roles:
                return func(*args, **kwargs)
            else:
                flash('У вас нет доступа к этой странице!')
                return redirect(url_for('login'))
        return wrapper
    return decorator

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/home')
@role_required('admin')
def home():
    if 'loggedin' in session:
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = 'SELECT * FROM лицензии'
        cur.execute(s)
        list_licences = cur.fetchall()
        return render_template('home.html', username=session['username'], list_licences = list_licences)
    return redirect(url_for('login'))

@app.route('/home_support')
@role_required('support')
def home_support():
    if 'loggedin' in session:
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = 'SELECT * FROM лицензии'
        cur.execute(s)
        list_licences = cur.fetchall()
        return render_template('home_support.html', username=session['username'], list_licences = list_licences)
    return redirect(url_for('login'))

@app.route('/home_editor')
@role_required('editor')
def home_editor():
    if 'loggedin' in session:
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = 'SELECT * FROM лицензии'
        cur.execute(s)
        list_licences = cur.fetchall()
        return render_template('home_editor.html', username=session['username'], list_licences = list_licences)
    return redirect(url_for('login'))
 
@app.route('/add_licence', methods=['POST'])
def add_licence():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method== 'POST':
        номер_пп = request.form['номер_пп']
        наименование_ПО = request.form['наименование_ПО']
        вендор = request.form['вендор']
        начало_действия_лицензии = request.form['начало_действия_лицензии']
        счёт_списания = request.form['счёт_списания']
        заказчик_ПО = request.form['заказчик_ПО']
        признак_ПО = request.form['признак_ПО']
        количество_ПО = int(request.form['количество_ПО'])
        оплачено = bool(request.form.get('оплачено'))
        примечание = request.form['примечание']
        cur.execute('SELECT 1 FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s', (наименование_ПО, признак_ПО))
        lic_exists = cur.fetchone()
        if lic_exists:
            cur.execute('SELECT стоимость_за_единицу FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s',(наименование_ПО, признак_ПО,))
            inst = cur.fetchone()
            стоимость_за_единицу = inst['стоимость_за_единицу']
            if not количество_ПО:
                flash('Пожалуйста, введите количество ПО!')
                return redirect(url_for('home'))
            if not начало_действия_лицензии:
                flash('Пожалуйста, заполните все поля формы!')
                return redirect(url_for('home'))
            if признак_ПО == 'Новое':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            elif признак_ПО == 'Техподдержка':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО * 1.2
            else:
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            if счёт_списания == '12':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365)).strftime('%Y-%m-%d')
            elif счёт_списания == '36':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365 * 3)).strftime('%Y-%m-%d')
            if оплачено:
                остаток = 0
            elif счёт_списания == '12' and not оплачено:
                остаток = итоговая_стоимость
            elif счёт_списания == '36' and not оплачено:
                окончание_действия_лицензии_date = datetime.strptime(окончание_действия_лицензии, '%Y-%m-%d').date()
                срок_действия_мес = (окончание_действия_лицензии_date - date.today()).days / 30
                мес_стоимость = итоговая_стоимость / 36
                остаток = round(мес_стоимость * срок_действия_мес, 2)
            else:
                остаток = 0
            cur.execute(
                "INSERT INTO лицензии (номер_пп, наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, счёт_списания, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, срок_действия_лицензии, оплачено, остаток, примечание) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, (to_timestamp(CAST(%s AS text), 'YYYY-MM-DD') - NOW())::interval, %s, %s, %s)",
                (
                    номер_пп, наименование_ПО, вендор, начало_действия_лицензии, 
                    окончание_действия_лицензии, счёт_списания, стоимость_за_единицу, 
                    итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, 
                    окончание_действия_лицензии, оплачено, остаток, примечание
                )
            )
            conn2.commit()
            flash('Запись была успешно добавлена!')
            return redirect(url_for('home'))
        else:
            flash('Такого ПО не существует в справочнике ПО')
            return redirect(url_for('home'))

@app.route('/editor_add_licence', methods=['POST'])
def editor_add_licence():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method== 'POST':
        номер_пп = request.form['номер_пп']
        наименование_ПО = request.form['наименование_ПО']
        вендор = request.form['вендор']
        начало_действия_лицензии = request.form['начало_действия_лицензии']
        счёт_списания = request.form['счёт_списания']
        заказчик_ПО = request.form['заказчик_ПО']
        признак_ПО = request.form['признак_ПО']
        количество_ПО = int(request.form['количество_ПО'])
        оплачено = bool(request.form.get('оплачено'))
        примечание = request.form['примечание']
        cur.execute('SELECT 1 FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s', (наименование_ПО, признак_ПО,))
        lic_exists = cur.fetchone()
        if lic_exists:
            cur.execute('SELECT стоимость_за_единицу FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s;', (наименование_ПО, признак_ПО,))
            lic = cur.fetchone()
            стоимость_за_единицу = lic['стоимость_за_единицу']
            if not количество_ПО:
                flash('Пожалуйста, введите количество ПО!')
                return redirect(url_for('home_editor'))
            if not начало_действия_лицензии:
                flash('Пожалуйста, заполните все поля формы!')
                return(redirect(url_for('home_editor')))
            if признак_ПО == 'Новое':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            elif признак_ПО == 'Техподдержка':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО * 1.2
            else:
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            if счёт_списания == '12':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365)).strftime('%Y-%m-%d')
            elif счёт_списания == '36':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365 * 3)).strftime('%Y-%m-%d')
            if оплачено:
                остаток = 0
            elif счёт_списания == '12' and not оплачено:
                остаток = итоговая_стоимость
            elif счёт_списания == '36' and not оплачено:
                окончание_действия_лицензии_date = datetime.strptime(окончание_действия_лицензии, '%Y-%m-%d').date()
                срок_действия_мес = (окончание_действия_лицензии_date - date.today()).days / 30
                мес_стоимость = итоговая_стоимость / 36
                остаток = round(мес_стоимость * срок_действия_мес, 2)
            else:
                остаток = 0
            cur.execute(
                "INSERT INTO лицензии (номер_пп, наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, счёт_списания, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, срок_действия_лицензии, оплачено, остаток, примечание) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, (to_timestamp(CAST(%s AS text), 'YYYY-MM-DD') - NOW())::interval, %s, %s, %s)",
                (
                    номер_пп, наименование_ПО, вендор, начало_действия_лицензии, 
                    окончание_действия_лицензии, счёт_списания, стоимость_за_единицу, 
                    итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, 
                    окончание_действия_лицензии, оплачено, остаток, примечание
                )
            )
            conn2.commit()
            flash('Запись была успешно добавлена!')
            return redirect(url_for('home_editor'))
        else:
            flash('Такого ПО нет в справочнике ПО!')
            return redirect(url_for('home_editor'))
    
@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM лицензии WHERE номер_пп = %s', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('edit.html', licence = data[0])

@app.route('/editor_edit/<id>', methods=['POST', 'GET'])
def editor_get_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM лицензии WHERE номер_пп=%s', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('editor_edit.html', licence=data[0])

@app.route('/update/<id>', methods=['POST'])
def update_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        вендор = request.form['вендор']
        начало_действия_лицензии = request.form['начало_действия_лицензии']
        счёт_списания = request.form['счёт_списания']
        заказчик_ПО = request.form['заказчик_ПО']
        признак_ПО = request.form['признак_ПО']
        количество_ПО = int(request.form['количество_ПО'])
        оплачено = bool(request.form.get('оплачено'))
        примечание = request.form['примечание']
        cur.execute('SELECT 1 FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s;', (наименование_ПО, признак_ПО))
        lic_exists = cur.fetchone()
        if lic_exists:
            cur.execute('SELECT стоимость_за_единицу FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s;', 
                        (наименование_ПО, признак_ПО,))
            lic = cur.fetchone()
            стоимость_за_единицу = lic['стоимость_за_единицу']
            if not количество_ПО:
                flash('Пожалуйста, введите количество ПО!')
                return redirect(url_for('edit'))
            if признак_ПО == 'Новое':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            elif признак_ПО == 'Техподдержка':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО * 1.2
            else:
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            if счёт_списания == '12':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365)).strftime('%Y-%m-%d')
            elif счёт_списания == '36':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365 * 3)).strftime('%Y-%m-%d')
            if оплачено:
                остаток = 0
            elif счёт_списания == '12' and not оплачено:
                остаток = итоговая_стоимость
            elif счёт_списания == '36' and not оплачено:
                окончание_действия_лицензии_date = datetime.strptime(окончание_действия_лицензии, '%Y-%m-%d').date()
                срок_действия_мес = (окончание_действия_лицензии_date - date.today()).days / 30
                мес_стоимость = итоговая_стоимость / 36
                остаток = round(мес_стоимость * срок_действия_мес, 2)
            else:
                остаток = 0
            cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(""" UPDATE лицензии
                        SET
                        наименование_ПО=%s,
                        вендор=%s,
                        начало_действия_лицензии=%s,
                        окончание_действия_лицензии=%s,
                        счёт_списания=%s,
                        стоимость_за_единицу=%s,
                        итоговая_стоимость=%s,
                        заказчик_ПО=%s,
                        признак_ПО=%s,
                        количество_ПО=%s,
                        срок_действия_лицензии=(to_timestamp(CAST(%s AS text), 'YYYY-MM-DD') - NOW())::interval,
                        оплачено=%s,
                        остаток=%s,
                        примечание=%s
                        WHERE номер_пп=%s
                        """, (наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, счёт_списания, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, окончание_действия_лицензии, оплачено, остаток, примечание, id))
            flash("Запись успешно обновлена!")
            conn2.commit()
            return redirect(url_for('home'))
        else:
            flash('Такого ПО нет в справочнике ПО!')
            return redirect(url_for('get_licence', id=id))
    
@app.route('/editor_update/<id>', methods=['POST'])
def editor_update_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        вендор = request.form['вендор']
        начало_действия_лицензии = request.form['начало_действия_лицензии']
        счёт_списания = request.form['счёт_списания']
        заказчик_ПО = request.form['заказчик_ПО']
        признак_ПО = request.form['признак_ПО']
        количество_ПО = int(request.form['количество_ПО'])
        оплачено = bool(request.form.get('оплачено'))
        примечание = request.form['примечание']
        cur.execute('SELECT 1 FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s;', (наименование_ПО, признак_ПО,))
        lic_exists = cur.fetchone()
        if lic_exists:
            cur.execute('SELECT стоимость_за_единицу FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s;',
                        (наименование_ПО, признак_ПО,))
            lic = cur.fetchone()
            стоимость_за_единицу = lic['стоимость_за_единицу']
            if not количество_ПО:
                flash('Пожалуйста, введите количество ПО!')
                return redirect(url_for('editor_edit'))
            if признак_ПО == 'Новое':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            elif признак_ПО == 'Техподдержка':
                итоговая_стоимость = стоимость_за_единицу * количество_ПО * 1.2
            else:
                итоговая_стоимость = стоимость_за_единицу * количество_ПО
            if счёт_списания == '12':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365)).strftime('%Y-%m-%d')
            elif счёт_списания == '36':
                начало_действия_лицензии_date = datetime.strptime(начало_действия_лицензии, '%Y-%m-%d').date()
                окончание_действия_лицензии = (начало_действия_лицензии_date + timedelta(days=365 * 3)).strftime('%Y-%m-%d')
            if оплачено:
                остаток = 0
            elif счёт_списания == '12' and not оплачено:
                остаток = итоговая_стоимость
            elif счёт_списания == '36' and not оплачено:
                окончание_действия_лицензии_date = datetime.strptime(окончание_действия_лицензии, '%Y-%m-%d').date()
                срок_действия_мес = (окончание_действия_лицензии_date - date.today()).days / 30
                мес_стоимость = итоговая_стоимость / 36
                остаток = round(мес_стоимость * срок_действия_мес, 2)
            else:
                остаток = 0
            cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(""" UPDATE лицензии
                        SET
                        наименование_ПО=%s,
                        вендор=%s,
                        начало_действия_лицензии=%s,
                        окончание_действия_лицензии=%s,
                        счёт_списания=%s,
                        стоимость_за_единицу=%s,
                        итоговая_стоимость=%s,
                        заказчик_ПО=%s,
                        признак_ПО=%s,
                        количество_ПО=%s,
                        срок_действия_лицензии=(to_timestamp(CAST(%s AS text), 'YYYY-MM-DD') - NOW())::interval,
                        оплачено=%s,
                        остаток=%s,
                        примечание=%s
                        WHERE номер_пп=%s
                        """, (наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, счёт_списания, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, окончание_действия_лицензии, оплачено, остаток, примечание, id))
            flash("Запись успешно обновлена!")
            conn2.commit()
            return redirect(url_for('home_editor'))
        else:
            flash('Такого ПО нет в справочнике ПО!')
            return redirect(url_for('editor_get_licence', id=id))
    
@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM лицензии WHERE номер_пп = {0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('home'))

@app.route('/editor_delete/<string:id>', methods=['POST', 'GET'])
def editor_delete_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM лицензии WHERE номер_пп = {0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('home_editor'))
                
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/support_profile')
def support_profile():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        cur.execute('SELECT * FROM users WHERE id=%s', [session['id']])
        account = cur.fetchone()
        return render_template('support_profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/editor_profile')
def editor_profile():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        cur.execute('SELECT * FROM users WHERE id=%s', [session['id']])
        account = cur.fetchone()
        return render_template('editor_profile.html', account=account)
    return redirect(url_for('login'))
 
@app.route('/software')
@role_required('admin')
def software_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_ПО'
        cur.execute(string)
        list_software = cur.fetchall()
        return render_template('software.html', list_software=list_software)
    return redirect(url_for('login'))

@app.route('/editor_software')
@role_required('editor')
def editor_software_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_ПО'
        cur.execute(string)
        list_software = cur.fetchall()
        return render_template('editor_software.html', list_software=list_software)
    return redirect(url_for('login'))

@app.route('/support_software')
@role_required('support')
def support_software_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = 'SELECT * FROM Справочник_ПО'
        cur.execute(string)
        list_software = cur.fetchall()
        return render_template('support_software.html', list_software=list_software)
    return redirect(url_for('login'))

@app.route('/add_software', methods=['POST'])
def add_software():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_ПО = request.form['код_ПО']
        наименование_ПО = request.form['наименование_ПО']
        описание_ПО = request.form['описание_ПО']
        ссылка_на_сайт_ПО = request.form['ссылка_на_сайт_ПО']
        вендор = request.form['вендор']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        признак_ПО = request.form.get('признак_ПО')
        примечание = request.form['примечание']
        cur.execute('SELECT наименование_ПО, признак_ПО FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s', (наименование_ПО, признак_ПО))
        soft = cur.fetchone()
        if soft:
            flash('Запись с такими данными уже существует!')
            return redirect(url_for('software_list'))
        cur.execute("INSERT INTO Справочник_ПО (код_ПО, наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, примечание) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (код_ПО, наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('software_list'))

@app.route('/editor_add_software', methods=['POST'])
def editor_add_software():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_ПО = request.form['код_ПО']
        наименование_ПО = request.form['наименование_ПО']
        описание_ПО = request.form['описание_ПО']
        ссылка_на_сайт_ПО = request.form['ссылка_на_сайт_ПО']
        вендор = request.form['вендор']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        признак_ПО = request.form.get('признак_ПО')
        примечание = request.form['примечание']
        cur.execute('SELECT наименование_ПО, признак_ПО FROM Справочник_ПО WHERE наименование_ПО=%s AND признак_ПО=%s;', (наименование_ПО, признак_ПО,))
        soft = cur.fetchone()
        if soft:
            flash('Запись с такими данными уже существует!')
            return redirect(url_for('editor_software_list'))
        cur.execute("INSERT INTO Справочник_ПО (код_ПО, наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, примечание) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (код_ПО, наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('editor_software_list'))

@app.route('/edit_software/<id>', methods=['POST', 'GET'])
def edit_software(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_ПО WHERE код_ПО=%s', (id,))
    get_software = cur.fetchall()
    cur.close()
    return render_template('edit_software.html', software=get_software[0])

@app.route('/editor_edit_software/<id>', methods=['POST', 'GET'])
def editor_edit_software(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_ПО WHERE код_ПО=%s', (id,))
    get_software = cur.fetchall()
    cur.close()
    return render_template('editor_edit_software.html', software=get_software[0])

@app.route('/update_software/<id>', methods=['POST'])
def update_software(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        описание_ПО = request.form['описание_ПО']
        ссылка_на_сайт_ПО = request.form['ссылка_на_сайт_ПО']
        вендор = request.form['вендор']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        признак_ПО = request.form['признак_ПО']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_ПО
                    SET
                    наименование_ПО=%s,
                    описание_ПО=%s,
                    ссылка_на_сайт_ПО=%s,
                    вендор=%s,
                    стоимость_за_единицу=%s,
                    признак_ПО=%s,
                    примечание=%s
                    WHERE код_ПО=%s
                    """, (наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, примечание, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('software_list'))
    
@app.route('/editor_update_software/<id>', methods=['POST'])
def editor_update_software(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        описание_ПО = request.form['описание_ПО']
        ссылка_на_сайт_ПО = request.form['ссылка_на_сайт_ПО']
        вендор = request.form['вендор']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        признак_ПО = request.form['признак_ПО']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_ПО
                    SET
                    наименование_ПО=%s,
                    описание_ПО=%s,
                    ссылка_на_сайт_ПО=%s,
                    вендор=%s,
                    стоимость_за_единицу=%s,
                    признак_ПО=%s,
                    примечание=%s
                    WHERE код_ПО=%s
                    """, (наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, примечание, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('editor_software_list'))
    
    
@app.route('/delete_software/<string:id>', methods=['POST', 'GET'])
def delete_software(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_ПО WHERE код_ПО = {0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('software_list'))

@app.route('/editor_delete_software/<string:id>' ,methods=['POST', 'GET'])
def editor_delete_software(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_ПО WHERE код_ПО = {0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('editor_software_list'))

@app.route('/download_software/report/excel')
def download_software_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_ПО')
    res_software = cur.fetchall()
    output_software = io.BytesIO()
    workbook_software = xlwt.Workbook()
    sh_software = workbook_software.add_sheet('Отчет по ПО')
    sh_software.write(0, 0, 'Код ПО')
    sh_software.write(0, 1, 'Наименование ПО')
    sh_software.write(0, 2, 'Описание ПО')
    sh_software.write(0, 3, 'Ссылка на сайт ПО')
    sh_software.write(0, 4, 'Вендор')
    sh_software.write(0, 5, 'Стоимость за единицу')
    sh_software.write(0, 6, 'Признак ПО')
    sh_software.write(0, 7, 'Примечание')
    idx = 0 
    for row in res_software:
        sh_software.write(idx+1, 0, str(row['код_ПО']))
        sh_software.write(idx+1, 1, row['наименование_ПО'])
        sh_software.write(idx+1, 2, row['описание_ПО'])
        sh_software.write(idx+1, 3, row['ссылка_на_сайт_ПО'])
        sh_software.write(idx+1, 4, row['вендор'])
        sh_software.write(idx+1, 5, row['стоимость_за_единицу'])
        sh_software.write(idx+1, 6, row['признак_ПО'])
        sh_software.write(idx+1, 7, row['примечание'])
        idx += 1
    workbook_software.save(output_software)
    output_software.seek(0)
    return Response(output_software, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=software_report.xls"})

@app.route('/vendor')
@role_required('admin')
def vendor_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_производителей_ПО'
        cur.execute(string)
        list_vendor = cur.fetchall()
        return render_template('vendor.html', list_vendor=list_vendor)
    return redirect(url_for('login'))

@app.route('/editor_vendor')
@role_required('editor')
def editor_vendor_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_производителей_ПО'
        cur.execute(string)
        list_vendor = cur.fetchall()
        return render_template('editor_vendor.html', list_vendor=list_vendor)
    return redirect(url_for('login'))

@app.route('/support_vendor')
@role_required('support')
def support_vendor_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_производителей_ПО'
        cur.execute(string)
        list_vendor = cur.fetchall()
        return render_template('support_vendor.html', list_vendor=list_vendor)
    return redirect(url_for('login'))

@app.route('/add_vendor', methods=['POST'])
def add_vendor():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_производителя = request.form['код_производителя']
        производитель = request.form['производитель']
        описание_производителя = request.form['описание_производителя']
        ссылка_на_сайт_производителя = request.form['ссылка_на_сайт_производителя']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Справочник_производителей_ПО (код_производителя, производитель, описание_производителя, ссылка_на_сайт_производителя, примечание) VALUES(%s,%s,%s,%s,%s)', (код_производителя, производитель, описание_производителя, ссылка_на_сайт_производителя, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('vendor_list'))
    
@app.route('/editor_add_vendor', methods=['POST'])
def editor_add_vendor():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_производителя = request.form['код_производителя']
        производитель = request.form['производитель']
        описание_производителя = request.form['описание_производителя']
        ссылка_на_сайт_производителя = request.form['ссылка_на_сайт_производителя']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Справочник_производителей_ПО (код_производителя, производитель, описание_производителя, ссылка_на_сайт_производителя, примечание) VALUES(%s,%s,%s,%s,%s)', (код_производителя, производитель, описание_производителя, ссылка_на_сайт_производителя, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('editor_vendor_list'))

@app.route('/edit_vendor/<id>', methods=['POST', 'GET'])
def edit_vendor(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_производителей_ПО WHERE код_производителя=%s', (id,))
    vendors = cur.fetchall()
    cur.close()
    return render_template('edit_vendor.html', vendor = vendors[0])

@app.route('/editor_edit_vendor/<id>', methods=['POST', 'GET'])
def editor_edit_vendor(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_производителей_ПО WHERE код_производителя=%s', (id,))
    vendors = cur.fetchall()
    cur.close()
    return render_template('editor_edit_vendor.html', vendor = vendors[0])

@app.route('/update_vendor/<id>', methods=['POST'])
def update_vendor(id):
    if request.method == 'POST':
        производитель = request.form['производитель']
        описание_производителя = request.form['описание_производителя']
        ссылка_на_сайт_производителя = request.form['ссылка_на_сайт_производителя']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_производителей_ПО
                    SET
                    производитель=%s,
                    описание_производителя=%s,
                    ссылка_на_сайт_производителя=%s,
                    примечание=%s
                    WHERE код_производителя=%s
                    """, (производитель, описание_производителя, ссылка_на_сайт_производителя, примечание, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('vendor_list'))
    
@app.route('/editor_update_vendor/<id>', methods=['POST'])
def editor_update_vendor(id):
    if request.method == 'POST':
        производитель = request.form['производитель']
        описание_производителя = request.form['описание_производителя']
        ссылка_на_сайт_производителя = request.form['ссылка_на_сайт_производителя']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_производителей_ПО
                    SET
                    производитель=%s,
                    описание_производителя=%s,
                    ссылка_на_сайт_производителя=%s,
                    примечание=%s
                    WHERE код_производителя=%s
                    """, (производитель, описание_производителя, ссылка_на_сайт_производителя, примечание, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('editor_vendor_list'))

@app.route('/delete_vendor/<string:id>', methods=['POST', 'GET'])
def delete_vendor(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_производителей_ПО WHERE код_производителя={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('vendor_list'))

@app.route('/editor_delete_vendor/<string:id>', methods=['POST', 'GET'])
def editor_delete_vendor(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_производителей_ПО WHERE код_производителя={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('editor_vendor_list'))

@app.route('/download_vendor/report/excel')
def download_vendor_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_производителей_ПО')
    result_vendor = cur.fetchall()
    output_vendor = io.BytesIO()
    workbook_vendor = xlwt.Workbook()
    sh_vendor = workbook_vendor.add_sheet('Отчет по производителям ПО')
    sh_vendor.write(0, 0, 'Код производителя')
    sh_vendor.write(0, 1, 'Производитель')
    sh_vendor.write(0, 2, 'Описание производителя')
    sh_vendor.write(0, 3, 'Ссылка на сайт производителя')
    sh_vendor.write(0, 4, 'Примечание')
    idx = 0
    for row in result_vendor:
        sh_vendor.write(idx+1, 0, str(row['код_производителя']))
        sh_vendor.write(idx+1, 1, row['производитель'])
        sh_vendor.write(idx+1, 2, row['описание_производителя'])
        sh_vendor.write(idx+1, 3, row['ссылка_на_сайт_производителя'])
        sh_vendor.write(idx+1, 4, row['примечание'])
        idx += 1
    workbook_vendor.save(output_vendor)
    output_vendor.seek(0)
    return Response(output_vendor, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=vendor_report.xls"})

@app.route('/customer')
@role_required('admin')
def customer_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_заказчиков_ПО'
        cur.execute(string)
        list_customer = cur.fetchall()
        return render_template('customer.html', list_customer=list_customer)
    return redirect(url_for('login'))

@app.route('/editor_customer')
@role_required('editor')
def editor_customer_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string= 'SELECT * FROM Справочник_заказчиков_ПО'
        cur.execute(string)
        list_customer = cur.fetchall()
        return render_template('editor_customer.html', list_customer=list_customer)
    return redirect(url_for('login'))

@app.route('/support_customer')
@role_required('support')
def support_customer_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_заказчиков_ПО'
        cur.execute(string)
        list_customer = cur.fetchall()
        return render_template('support_customer.html', list_customer=list_customer)
    return redirect(url_for('login'))

@app.route('/add_customer', methods=['POST'])
def add_customer():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_заказчика = request.form['код_заказчика']
        заказчик_ПО = request.form['заказчик_ПО']
        описание_заказчика = request.form['описание_заказчика']
        ссылка_на_сайт_заказчика = request.form['ссылка_на_сайт_заказчика']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Справочник_заказчиков_ПО (код_заказчика, заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, примечание) VALUES(%s,%s,%s,%s,%s)', (код_заказчика, заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('customer_list'))
    
@app.route('/editor_add_customer', methods=['POST'])
def editor_add_customer():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_заказчика = request.form['код_заказчика']
        заказчик_ПО = request.form['заказчик_ПО']
        описание_заказчика = request.form['описание_заказчика']
        ссылка_на_сайт_заказчика = request.form['ссылка_на_сайт_заказчика']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Справочник_заказчиков_ПО (код_заказчика, заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, примечание) VALUES(%s,%s,%s,%s,%s)', (код_заказчика, заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('editor_customer_list'))
    

@app.route('/edit_customer/<id>', methods=['POST','GET'])
def edit_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_заказчиков_ПО WHERE код_заказчика=%s', (id,))
    customers = cur.fetchall()
    cur.close()
    return render_template('edit_customer.html', customer=customers[0])

@app.route('/editor_edit_customer/<id>', methods=['POST', 'GET'])
def editor_edit_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_заказчиков_ПО WHERE код_заказчика=%s', (id,))
    customers = cur.fetchall()
    cur.close()
    return render_template('editor_edit_customer.html', customer=customers[0])

@app.route('/update_customer/<id>', methods=['POST'])
def update_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        заказчик_ПО = request.form['заказчик_ПО']
        описание_заказчика = request.form['описание_заказчика']
        ссылка_на_сайт_заказчика = request.form['ссылка_на_сайт_заказчика']
        примечание = request.form['примечание']
        cur.execute(""" UPDATE Справочник_заказчиков_ПО
                    SET
                    заказчик_ПО=%s,
                    описание_заказчика=%s,
                    ссылка_на_сайт_заказчика=%s,
                    примечание=%s
                    WHERE код_заказчика=%s
                    """, (заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, примечание, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('customer_list'))
    
@app.route('/editor_update_customer/<id>', methods=['POST'])
def editor_update_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        заказчик_ПО = request.form['заказчик_ПО']
        описание_заказчика = request.form['описание_заказчика']
        ссылка_на_сайт_заказчика = request.form['ссылка_на_сайт_заказчика']
        примечание = request.form['примечание']
        cur.execute(""" UPDATE Справочник_заказчиков_ПО
                    SET
                    заказчик_ПО=%s,
                    описание_заказчика=%s,
                    ссылка_на_сайт_заказчика=%s,
                    примечание=%s
                    WHERE код_заказчика=%s
                    """, (заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, примечание, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('editor_customer_list'))
    
@app.route('/delete_customer/<string:id>', methods=['POST', 'GET'])
def delete_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_заказчиков_ПО WHERE код_заказчика={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('customer_list'))

@app.route('/editor_delete_customer/<string:id>', methods=['POST', 'GET'])
def editor_delete_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_заказчиков_ПО WHERE код_заказчика={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('editor_customer_list'))

@app.route('/download_customer/report/excel')
def download_customer_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_заказчиков_ПО')
    result_customer = cur.fetchall()
    output_customer = io.BytesIO()
    workbook_customer = xlwt.Workbook()
    sh_customer = workbook_customer.add_sheet('Отчет по заказчикам')
    sh_customer.write(0, 0, 'Код заказчика')
    sh_customer.write(0, 1, 'Заказчик ПО')
    sh_customer.write(0, 2, 'Описание заказчика')
    sh_customer.write(0, 3, 'Ссылка на сайт заказчика')
    sh_customer.write(0, 4, 'Примечание')
    idx = 0
    for row in result_customer:
        sh_customer.write(idx+1, 0, str(row['код_заказчика']))
        sh_customer.write(idx+1, 1, row['заказчик_ПО'])
        sh_customer.write(idx+1, 2, row['описание_заказчика'])
        sh_customer.write(idx+1, 3, row['ссылка_на_сайт_заказчика'])
        sh_customer.write(idx+1, 4, row['примечание'])
        idx += 1
    workbook_customer.save(output_customer)
    output_customer.seek(0)
    return Response(output_customer, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=customer_report.xls"})

@app.route('/licence')
@role_required('admin')
def licence_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_лицензий'
        cur.execute(string)
        list_licence = cur.fetchall()
        return render_template('licence.html', list_licence=list_licence)
    return redirect(url_for('login'))

@app.route('/editor_licence')
@role_required('editor')
def editor_licence_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_лицензий'
        cur.execute(string)
        list_licence = cur.fetchall()
        return render_template('editor_licence.html', list_licence=list_licence)
    return redirect(url_for('login'))

@app.route('/support_licence')
@role_required('support')
def support_licence_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_лицензий'
        cur.execute(string)
        list_licence = cur.fetchall()
        return render_template('support_licence.html', list_licence=list_licence)
    return redirect(url_for('login'))
    
@app.route('/add_licence_to_list', methods=['POST'])
def add_licence_to_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_лицензии = request.form['код_лицензии']
        наименование_лицензии = request.form['наименование_лицензии']
        тип_лицензии = request.form['тип_лицензии']
        счёт_списания = request.form['счёт_списания']
        версия_лицензии = request.form['версия_лицензии']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Справочник_лицензий (код_лицензии, наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, примечание) VALUES(%s,%s,%s,%s,%s,%s)', (код_лицензии, наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('licence_list'))

@app.route('/editor_add_licence_to_list', methods=['POST'])
def editor_add_licence_to_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_лицензии = request.form['код_лицензии']
        наименование_лицензии = request.form['наименование_лицензии']
        тип_лицензии = request.form['тип_лицензии']
        счёт_списания = request.form['счёт_списания']
        версия_лицензии = request.form['версия_лицензии']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Справочник_лицензий (код_лицензии, наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, примечание) VALUES(%s,%s,%s,%s,%s,%s)', (код_лицензии, наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('editor_licence_list'))
    
@app.route('/edit_licence/<id>', methods=['POST', 'GET'])
def edit_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_лицензий WHERE код_лицензии=%s', (id))
    lic = cur.fetchall()
    return render_template('edit_licence.html', lice = lic[0])

@app.route('/editor_edit_licence/<id>', methods=['POST', 'GET'])
def editor_edit_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_лицензий WHERE код_лицензии=%s', (id))
    lic = cur.fetchall()
    return render_template('editor_edit_licence.html', lice = lic[0])

@app.route('/update_licence/<id>', methods=['POST'])
def update_licence_list(id):
    if request.method == 'POST':
        наименование_лицензии = request.form['наименование_лицензии']
        тип_лицензии = request.form['тип_лицензии']
        счёт_списания = request.form.get('счёт_списания')
        версия_лицензии = request.form['версия_лицензии']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_лицензий
                    SET наименование_лицензии=%s,
                    тип_лицензии=%s,
                    счёт_списания=%s,
                    версия_лицензии=%s,
                    примечание=%s
                    WHERE код_лицензии=%s
                    """, (наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, примечание, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('licence_list'))
    
@app.route('/editor_update_licence/<id>', methods=['POST'])
def editor_update_licence_list(id):
    if request.method == 'POST':
        наименование_лицензии = request.form['наименование_лицензии']
        тип_лицензии = request.form['тип_лицензии']
        счёт_списания = request.form.get('счёт_списания')
        версия_лицензии = request.form['версия_лицензии']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_лицензий
                    SET наименование_лицензии=%s,
                    тип_лицензии=%s,
                    счёт_списания=%s,
                    версия_лицензии=%s,
                    примечание=%s
                    WHERE код_лицензии=%s
                    """, (наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, примечание, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('editor_licence_list'))
    
@app.route('/delete_licence/<string:id>', methods=['POST', 'GET'])
def delete_licence_from_list(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_лицензий WHERE код_лицензии={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('licence_list'))

@app.route('/editor_delete_licence/<string:id>', methods=['POST', 'GET'])
def editor_delete_licence_from_list(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_лицензий WHERE код_лицензии={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('editor_licence_list'))

@app.route('/partners_list')
@role_required('admin')
def partners_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = "SELECT * FROM Контрагенты"
        cur.execute(string)
        partner_list = cur.fetchall()
        return render_template('partner.html', partner_list=partner_list)
    return redirect(url_for('login'))

@app.route('/editor_partners_list')
@role_required('editor')
def editor_partners_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = "SELECT * FROM Контрагенты"
        cur.execute(string)
        partner_list = cur.fetchall()
        return render_template('editor_partner.html', partner_list=partner_list)
    return redirect(url_for('login'))

@app.route('/support_partners_list')
@role_required('support')
def support_partners_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Контрагенты'
        cur.execute(string)
        partner_list = cur.fetchall()
        return render_template('support_partner.html', partner_list=partner_list)
    return redirect(url_for('login'))

@app.route('/add_partner', methods=['POST'])
def add_partner():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_контрагента = request.form['код_контрагента']
        наименование_контрагента = request.form['наименование_контрагента']
        договор = request.form['договор']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Контрагенты (код_контрагента, наименование_контрагента, договор, примечание) VALUES(%s,%s,%s,%s)', (код_контрагента, наименование_контрагента, договор, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('partners_list'))
    
@app.route('/editor_add_partner', methods=['POST'])
def editor_add_partner():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_контрагента = request.form['код_контрагента']
        наименование_контрагента = request.form['наименование_контрагента']
        договор = request.form['договор']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Контрагенты (код_контрагента, наименование_контрагента, договор, примечание) VALUES(%s,%s,%s,%s)', (код_контрагента, наименование_контрагента, договор, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('editor_partners_list'))
    
@app.route('/edit_partner/<id>', methods=['POST', 'GET'])
def edit_partner(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Контрагенты WHERE код_контрагента=%s', (id,))
    partners = cur.fetchall()
    return render_template('edit_partner.html', partner = partners[0])

@app.route('/editor_edit_partner/<id>', methods=['POST', 'GET'])
def editor_edit_partner(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Контрагенты WHERE код_контрагента=%s', (id,))
    partners=cur.fetchall()
    return render_template('editor_edit_partner.html', partner=partners[0])

@app.route('/update_partner/<id>', methods=['POST'])
def update_partner(id):
    if request.method == 'POST':
        наименование_контрагента = request.form['наименование_контрагента']
        договор = request.form['договор']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Контрагенты
                    SET наименование_контрагента=%s,
                    договор=%s,
                    примечание=%s
                    WHERE код_контрагента=%s
                    """, (наименование_контрагента, договор, примечание, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('partners_list'))
    
@app.route('/editor_update_partner/<id>', methods=['POST'])
def editor_update_partner(id):
    if request.method == 'POST':
        наименование_контрагента = request.form['наименование_контрагента']
        договор = request.form['договор']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Контрагенты
                    SET наименование_контрагента=%s,
                    договор=%s,
                    примечание=%s
                    WHERE код_контрагента=%s
                    """, (наименование_контрагента, договор, примечание, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('editor_partners_list'))
    
@app.route('/delete_partner/<string:id>', methods=['POST', 'GET'])
def delete_partner(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Контрагенты WHERE код_контрагента={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('partners_list'))

@app.route('/editor_delete_partner/<string:id>', methods=['POST', 'GET'])
def editor_delete_partner(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Контрагенты WHERE код_контрагента={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('editor_partners_list'))

@app.route('/download_partner/report/excel')
def download_partner_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Контрагенты')
    result_partner = cur.fetchall()
    output_partner = io.BytesIO()
    workbook_partner = xlwt.Workbook()
    sh_partner = workbook_partner.add_sheet('Отчет по контрагентам')
    sh_partner.write(0, 0, 'Код контрагента')
    sh_partner.write(0, 1, 'Наименование контрагента')
    sh_partner.write(0, 2, 'Договор')
    sh_partner.write(0, 3, 'Примечание')
    idx = 0
    for row in result_partner:
        sh_partner.write(idx+1, 0, str(row['код_контрагента']))
        sh_partner.write(idx+1, 1, row['наименование_контрагента'])
        sh_partner.write(idx+1, 2, row['договор'])
        sh_partner.write(idx+1, 3, row['примечание'])
        idx += 1
    workbook_partner.save(output_partner)
    output_partner.seek(0)
    return Response(output_partner, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=partner_report.xls"})

@app.route('/download_licence/report/excel')
def download_licence_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_лицензий')
    result_licence = cur.fetchall()
    output_licence = io.BytesIO()
    workbook_licence = xlwt.Workbook()
    sh_licence = workbook_licence.add_sheet('Отчет по лицензиям')
    sh_licence.write(0, 0, 'Код лицензии')
    sh_licence.write(0, 1, 'Наименование лицензии')
    sh_licence.write(0, 2, 'Тип лицензии')
    sh_licence.write(0, 3, 'Счёт списания')
    sh_licence.write(0, 4, 'Версия лицензии')
    sh_licence.write(0, 5, 'Примечание')
    idx = 0  
    for row in result_licence:
        sh_licence.write(idx+1, 0, str(row['код_лицензии']))
        sh_licence.write(idx+1, 1, row['наименование_лицензии'])
        sh_licence.write(idx+1, 2, row['тип_лицензии'])
        sh_licence.write(idx+1, 3, row['счёт_списания'])
        sh_licence.write(idx+1, 4, row['версия_лицензии'])
        sh_licence.write(idx+1, 5, row['примечание'])
        idx += 1
    workbook_licence.save(output_licence)
    output_licence.seek(0)
    return Response(output_licence, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=licence_report.xls"})

@app.route('/download/report/excel')
def download_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM лицензии')
    result = cur.fetchall()
    output = io.BytesIO()
    workbook = xlwt.Workbook()
    sh = workbook.add_sheet('Отчет')
    sh.write(0, 0, 'Номер пп')
    sh.write(0, 1, 'Наименование ПО')
    sh.write(0, 2, 'Вендор')
    sh.write(0, 3, 'Начало действия лицензии')
    sh.write(0, 4, 'Окончание действия лицензии')
    sh.write(0, 5, 'Счёт списания')
    sh.write(0, 6, 'Стоимость за единицу')
    sh.write(0, 7, 'Итоговая стоимость')
    sh.write(0, 8, 'Заказчик ПО')
    sh.write(0, 9, 'Признак ПО')
    sh.write(0, 10, 'Количество ПО')
    sh.write(0, 11, 'Срок действия лицензии')
    sh.write(0, 12, 'Оплачено')
    sh.write(0, 13, 'Остаток')
    sh.write(0, 14, 'Примечание')
    idx = 0
    for row in result:
        sh.write(idx+1, 0, str(row['номер_пп']))
        sh.write(idx+1, 1, row['наименование_ПО'])
        sh.write(idx+1, 2, row['вендор'])
        sh.write(idx+1, 3, row['начало_действия_лицензии'])
        sh.write(idx+1, 4, row['окончание_действия_лицензии'])
        sh.write(idx+1, 5, row['счёт_списания'])
        sh.write(idx+1, 6, row['стоимость_за_единицу'])
        sh.write(idx+1, 7, row['итоговая_стоимость'])
        sh.write(idx+1, 8, row['заказчик_ПО'])
        sh.write(idx+1, 9, row['признак_ПО'])
        sh.write(idx+1, 10, row['количество_ПО'])
        sh.write(idx+1, 11, row['срок_действия_лицензии'])
        sh.write(idx+1, 12, row['оплачено'])
        sh.write(idx+1, 13, row['остаток'])
        sh.write(idx+1, 14, row['примечание'])
        idx += 1
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=total_report.xls"})

@app.route('/support_install_software')
@role_required('support')
def support_install_software():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    string='SELECT код_установки, наименование_ПО, тип_лицензии, чекбокс, число_установленных_лицензий, дата_установки_ПО, чекбокс_условно_бесплатное_ПО, примечание FROM Установка_ПО'
    cur.execute(string)
    list_installation = cur.fetchall()
    return render_template('support_install.html', list_installation=list_installation)

@app.route('/editor_installation_software')
def editor_installation_software():
    if 'role' in session and session['role'] == 'editor':
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        string='SELECT * FROM Установка_ПО'
        cur.execute(string)
        list_installation = cur.fetchall()
        return render_template('editor_install.html', list_installation=list_installation)
    return redirect(url_for('login'))

@app.route('/install_software')
@role_required('admin')
def install_software():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    string='SELECT код_установки, наименование_ПО, тип_лицензии, чекбокс, число_установленных_лицензий, дата_установки_ПО, чекбокс_условно_бесплатное_ПО, примечание FROM Установка_ПО'
    cur.execute(string)
    list_installation = cur.fetchall()
    return render_template('install.html', list_installation=list_installation)

@app.route('/admin_add_installation', methods=['POST'])
def admin_add_installation():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_установки = request.form['код_установки']
        наименование_ПО = request.form['наименование_ПО']
        тип_лицензии = request.form.get('тип_лицензии')
        ФИО = request.form['ФИО']
        ip_адрес = request.form['ip_адрес']
        наименование_машины = request.form['наименование_машины']
        чекбокс = bool(request.form.get('чекбокс'))
        дата_установки_ПО = request.form.get('дата_установки_ПО')
        if not чекбокс:
            дата_установки_ПО = None
        if not дата_установки_ПО:
            дата_установки_ПО = None
        else:
            try:
                дата_установки_ПО = datetime.strptime(дата_установки_ПО, '%Y-%m-%d').date()
            except ValueError:
                flash('Некорректный формат даты!', 'warning')
                return redirect(url_for('install_software'))
        чекбокс_условно_бесплатное_ПО = bool(request.form.get('чекбокс_условно_бесплатное_ПО'))
        примечание = request.form['примечание']
        if чекбокс_условно_бесплатное_ПО:
            тип_лицензии = 'Условно-бесплатная'
        cur.execute("""SELECT количество_лицензий_ПО FROM Учет_лицензий
                    WHERE наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии))
        licence_data = cur.fetchone()
    
        if licence_data:
            общее_количество = licence_data['количество_лицензий_ПО']
        else:
            общее_количество = 0  
        cur.execute("""SELECT COUNT(*) AS count FROM Установка_ПО WHERE 
                    наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии)) 

        число_установленных_лицензий = cur.fetchone()['count']

        if чекбокс:
            число_установленных_лицензий += 1
        
        if чекбокс and дата_установки_ПО is None:
            flash('Введите дату установки ПО!')
            return redirect(url_for('install_software'))
        if дата_установки_ПО and дата_установки_ПО > datetime.now().date():
           flash('Дата установки ПО не может быть больше текущей даты!', 'warning')
           return redirect(url_for('install_software'))
        if not чекбокс_условно_бесплатное_ПО and число_установленных_лицензий > общее_количество:
           flash('Превышено количество доступных лицензий!', 'warning')
           return redirect(url_for('install_software'))
        else:
            cur.execute('INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины, чекбокс, общее_количество, число_установленных_лицензий, дата_установки_ПО, чекбокс_условно_бесплатное_ПО, примечание) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (код_установки, наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины, чекбокс, общее_количество, число_установленных_лицензий, дата_установки_ПО, чекбокс_условно_бесплатное_ПО, примечание))
            conn2.commit()
            flash('Запись успешно создана!')
            return redirect(url_for('install_software'))
        
@app.route('/add_installation', methods=['POST'])
def add_installation():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_установки = request.form['код_установки']
        наименование_ПО = request.form['наименование_ПО']
        тип_лицензии = request.form.get('тип_лицензии')
        ФИО = request.form['ФИО']
        ip_адрес = request.form['ip_адрес']
        наименование_машины = request.form['наименование_машины']
        чекбокс = bool(request.form.get('чекбокс'))
        дата_установки_ПО = request.form.get('дата_установки_ПО')
        if not чекбокс:
            дата_установки_ПО = None
        else:
            try:
                дата_установки_ПО = datetime.strptime(дата_установки_ПО, '%Y-%m-%d').date()
            except ValueError:
                flash('Введен некорректный формат даты', 'warning')
                return redirect(url_for('support_install_software'))
        чекбокс_условно_бесплатное_ПО = bool(request.form.get('чекбокс_условно_бесплатное_ПО'))
        примечание = request.form['примечание']
        cur.execute("""SELECT количество_лицензий_ПО FROM Учет_лицензий
                    WHERE наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии))
        licence_data = cur.fetchone()
    
        if licence_data:
            общее_количество = licence_data['количество_лицензий_ПО']
        else:
            общее_количество = 0  
        cur.execute("""SELECT COUNT(*) AS count FROM Установка_ПО WHERE 
                    наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии)) 
        число_установленных_лицензий = cur.fetchone()['count']
        if чекбокс: 
            число_установленных_лицензий += 1
            
        if чекбокс and дата_установки_ПО is None:
            flash('Введите дату установки ПО!')
            return redirect(url_for('support_install_software'))
        if дата_установки_ПО and дата_установки_ПО > datetime.now().date():
           flash('Дата установки ПО не может быть больше текущей даты!', 'warning')
           return redirect(url_for('support_install_software'))
        if not чекбокс_условно_бесплатное_ПО and число_установленных_лицензий > общее_количество:
           flash('Превышено количество доступных лицензий!', 'warning')
           return redirect(url_for('support_install_software'))
        else:
            cur.execute('INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины, чекбокс, общее_количество, число_установленных_лицензий, дата_установки_ПО, чекбокс_условно_бесплатное_ПО, примечание) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (код_установки, наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины, чекбокс, общее_количество, число_установленных_лицензий, дата_установки_ПО, чекбокс_условно_бесплатное_ПО, примечание))
            conn2.commit()
            flash('Запись успешно создана!')
            return redirect(url_for('support_install_software'))
    
@app.route('/edit_installation/<id>', methods=['POST', 'GET'])
def edit_installation(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Установка_ПО WHERE код_установки=%s', (id,))
    installations = cur.fetchall()
    return render_template('edit_installation.html', installation = installations[0])

@app.route('/admin_edit_installation/<id>', methods=['POST', 'GET'])
def admin_edit_installation(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Установка_ПО WHERE код_установки=%s", (id,))
    installations = cur.fetchall()
    return render_template('admin_edit_installation.html', installation = installations[0])


@app.route('/update_installation/<id>', methods=['POST'])
def update_installation(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        тип_лицензии = request.form['тип_лицензии']
        ФИО = request.form['ФИО']
        ip_адрес = request.form['ip_адрес']
        наименование_машины = request.form['наименование_машины']
        чекбокс = bool(request.form.get('чекбокс'))
        дата_установки_ПО = request.form['дата_установки_ПО']
        чекбокс_условно_бесплатное_ПО = bool(request.form.get('чекбокс_условно_бесплатное_ПО'))
        if чекбокс_условно_бесплатное_ПО:
            тип_лицензии = 'Условно-бесплатная'
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT наименование_ПО, тип_лицензии, число_установленных_лицензий , чекбокс
                    FROM Установка_ПО WHERE код_установки=%s""", (id,))
        installation_data = cur.fetchone() #данные из бд
        
        if not installation_data:
            flash('Установка с указанным ID не найдена!')
            return redirect(url_for('edit_installation', id=id))
        
        cur.execute("""SELECT количество_лицензий_ПО FROM Учет_лицензий
                    WHERE наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии))
        new_licence_data = cur.fetchone() #общее количество лицензий ПО

        if new_licence_data:
            общее_количество = new_licence_data['количество_лицензий_ПО']
        else:
            общее_количество = 0
        
        if installation_data['чекбокс'] != чекбокс:
            if чекбокс: #False to True
                if installation_data['тип_лицензии'] != тип_лицензии:
                    cur.execute("""SELECT COUNT(*) AS count FROM Установка_ПО WHERE 
                  наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии)) 
                    число_установленных_лицензий = cur.fetchone()['count']
                    if число_установленных_лицензий + 1 > общее_количество:
                        flash('Превышено допустимое количество лицензий!')
                        return redirect(url_for('edit_installation', id=id))
                    if installation_data['число_установленных_лицензий'] >0:
                        cur.execute(""" UPDATE Установка_ПО
                                    SET число_установленных_лицензий = число_установленных_лицензий - 1
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s
                                    """, (наименование_ПО, installation_data['тип_лицензии']))    
                        cur.execute(""" UPDATE Установка_ПО
                                    SET число_установленных_лицензий = число_установленных_лицензий + 1
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s
                                    """, (наименование_ПО, тип_лицензии))
                        cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                        max_id = cur.fetchone()[0]

                        new_id = max_id + 1

                        cur.execute("""
                             INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                             VALUES (%s, %s, %s, 1)
                         """, (new_id, наименование_ПО, тип_лицензии))
                        flash('Запись успешно обновлена!')
                        conn2.commit()
                        return redirect(url_for('support_install_software'))
                    else:
                        cur.execute("""UPDATE Установка_ПО
                                    SET число_установленных_лицензий = 0
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, installation_data['тип_лицензии']))
                        cur.execute("""UPDATE Установка_ПО
                                    SET число_установленных_лицензий = число_установленных_лицензий + 1
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, тип_лицензии))
                        cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                        max_id = cur.fetchone()[0]

                        new_id = max_id + 1

                        cur.execute("""
                             INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                             VALUES (%s, %s, %s, 1)
                         """, (new_id, наименование_ПО, тип_лицензии))
                        flash('Запись успешно обновлена!')
                        conn2.commit()
                        return redirect(url_for('support_install_software'))
                    
                cur.execute(""" UPDATE Установка_ПО
                            SET наименование_ПО=%s,
                            тип_лицензии=%s,
                            ФИО=%s,
                            ip_адрес=%s,
                            наименование_машины=%s,
                            чекбокс=%s,
                            общее_количество=%s,
                            дата_установки_ПО=%s,
                            чекбокс_условно_бесплатное_ПО=%s,
                            примечание=%s
                            WHERE код_установки=%s
                            """, (наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины,
                                   чекбокс, общее_количество,
                                   дата_установки_ПО, 
                                   чекбокс_условно_бесплатное_ПО, примечание, id))

                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('support_install_software'))
            else: #True to False
                if installation_data['число_установленных_лицензий'] > 0:
                    cur.execute("""UPDATE Установка_ПО SET число_установленных_лицензий = число_установленных_лицензий - 1
                                WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, тип_лицензии))
                    flash('Запись успешно обновлена!')
                    conn2.commit()
                    return redirect(url_for('support_install_software'))
                else:
                    cur.execute("""UPDATE Установка_ПО SET число_установленных_лицензий = 0
                                WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, тип_лицензии))
                    flash('Запись успешно обновлена!')
                    conn2.commit()
                    return redirect(url_for('support_install_software'))

        if not чекбокс:
            дата_установки_ПО = None
            cur.execute("""UPDATE Установка_ПО
                        SET число_установленных_лицензий = число_установленных_лицензий WHERE наименование_ПО=%s AND 
                        тип_лицензии=%s;""", (наименование_ПО, installation_data['тип_лицензии']))
            flash('Запись успешно обновлена!')
            conn2.commit()
            return redirect(url_for('support_install_software'))
        else:
            try:
                дата_установки_ПО = datetime.strptime(дата_установки_ПО, '%Y-%m-%d').date()
            except ValueError:
                flash('Введен некорректный формат даты', 'warning')
                return redirect(url_for('edit_installation', id=id))
            
        if чекбокс and дата_установки_ПО is None:
            flash('Введите дату установки ПО!')
            return redirect(url_for('edit_installation', id=id))
        if дата_установки_ПО and дата_установки_ПО > datetime.now().date():
           flash('Дата установки ПО не может быть больше текущей даты!', 'warning')
           return redirect(url_for('edit_installation', id=id))
        
       
        if installation_data['тип_лицензии'] != тип_лицензии:
            cur.execute("""SELECT COUNT(*) AS count FROM Установка_ПО WHERE 
          наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии)) 
            число_установленных_лицензий = cur.fetchone()['count']
            if число_установленных_лицензий + 1 > общее_количество:
                flash('Превышено допустимое количество лицензий!')
                return redirect(url_for('edit_installation', id=id))
            if installation_data['число_установленных_лицензий'] > 0:
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = число_установленных_лицензий - 1
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, installation_data['тип_лицензии']))    
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = число_установленных_лицензий + 1
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, тип_лицензии))
                cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                max_id = cur.fetchone()[0]

                new_id = max_id + 1

                cur.execute("""
                     INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                     VALUES (%s, %s, %s, 1)
                 """, (new_id, наименование_ПО, тип_лицензии))
                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('support_install_software'))
            else:
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = 0
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, installation_data['тип_лицензии']))    
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = число_установленных_лицензий + 1
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, тип_лицензии))
                cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                max_id = cur.fetchone()[0]

                new_id = max_id + 1

                cur.execute("""
                     INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                     VALUES (%s, %s, %s, 1)
                 """, (new_id, наименование_ПО, тип_лицензии))
                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('support_install_software'))
            
        cur.execute(""" UPDATE Установка_ПО
                    SET наименование_ПО=%s,
                    тип_лицензии=%s,
                    ФИО=%s,
                    ip_адрес=%s,
                    наименование_машины=%s,
                    чекбокс=%s,
                    общее_количество=%s,
                    дата_установки_ПО=%s,
                    чекбокс_условно_бесплатное_ПО=%s,
                    примечание=%s
                    WHERE код_установки=%s
                    """, (наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины,
                           чекбокс, общее_количество,
                           дата_установки_ПО, 
                           чекбокс_условно_бесплатное_ПО, примечание, id))

        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('support_install_software'))
    
@app.route('/admin_update_installation/<id>', methods=['POST'])
def admin_update_installation(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        тип_лицензии = request.form['тип_лицензии']
        ФИО = request.form['ФИО']
        ip_адрес = request.form['ip_адрес']
        наименование_машины = request.form['наименование_машины']
        чекбокс = bool(request.form.get('чекбокс'))
        дата_установки_ПО = request.form['дата_установки_ПО']
        чекбокс_условно_бесплатное_ПО = bool(request.form.get('чекбокс_условно_бесплатное_ПО'))
        if чекбокс_условно_бесплатное_ПО:
            тип_лицензии = 'Условно-бесплатная'
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""SELECT наименование_ПО, тип_лицензии, число_установленных_лицензий , чекбокс
                    FROM Установка_ПО WHERE код_установки=%s""", (id,))
        installation_data = cur.fetchone() #данные из бд
        
        if not installation_data:
            flash('Установка с указанным ID не найдена!')
            return redirect(url_for('admin_edit_installation', id=id))
        
        cur.execute("""SELECT количество_лицензий_ПО FROM Учет_лицензий
                    WHERE наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии))
        new_licence_data = cur.fetchone() #общее количество лицензий ПО

        if new_licence_data:
            общее_количество = new_licence_data['количество_лицензий_ПО']
        else:
            общее_количество = 0
        
        if installation_data['чекбокс'] != чекбокс:
            if чекбокс: #False to True
                if installation_data['тип_лицензии'] != тип_лицензии:
                    cur.execute("""SELECT COUNT(*) AS count FROM Установка_ПО WHERE 
                  наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии)) 
                    число_установленных_лицензий = cur.fetchone()['count']
                    if число_установленных_лицензий + 1 > общее_количество:
                        flash('Превышено допустимое количество лицензий!')
                        return redirect(url_for('admin_edit_installation', id=id))
                    if installation_data['число_установленных_лицензий'] > 0:
                        cur.execute(""" UPDATE Установка_ПО
                                    SET число_установленных_лицензий = число_установленных_лицензий - 1
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s
                                    """, (наименование_ПО, installation_data['тип_лицензии']))    
                        cur.execute(""" UPDATE Установка_ПО
                                    SET число_установленных_лицензий = число_установленных_лицензий + 1
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s
                                    """, (наименование_ПО, тип_лицензии))
                        cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                        max_id = cur.fetchone()[0]

                        new_id = max_id + 1

                        cur.execute("""
                             INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                             VALUES (%s, %s, %s, 1)
                         """, (new_id, наименование_ПО, тип_лицензии))
                        flash('Запись успешно обновлена!')
                        conn2.commit()
                        return redirect(url_for('install_software'))
                    else:
                        cur.execute("""UPDATE Установка_ПО
                                    SET число_установленных_лицензий = 0
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, installation_data['тип_лицензии']))
                        cur.execute("""UPDATE Установка_ПО
                                    SET число_установленных_лицензий = число_установленных_лицензий + 1
                                    WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, тип_лицензии))
                        cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                        max_id = cur.fetchone()[0]

                        new_id = max_id + 1

                        cur.execute("""
                             INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                             VALUES (%s, %s, %s, 1)
                         """, (new_id, наименование_ПО, тип_лицензии))
                        flash('Запись успешно обновлена!')
                        conn2.commit()
                        return redirect(url_for('install_software'))
                    
                cur.execute(""" UPDATE Установка_ПО
                            SET наименование_ПО=%s,
                            тип_лицензии=%s,
                            ФИО=%s,
                            ip_адрес=%s,
                            наименование_машины=%s,
                            чекбокс=%s,
                            общее_количество=%s,
                            дата_установки_ПО=%s,
                            чекбокс_условно_бесплатное_ПО=%s,
                            примечание=%s
                            WHERE код_установки=%s
                            """, (наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины,
                                   чекбокс, общее_количество,
                                   дата_установки_ПО, 
                                   чекбокс_условно_бесплатное_ПО, примечание, id))

                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('install_software'))
            else: #True to False
                if installation_data['число_установленных_лицензий'] > 0:
                    cur.execute("""UPDATE Установка_ПО SET число_установленных_лицензий = число_установленных_лицензий - 1
                                WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, тип_лицензии))
                    flash('Запись успешно обновлена!')
                    conn2.commit()
                    return redirect(url_for('install_software'))
                else:
                    cur.execute("""UPDATE Установка_ПО SET число_установленных_лицензий = 0
                                WHERE наименование_ПО=%s AND тип_лицензии=%s;""", (наименование_ПО, тип_лицензии))
                    flash('Запись успешно обновлена!')
                    conn2.commit()
                    return redirect(url_for('install_software'))

        if not чекбокс:
            дата_установки_ПО = None
            cur.execute("""UPDATE Установка_ПО
                        SET число_установленных_лицензий = число_установленных_лицензий WHERE наименование_ПО=%s AND 
                        тип_лицензии=%s;""", (наименование_ПО, installation_data['тип_лицензии']))
            flash('Запись успешно обновлена!')
            conn2.commit()
            return redirect(url_for('install_software'))
        else:
            try:
                дата_установки_ПО = datetime.strptime(дата_установки_ПО, '%Y-%m-%d').date()
            except ValueError:
                flash('Введен некорректный формат даты', 'warning')
                return redirect(url_for('admin_edit_installation', id=id))
            
        if чекбокс and дата_установки_ПО is None:
            flash('Введите дату установки ПО!')
            return redirect(url_for('edit_installation', (id,)))
        if дата_установки_ПО and дата_установки_ПО > datetime.now().date():
           flash('Дата установки ПО не может быть больше текущей даты!', 'warning')
           return redirect(url_for('admin_edit_installation', id=id))
        
       
        if installation_data['тип_лицензии'] != тип_лицензии:
            cur.execute("""SELECT COUNT(*) AS count FROM Установка_ПО WHERE 
          наименование_ПО=%s AND тип_лицензии=%s""", (наименование_ПО, тип_лицензии)) 
            число_установленных_лицензий = cur.fetchone()['count']
            if число_установленных_лицензий + 1 > общее_количество:
                flash('Превышено допустимое количество лицензий!')
                return redirect(url_for('admin_edit_installation', id=id))
            if installation_data['число_установленных_лицензий'] > 0:
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = число_установленных_лицензий - 1
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, installation_data['тип_лицензии']))    
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = число_установленных_лицензий + 1
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, тип_лицензии))
                cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                max_id = cur.fetchone()[0]

                new_id = max_id + 1

                cur.execute("""
                    INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                    VALUES (%s, %s, %s, 1)
                """, (new_id, наименование_ПО, тип_лицензии))
                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('install_software'))
            else:
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = 0
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, installation_data['тип_лицензии']))    
                cur.execute(""" UPDATE Установка_ПО
                            SET число_установленных_лицензий = число_установленных_лицензий + 1
                            WHERE наименование_ПО=%s AND тип_лицензии=%s
                            """, (наименование_ПО, тип_лицензии))
                cur.execute("SELECT MAX(код_установки) FROM Установка_ПО")
                max_id = cur.fetchone()[0]

                new_id = max_id + 1

                cur.execute("""
                     INSERT INTO Установка_ПО (код_установки, наименование_ПО, тип_лицензии, число_установленных_лицензий)
                     VALUES (%s, %s, %s, 1)
                 """, (new_id, наименование_ПО, тип_лицензии))
                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('install_software'))
        
                flash('Запись успешно обновлена!')
                conn2.commit()
                return redirect(url_for('install_software'))
            
        cur.execute(""" UPDATE Установка_ПО
                    SET наименование_ПО=%s,
                    тип_лицензии=%s,
                    ФИО=%s,
                    ip_адрес=%s,
                    наименование_машины=%s,
                    чекбокс=%s,
                    общее_количество=%s,
                    дата_установки_ПО=%s,
                    чекбокс_условно_бесплатное_ПО=%s,
                    примечание=%s
                    WHERE код_установки=%s
                    """, (наименование_ПО, тип_лицензии, ФИО, ip_адрес, наименование_машины,
                           чекбокс, общее_количество,
                           дата_установки_ПО, 
                           чекбокс_условно_бесплатное_ПО, примечание, id))

        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('install_software'))
    
@app.route('/delete_installation/<string:id>', methods=['POST', 'GET'])
def delete_installation(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT наименование_ПО, тип_лицензии, число_установленных_лицензий FROM Установка_ПО WHERE код_установки=%s', (id,))
    installation_info = cur.fetchone()
    if installation_info:
        число_установленных_лицензий = installation_info['число_установленных_лицензий']
        if число_установленных_лицензий > 0:
            cur.execute(
                """
                UPDATE Установка_ПО
                SET число_установленных_лицензий = число_установленных_лицензий - 1 
                WHERE код_установки=%s;
                """,
                (id,),
            )
            conn2.commit()
    
            cur.execute('DELETE FROM Установка_ПО WHERE код_установки={0}'.format(id))
            conn2.commit()
    
            flash('Запись успешно удалена!')
        else:
            cur.execute("""UPDATE Установка_ПО
                        SET число_установленных_лицензий = 0
                        WHERE код_установки=%s;""", (id,))
            conn2.commit()
            cur.execute('DELETE FROM Установка_ПО WHERE код_установки={0}'.format(id))
            conn2.commit()
            flash('Запись успешно удалена!')
    else:
        flash('Запись не найдена!')

    return redirect(url_for('support_install_software'))

@app.route('/admin_delete_installation/<string:id>', methods=['POST', 'GET'])
def admin_delete_installation(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT наименование_ПО, тип_лицензии, число_установленных_лицензий FROM Установка_ПО WHERE код_установки=%s', (id,))
    installation_info = cur.fetchone()
    if installation_info:
        число_установленных_лицензий = installation_info['число_установленных_лицензий']
        if число_установленных_лицензий > 0:
            cur.execute(
                """
                UPDATE Установка_ПО
                SET число_установленных_лицензий = число_установленных_лицензий - 1 
                WHERE код_установки=%s;
                """,
                (id,),
            )
            conn2.commit()
    
            cur.execute('DELETE FROM Установка_ПО WHERE код_установки={0}'.format(id))
            conn2.commit()
    
            flash('Запись успешно удалена!')
        else:
            cur.execute("""UPDATE Установка_ПО
                        SET число_установленных_лицензий = 0
                        WHERE код_установки=%s;""", (id,))
            conn2.commit()
            cur.execute('DELETE FROM Установка_ПО WHERE код_установки={0}'.format(id))
            conn2.commit()
            flash('Запись успешно удалена!')
    else:
        flash('Запись не найдена!')

    return redirect(url_for('install_software'))

@app.route('/download/software_install_report/excel')
def download_software_install_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Установка_ПО')
    result = cur.fetchall()
    output = io.BytesIO()
    workbook = xlwt.Workbook()
    sh = workbook.add_sheet('Отчет')
    sh.write(0, 0, 'Код установки')
    sh.write(0, 1, 'Наименование ПО')
    sh.write(0, 2, 'Тип лицензии')
    sh.write(0, 3, 'ФИО')
    sh.write(0, 4, 'IP адрес')
    sh.write(0, 5, 'Наименование машины')
    sh.write(0, 6, 'Чекбокс')
    sh.write(0, 7, 'Общее количество')
    sh.write(0, 8, 'Число установленных лицензий')
    sh.write(0, 9, 'Дата установки ПО')
    sh.write(0, 10, 'Чекбокс условно-бесплатное ПО')
    sh.write(0, 11, 'Примечание')
    idx = 0
    for row in result:
        sh.write(idx+1, 0, str(row['код_установки']))
        sh.write(idx+1, 1, row['наименование_ПО'])
        sh.write(idx+1, 2, row['тип_лицензии'])
        sh.write(idx+1, 3, row['ФИО'])
        sh.write(idx+1, 4, row['ip_адрес'])
        sh.write(idx+1, 5, row['наименование_машины'])
        sh.write(idx+1, 6, row['чекбокс'])
        sh.write(idx+1, 7, row['общее_количество'])
        sh.write(idx+1, 8, row['число_установленных_лицензий'])
        sh.write(idx+1, 9, row['дата_установки_ПО'])
        sh.write(idx+1, 10, row['чекбокс_условно_бесплатное_ПО'])
        sh.write(idx+1, 11, row['примечание'])
        idx += 1
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=software_installation_report.xls"})

@app.route('/number_licences')
@role_required('admin')
def number_licences():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = ('SELECT * FROM Учет_лицензий')
        cur.execute(string)
        list_number = cur.fetchall()
        return render_template('number.html', list_number=list_number)
    return redirect(url_for('login'))

@app.route('/editor_number_licences')
@role_required('editor')
def editor_number_licences():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = 'SELECT * FROM Учет_лицензий'
        cur.execute(string)
        list_number = cur.fetchall()
        return render_template('editor_number.html', list_number=list_number)
    return redirect(url_for('login'))

@app.route('/view_number_licences')
@role_required('support')
def view_number_licences():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = ('SELECT * FROM Учет_лицензий')
        cur.execute(string)
        list_number = cur.fetchall()
        return render_template('support_number.html', list_number=list_number)
    return redirect(url_for('login'))

@app.route('/add_number', methods=['POST'])
def add_number():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        номер_заявки = request.form['номер_заявки']
        наименование_ПО = request.form['наименование_ПО']
        тип_лицензии = request.form.get('тип_лицензии')
        количество_лицензий_ПО = request.form['количество_лицензий_ПО']
        примечание = request.form['примечание']
        cur.execute('INSERT INTO Учет_лицензий (номер_заявки, наименование_ПО, тип_лицензии, количество_лицензий_ПО, примечание) VALUES(%s,%s,%s,%s,%s)', (номер_заявки, наименование_ПО, тип_лицензии, количество_лицензий_ПО, примечание))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('number_licences'))
    

@app.route('/edit_number/<id>', methods=['POST', 'GET'])
def edit_number(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Учет_лицензий WHERE номер_заявки=%s', (id,))
    numbers = cur.fetchall()
    return render_template('edit_number.html', number = numbers[0])

@app.route('/update_number/<id>', methods=['POST'])
def update_number(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        тип_лицензии = request.form.get('тип_лицензии')
        количество_лицензий_ПО = request.form['количество_лицензий_ПО']
        примечание = request.form['примечание']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Учет_лицензий
                    SET наименование_ПО=%s,
                    тип_лицензии=%s,
                    количество_лицензий_ПО=%s,
                    примечание=%s
                    WHERE номер_заявки=%s
                    """, (наименование_ПО, тип_лицензии, количество_лицензий_ПО, примечание, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('number_licences'))
    
@app.route('/delete_number/<string:id>', methods=['POST', 'GET'])
def delete_number(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Учет_лицензий WHERE номер_заявки={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('number_licences'))

@app.route('/download/number_report/excel')
def download_number_report():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Учет_лицензий')
    result = cur.fetchall()
    output = io.BytesIO()
    workbook = xlwt.Workbook()
    sh = workbook.add_sheet('Отчет')
    sh.write(0, 0, 'Номер заявки')
    sh.write(0, 1, 'Наименование ПО')
    sh.write(0, 2, 'Тип лицензии')
    sh.write(0, 3, 'Количество лицензий ПО')
    sh.write(0, 4, 'Примечание')
    idx = 0
    for row in result:
        sh.write(idx+1, 0, str(row['номер_заявки']))
        sh.write(idx+1, 1, row['наименование_ПО'])
        sh.write(idx+1, 2, row['тип_лицензии'])
        sh.write(idx+1, 3, row['количество_лицензий_ПО'])
        sh.write(idx+1, 4, row['примечание'])
        idx += 1
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=number_report.xls"})

@app.route('/user_change_password', methods = ['POST', 'GET'])
def user_change_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
        account = cur.fetchone()
        if request.method == 'POST':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            if not old_password or not new_password:
                flash('Пожалуйста, заполните форму!')
            else:
                if account:
                        if not check_password_hash(account['password'], old_password):
                            flash('Неверный старый пароль!')
                            return redirect(url_for('user_change_password'))
                        if old_password == new_password:
                            flash('Пароли совпадают!')
                            return redirect(url_for('user_change_password'))
                        id=account['id']
                        _hashed_password = generate_password_hash(new_password)
                        cur.execute("""UPDATE users
                                    SET password=%s
                                    WHERE id=%s
                                    """, (_hashed_password, id))
                        flash('Запись успешно обновлена!')
                        conn.commit()
                        return redirect(url_for('profile'))
                else:
                    flash('Введены некорректные данные!')
                    return redirect(url_for('user_change_password'))
        return render_template('profile_change_password.html', title="Поменять пароль")
    
@app.route('/support_change_password', methods=['POST', 'GET'])
def support_change_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
        account = cur.fetchone()
        if request.method == 'POST':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            if not old_password or not new_password:
                flash('Пожалуйста, заполните форму!')
            else:
                if account:
                    if not check_password_hash(account['password'], old_password):
                        flash('Неверный старый пароль!')
                        return redirect(url_for('support_change_password'))
                    if old_password == new_password:
                        flash('Пароли совпадают!')
                        return redirect(url_for('support_change_password'))
                    id=account['id']
                    _hashed_password = generate_password_hash(new_password)
                    cur.execute("""UPDATE users
                                SET password=%s
                                WHERE id=%s""", (_hashed_password, id))
                    flash('Запись успешно обновлена!')
                    conn.commit()
                    return redirect(url_for('support_profile'))
                else:
                    flash('Введены некорректные данные!')
                    return redirect(url_for('support_change_password'))
        return render_template('support_change_password.html', title='Поменять пароль')
    
@app.route('/editor_change_password', methods=['POST', 'GET'])
def editor_change_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
        account = cur.fetchone()
        if request.method == 'POST':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            if not old_password or not new_password:
                flash('Пожалуйста, заполните форму!')
            else:
                if account:
                    if not check_password_hash(account['password'], old_password):
                        flash('Неверный старый пароль!')
                        return redirect(url_for('editor_change_password'))
                    if old_password == new_password:
                        flash('Пароли совпадают!')
                        return redirect(url_for('editor_change_password'))
                    id=account['id']
                    _hashed_password = generate_password_hash(new_password)
                    cur.execute("""UPDATE users
                                SET password=%s
                                WHERE id=%s""", (_hashed_password, id))
                    flash('Запись успешно обновлена!')
                    conn.commit()
                    return redirect(url_for('editor_profile'))
                else:
                    flash('Введены некорректные данные!')
                    return redirect(url_for('editor_change_password'))
        return render_template('editor_change_password.html', title='Поменять пароль')
    

@app.route('/user_change_email', methods=['POST', 'GET'])
def user_change_email():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            new_email = request.form.get('new_email')
            if not new_email:
                flash("Пожалуйста, заполните форму!")
            else:
                cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
                account = cur.fetchone()
                if account:
                    if new_email == session['email']:
                        flash('Новый адрес электронной почты совпадает с предыдущим!')
                        return redirect(url_for('user_change_email'))
                    id = account['id']
                    cur.execute("""UPDATE users
                                SET email=%s
                                WHERE id=%s""", (new_email, id))
                    flash('Запись успешно обновлена!')
                    conn.commit()
                    session['email'] = new_email  
                    return redirect(url_for('profile'))
                else:
                    flash('Введен некорректный адрес электронной почты!')
                    return redirect(url_for('user_change_email'))
        return render_template('change_email.html', title='Поменять адрес электронной почты')

@app.route('/support_change_email', methods=['POST', 'GET'])
def support_change_email():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            new_email = request.form.get('new_email')
            if not new_email:
                flash('Пожалуйста, заполните форму!')
            else:
                cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
                account = cur.fetchone()
                if account:
                    if new_email == session['email']:
                        flash('Новый адрес электронной почты совпадает с предыдущим!')
                        return redirect(url_for('support_change_email'))
                    id = account['id']
                    cur.execute("""UPDATE users
                                SET email=%s
                                WHERE id=%s""", (new_email, id))
                    flash('Запись успешно обновлена!')
                    conn.commit()
                    session['email'] = new_email
                    return redirect(url_for('support_profile'))
                else:
                    flash('Введен некорректный адрес электронной почты!')
                    return redirect(url_for('support_change_email'))
        return render_template('support_change_email.html', title='Поменять адрес электронной почты')

@app.route('/editor_change_email', methods=['POST', 'GET'])
def editor_change_email():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            new_email = request.form.get('new_email')
            if not new_email:
                flash('Пожалуйста, заполните форму!')
            else:
                cur.execute('SELECT * FROM users WHERE username=%s', (session['username'],))
                account = cur.fetchone()
                if account:
                    if new_email == session['email']:
                        flash('Новый адрес электронной почты совпадает с предыдущим!')
                        return redirect(url_for('editor_change_email'))
                    id = account['id']
                    cur.execute("""UPDATE users
                                SET email=%s
                                WHERE id=%s""", (new_email, id))
                    flash('Запись успешно обновлена!')
                    conn.commit()
                    session['email'] = new_email
                    return redirect(url_for('editor_profile'))
                else:
                    flash('Введен некорректный адрес электронной почты!')
                    return redirect(url_for('editor_change_email'))
        return render_template('editor_change_email.html', title='Поменять адрес электронной почты')

@app.route('/profile_reset_password', methods=['POST', 'GET'])
def profile_reset_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        email = request.form.get('email')
        user_otp = request.form.get('otp')
        current_email = session.get('email')
        if email != current_email:
            flash('Введенный адрес электронной почты не совпадает с предыдущим!')
            return render_template('profile_reset_password.html')
        cur.execute('SELECT * FROM users WHERE email=%s', (session['email'],))
        user = cur.fetchone()
        if not user:
            flash('Неправильный адрес электронной почты! Пожалуйста, попробуйте еще раз.')
            return render_template('profile_reset_password.html') 
        if user_otp:
            otp = session.get('otp')
            if otp == int(user_otp):
                return redirect(url_for('profile_change_password', email=email))
            else:
                flash('Неверный код подтверждения!')
                return render_template('profile_reset_password.html', email=email)
        else:
            otp = randint(000000, 999999)
            send_email(email, otp)
            session['otp'] = otp
            flash('Код подтверждения отправлен вам на адрес электронной почты!')
            return render_template('profile_reset_password.html', email=email)
    return render_template('profile_reset_password.html', title='Пользователь забыл пароль')

@app.route('/profile_support_reset_password', methods=['POST', 'GET'])
def profile_support_reset_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        email = request.form.get('email')
        user_otp = request.form.get('otp')
        current_email = session.get('email')
        if email != current_email:
            flash('Введенный адрес электронной почты не совпадает с предыдущим!')
            return render_template('profile_support_reset_password.html')
        cur.execute('SELECT * FROM users WHERE email=%s', (session['email'],))
        user = cur.fetchone()
        if not user:
            flash('Неправильный адрес электронной почты! Пожалуйста, попробуйте еще раз.')
            return render_template('profile_support_reset_password.html') 
        if user_otp:
            otp = session.get('otp')
            if otp == int(user_otp):
                return redirect(url_for('profile_support_change_password', email=email))
            else:
                flash('Неверный код подтверждения!')
                return render_template('profile_support_reset_password.html', email=email)
        else:
            otp = randint(000000, 999999)
            send_email(email, otp)
            session['otp'] = otp
            flash('Код подтверждения отправлен вам на адрес электронной почты!')
            return render_template('profile_support_reset_password.html', email=email)
    return render_template('profile_support_reset_password.html', title='Пользователь забыл пароль')

@app.route('/profile_editor_reset_password', methods=['POST', 'GET'])
def profile_editor_reset_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method=='POST':
        email = request.form.get('email')
        user_otp = request.form.get('otp')
        current_email = session.get('email')
        if email != current_email:
            flash('Введенный адрес электронной почты не совпадает с предыдущим!')
            return render_template('profile_editor_reset_password.html')
        cur.execute('SELECT * FROM users WHERE email=%s', (session['email'],))
        user = cur.fetchone()
        if not user:
            flash('Неправильный адрес электронной почты! Пожалуйста, попробуйте еще раз. ')
            return render_template('profile_editor_reset_password.html')
        if user_otp:
            otp = session.get('otp')
            if otp == int(user_otp):
                return redirect(url_for('profile_editor_change_password', email=email))
            else:
                flash('Неверный код подтверждения!')
                return render_template('profile_editor_reset_password.html', email=email)
        else:
            otp = randint(000000, 999999)
            send_email(email, otp)
            session['otp'] = otp
            flash('Код подтверждения отправлен вам на адрес электронной почты!')
            return render_template('profile_editor_reset_password.html', email=email)
    return render_template('profile_editor_reset_password.html', title='Пользователь забыл пароль ')

@app.route('/reset_email', methods=['POST', 'GET'])
def reset_email():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        cur.execute('SELECT * FROM users WHERE phone_number=%s', (phone_number,))
        user = cur.fetchone()
        
        if not user:
            flash('Неправильный номер телефона! Пожалуйста, попробуйте еще раз.')
            return render_template('reset_email.html')
        else:
            return redirect(url_for('change_password_email', phone_number=phone_number))
    return render_template('reset_email.html', title='Пользователь забыл адрес электронной почты')
    

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        email = request.form.get('email')
        user_otp = request.form.get('otp')

        cur.execute('SELECT * FROM users WHERE email=%s', (email,))
        user = cur.fetchone()

        if not user:
            flash('Неправильный адрес электронной почты! Пожалуйста, попробуйте еще раз.')
            return render_template('reset_password.html')

        if user_otp:
            otp = session.get('otp')
            if otp == int(user_otp):
                return redirect(url_for('change_password', email=email))
            else:
                flash('Неверный код подтверждения!')
                return render_template('reset_password.html', email=email)
        else:
            otp = randint(000000, 999999)
            send_email(email, otp)
            session['otp'] = otp
            flash('Код подтверждения отправлен вам на адрес электронной почты!')
            return render_template('reset_password.html', email=email)

    return render_template('reset_password.html', title='Пользователь забыл пароль')

def send_email(email, otp):
    msg = MIMEText(str(otp))
    msg['Subject'] = 'OTP'
    msg['From'] = 'Analstasia.Sholokhova@yandex.ru'
    msg['To'] = email

    with smtplib.SMTP('smtp.yandex.ru', 587) as smtp:
        smtp.starttls()
        smtp.login('Analstasia.Sholokhova@yandex.ru', 'xyanueciccoxachh')
        smtp.send_message(msg)
        
@app.route('/change_password_email/<phone_number>', methods=['POST', 'GET'])
def change_password_email(phone_number):
    cur= conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT password FROM users WHERE phone_number=%s', (phone_number,))
    user = cur.fetchone()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if check_password_hash(user['password'], new_password):
            flash('Новый пароль совпадает с текущим!')
            return redirect(url_for('change_password_email', phone_number=phone_number))
        _hashed_password = generate_password_hash(new_password)
        cur.execute("""UPDATE users
                    SET password=%s
                    WHERE phone_number=%s""", (_hashed_password, phone_number))
        flash('Пароль успешно обновлен!')
        conn.commit()
        return redirect(url_for('login'))
    return render_template('change_password_email.html', phone_number=phone_number, title='Изменить пароль')

@app.route('/change_password/<email>', methods=['POST', 'GET'])
def change_password(email):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT password FROM users WHERE email=%s', (email,))
    user = cur.fetchone()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if check_password_hash(user['password'], new_password):
            flash('Новый пароль совпадает с текущим паролем!')
            return redirect(url_for('change_password', email=email))
        _hashed_password = generate_password_hash(new_password)
        cur.execute("""UPDATE users
                    SET password=%s
                    WHERE email=%s""", (_hashed_password, email))
        flash('Пароль успешно обновлен!')
        conn.commit()
        return redirect(url_for('login'))
    return render_template('change_password.html', email=email, title='Изменить пароль')

@app.route('/profile_change_password/<email>', methods=['POST', 'GET'])
def profile_change_password(email):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if check_password_hash(user['password'], new_password):
            flash('Новый пароль совпадает с текущим паролем!')
            return redirect(url_for('profile_change_password', email=email))
        _hashed_password = generate_password_hash(new_password)
        cur.execute("""UPDATE users
                    SET password=%s
                    WHERE email=%s""", (_hashed_password, email))
        flash('Пароль успешно обновлен!')
        conn.commit()
        return redirect(url_for('profile'))
    return render_template('success_change_password.html', email=email, title='Изменить пароль')

@app.route('/profile_support_change_password/<email>', methods=['POST', 'GET'])
def profile_support_change_password(email):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if check_password_hash(user['password'], new_password):
            flash('Новый пароль совпадает с текущим паролем!')
            return redirect(url_for('profile_support_change_password', email=email))
        _hashed_password = generate_password_hash(new_password)
        cur.execute("""UPDATE users
                    SET password=%s
                    WHERE email=%s""", (_hashed_password, email))
        flash('Пароль успешно обновлен!')
        conn.commit()
        return redirect(url_for('support_profile'))
    return render_template('success_support_change_password.html', email=email, title='Изменить пароль')

@app.route('/profile_editor_change_password/<email>', methods=['POST', 'GET'])
def profile_editor_change_password(email):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT( password FROM users WHERE email=%s', (email,))
    user = cur.fetchone()
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if check_password_hash(user['password'], new_password):
            flash('Новый пароль совпадает с текущим паролем!')
            return redirect(url_for('profile_editor_change_password', email=email))
        _hashed_password = generate_password_hash(new_password)
        cur.execute("""UPDATE users
                    SET password=%s
                    WHERE email=%s""", (_hashed_password, email))
        flash('Пароль успешно обновлен!')
        conn.commit()
        return redirect(url_for('editor_profile'))
    return render_template('success_editor_change_password.html', email=email, title='Изменить пароль')


@app.route('/page/<software>')
def show_installation_details(software):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT код_установки, ФИО, ip_адрес, наименование_машины, дата_установки_ПО, тип_лицензии FROM Установка_ПО WHERE наименование_ПО=%s AND чекбокс=True", (software,))
    list_installation = cur.fetchall()
    return render_template('software_description.html', list_installation=list_installation, software=software)

@app.route('/support_page/<software>')
def support_show_installation_details(software):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
            SELECT код_установки, ФИО, ip_адрес, наименование_машины, дата_установки_ПО, тип_лицензии
            FROM Установка_ПО 
            WHERE наименование_ПО = %s AND чекбокс=True
        """, (software,))
    list_installation = cur.fetchall()
    return render_template('support_software_description.html', list_installation=list_installation, software=software)


@app.route('/download/soft_report/excel/<software>')
def download_soft_report(software):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT код_установки, ФИО, ip_адрес, наименование_машины, дата_установки_ПО, тип_лицензии FROM Установка_ПО WHERE наименование_ПО=%s AND чекбокс=True', (software,))
    result = cur.fetchall()
    output = io.BytesIO()
    workbook = xlwt.Workbook()
    sh = workbook.add_sheet('Отчет')
    sh.write(0, 0, 'Код установки')
    sh.write(0, 1, 'ФИО')
    sh.write(0, 2, 'IP адрес')
    sh.write(0, 3, 'Наименование машины')
    sh.write(0, 4, 'Дата установки ПО')
    sh.write(0, 5, 'Тип лицензии')
    idx = 0
    for row in result:
        sh.write(idx+1, 0, str(row['код_установки']))
        sh.write(idx+1, 1, row['ФИО'])
        sh.write(idx+1, 2, row['ip_адрес'])
        sh.write(idx+1, 3, row['наименование_машины'])
        sh.write(idx+1, 4, row['дата_установки_ПО'])
        sh.write(idx+1, 5, row['тип_лицензии'])
        idx += 1
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=soft_report.xls"})

if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5000)
