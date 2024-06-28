from flask import Flask, request, session, redirect, url_for, render_template, flash, Response
import psycopg2 #pip install psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
import io
import xlwt
 
app = Flask(__name__)
app.secret_key = 'anastasia-database'
 
DB_HOST = "localhost"
DB_NAME = "Users"
DB_NAME2 = 'software_licences'
DB_USER = "postgres"
DB_PASS = "12345"



conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)#подключение БД пользователей
conn2 = psycopg2.connect(dbname=DB_NAME2, user=DB_USER, password=DB_PASS, host=DB_HOST)#подключение БД реестра лицензий
 
@app.route('/')
def home():
    if 'loggedin' in session:
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = 'SELECT * FROM лицензии'
        cur.execute(s) #Execute SQL
        list_licences = cur.fetchall()
        return render_template('home.html', username=session['username'], list_licences = list_licences)
    return redirect(url_for('login'))
 
    
@app.route('/add_licence', methods=['POST'])
def add_licence():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method== 'POST':
        номер_пп = request.form['номер_пп']
        наименование_ПО = request.form['наименование_ПО']
        вендор = request.form['вендор']
        начало_действия_лицензии = request.form['начало_действия_лицензии']
        окончание_действия_лицензии = request.form['окончание_действия_лицензии']
        срок_полезного_использования_мес = request.form['срок_полезного_использования_мес']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        итоговая_стоимость = request.form['итоговая_стоимость']
        заказчик_ПО = request.form['заказчик_ПО']
        признак_ПО = request.form['признак_ПО']
        количество_ПО = request.form['количество_ПО']
        тип_ПО = request.form['тип_ПО']
        cur.execute("INSERT INTO лицензии (номер_пп, наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, срок_полезного_использования_мес, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, тип_ПО) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (номер_пп, наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, срок_полезного_использования_мес, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, тип_ПО))
        conn2.commit()
        flash('Запись была успешно добавлена!')
        return redirect(url_for('home'))
    
@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM лицензии WHERE номер_пп = %s', (id))
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', licence = data[0])

@app.route('/update/<id>', methods=['POST'])
def update_licence(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        вендор = request.form['вендор']
        начало_действия_лицензии = request.form['начало_действия_лицензии']
        окончание_действия_лицензии = request.form['окончание_действия_лицензии']
        срок_полезного_использования_мес = request.form['срок_полезного_использования_мес']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        итоговая_стоимость = request.form['итоговая_стоимость']
        заказчик_ПО = request.form['заказчик_ПО']
        признак_ПО = request.form['признак_ПО']
        количество_ПО = request.form['количество_ПО']
        тип_ПО = request.form['тип_ПО']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE лицензии
                    SET
                    наименование_ПО=%s,
                    вендор=%s,
                    начало_действия_лицензии=%s,
                    окончание_действия_лицензии=%s,
                    срок_полезного_использования_мес=%s,
                    стоимость_за_единицу=%s,
                    итоговая_стоимость=%s,
                    заказчик_ПО=%s,
                    признак_ПО=%s,
                    количество_ПО=%s,
                    тип_ПО=%s
                    WHERE номер_пп=%s
                    """, (наименование_ПО, вендор, начало_действия_лицензии, окончание_действия_лицензии, срок_полезного_использования_мес, стоимость_за_единицу, итоговая_стоимость, заказчик_ПО, признак_ПО, количество_ПО, тип_ПО, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('home'))
    
@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM лицензии WHERE номер_пп = {0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('home'))
                
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                flash('Неверное имя пользователя/пароль')
        else:
            flash('Неверное имя пользователя/пароль')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)

        if account:
            flash('Аккаунт уже зарегистрирован!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Некорректный адрес электронной почты!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Имя пользователя должно содержать только буквы и цифры!')
        elif not username or not password or not email:
            flash('Пожалуйста, заполните форму!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('Вы были успешно зарегистрированы!')
    elif request.method == 'POST':
        flash('Пожалуйста, заполните форму!')
    return render_template('register.html')
   
   
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))
 
@app.route('/software')
def software_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_ПО'
        cur.execute(string)
        list_software = cur.fetchall()
        return render_template('software.html', list_software=list_software)
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
        признак_ПО = request.form['признак_ПО']
        тип_ПО = request.form['тип_ПО']
        cur.execute("INSERT INTO Справочник_ПО (код_ПО, наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, тип_ПО) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)", (код_ПО, наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, тип_ПО))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('software_list'))

@app.route('/edit_software/<id>', methods=['POST', 'GET'])
def edit_software(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_ПО WHERE код_ПО=%s', (id))
    get_software = cur.fetchall()
    cur.close()
    print(get_software[0])
    return render_template('edit_software.html', software=get_software[0])

@app.route('/update_software/<id>', methods=['POST'])
def update_software(id):
    if request.method == 'POST':
        наименование_ПО = request.form['наименование_ПО']
        описание_ПО = request.form['описание_ПО']
        ссылка_на_сайт_ПО = request.form['ссылка_на_сайт_ПО']
        вендор = request.form['вендор']
        стоимость_за_единицу = request.form['стоимость_за_единицу']
        признак_ПО = request.form['признак_ПО']
        тип_ПО = request.form['тип_ПО']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_ПО
                    SET
                    наименование_ПО=%s,
                    описание_ПО=%s,
                    ссылка_на_сайт_ПО=%s,
                    вендор=%s,
                    стоимость_за_единицу=%s,
                    признак_ПО=%s,
                    тип_ПО=%s
                    WHERE код_ПО=%s
                    """, (наименование_ПО, описание_ПО, ссылка_на_сайт_ПО, вендор, стоимость_за_единицу, признак_ПО, тип_ПО, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('software_list'))
    
@app.route('/delete_software/<string:id>', methods=['POST', 'GET'])
def delete_software(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_ПО WHERE код_ПО = {0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('software_list'))

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
    sh_software.write(0, 7, 'Тип ПО')
    idx = 0 
    for row in res_software:
        sh_software.write(idx+1, 0, str(row['код_ПО']))
        sh_software.write(idx+1, 1, row['наименование_ПО'])
        sh_software.write(idx+1, 2, row['описание_ПО'])
        sh_software.write(idx+1, 3, row['ссылка_на_сайт_ПО'])
        sh_software.write(idx+1, 4, row['вендор'])
        sh_software.write(idx+1, 5, row['стоимость_за_единицу'])
        sh_software.write(idx+1, 6, row['признак_ПО'])
        sh_software.write(idx+1, 7, row['тип_ПО'])
        idx += 1
    workbook_software.save(output_software)
    output_software.seek(0)
    return Response(output_software, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=software_report.xls"})

@app.route('/vendor')
def vendor_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_производителей_ПО'
        cur.execute(string)
        list_vendor = cur.fetchall()
        return render_template('vendor.html', list_vendor=list_vendor)
    return redirect(url_for('login'))

@app.route('/add_vendor', methods=['POST'])
def add_vendor():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_производителя = request.form['код_производителя']
        производитель = request.form['производитель']
        описание_производителя = request.form['описание_производителя']
        ссылка_на_сайт_производителя = request.form['ссылка_на_сайт_производителя']
        cur.execute('INSERT INTO Справочник_производителей_ПО (код_производителя, производитель, описание_производителя, ссылка_на_сайт_производителя) VALUES(%s,%s,%s,%s)', (код_производителя, производитель, описание_производителя, ссылка_на_сайт_производителя))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('vendor_list'))

@app.route('/edit_vendor/<id>', methods=['POST', 'GET'])
def edit_vendor(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_производителей_ПО WHERE код_производителя=%s', (id))
    vendors = cur.fetchall()
    cur.close()
    print(vendors[0])
    return render_template('edit_vendor.html', vendor = vendors[0])

@app.route('/update_vendor/<id>', methods=['POST'])
def update_vendor(id):
    if request.method == 'POST':
        производитель = request.form['производитель']
        описание_производителя = request.form['описание_производителя']
        ссылка_на_сайт_производителя = request.form['ссылка_на_сайт_производителя']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_производителей_ПО
                    SET
                    производитель=%s,
                    описание_производителя=%s,
                    ссылка_на_сайт_производителя=%s
                    WHERE код_производителя=%s
                    """, (производитель, описание_производителя, ссылка_на_сайт_производителя, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('vendor_list'))

@app.route('/delete_vendor/<string:id>', methods=['POST', 'GET'])
def delete_vendor(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_производителей_ПО WHERE код_производителя={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('vendor_list'))

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
    idx = 0
    for row in result_vendor:
        sh_vendor.write(idx+1, 0, str(row['код_производителя']))
        sh_vendor.write(idx+1, 1, row['производитель'])
        sh_vendor.write(idx+1, 2, row['описание_производителя'])
        sh_vendor.write(idx+1, 3, row['ссылка_на_сайт_производителя'])
        idx += 1
    workbook_vendor.save(output_vendor)
    output_vendor.seek(0)
    return Response(output_vendor, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=vendor_report.xls"})

@app.route('/customer')
def customer_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_заказчиков_ПО'
        cur.execute(string)
        list_customer = cur.fetchall()
        return render_template('customer.html', list_customer=list_customer)
    return redirect(url_for('login'))

@app.route('/add_customer', methods=['POST'])
def add_customer():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_заказчика = request.form['код_заказчика']
        заказчик_ПО = request.form['заказчик_ПО']
        описание_заказчика = request.form['описание_заказчика']
        ссылка_на_сайт_заказчика = request.form['ссылка_на_сайт_заказчика']
        cur.execute('INSERT INTO Справочник_заказчиков_ПО (код_заказчика, заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика) VALUES(%s,%s,%s,%s)', (код_заказчика, заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('customer_list'))
    

@app.route('/edit_customer/<id>', methods=['POST','GET'])
def edit_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_заказчиков_ПО WHERE код_заказчика=%s', (id))
    customers = cur.fetchall()
    cur.close()
    print(customers[0])
    return render_template('edit_customer.html', customer=customers[0])

@app.route('/update_customer/<id>', methods=['POST'])
def update_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        заказчик_ПО = request.form['заказчик_ПО']
        описание_заказчика = request.form['описание_заказчика']
        ссылка_на_сайт_заказчика = request.form['ссылка_на_сайт_заказчика']
        cur.execute(""" UPDATE Справочник_заказчиков_ПО
                    SET
                    заказчик_ПО=%s,
                    описание_заказчика=%s,
                    ссылка_на_сайт_заказчика=%s
                    WHERE код_заказчика=%s
                    """, (заказчик_ПО, описание_заказчика, ссылка_на_сайт_заказчика, id))
        flash("Запись успешно обновлена!")
        conn2.commit()
        return redirect(url_for('customer_list'))
    
@app.route('/delete_customer/<string:id>', methods=['POST', 'GET'])
def delete_customer(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_заказчиков_ПО WHERE код_заказчика={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('customer_list'))

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
    idx = 0
    for row in result_customer:
        sh_customer.write(idx+1, 0, str(row['код_заказчика']))
        sh_customer.write(idx+1, 1, row['заказчик_ПО'])
        sh_customer.write(idx+1, 2, row['описание_заказчика'])
        sh_customer.write(idx+1, 3, row['ссылка_на_сайт_заказчика'])
        idx += 1
    workbook_customer.save(output_customer)
    output_customer.seek(0)
    return Response(output_customer, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=customer_report.xls"})

@app.route('/licence')
def licence_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string='SELECT * FROM Справочник_лицензий'
        cur.execute(string)
        list_licence = cur.fetchall()
        return render_template('licence.html', list_licence=list_licence)
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
        cur.execute('INSERT INTO Справочник_лицензий (код_лицензии, наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии) VALUES(%s,%s,%s,%s,%s)', (код_лицензии, наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('licence_list'))
    
@app.route('/edit_licence/<id>', methods=['POST', 'GET'])
def edit_licence(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Справочник_лицензий WHERE код_лицензии=%s', (id))
    lic = cur.fetchall()
    print(lic[0])
    return render_template('edit_licence.html', lice = lic[0])

@app.route('/update_licence/<id>', methods=['POST'])
def update_licence_list(id):
    if request.method == 'POST':
        наименование_лицензии = request.form['наименование_лицензии']
        тип_лицензии = request.form['тип_лицензии']
        счёт_списания = request.form['счёт_списания']
        версия_лицензии = request.form['версия_лицензии']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Справочник_лицензий
                    SET наименование_лицензии=%s,
                    тип_лицензии=%s,
                    счёт_списания=%s,
                    версия_лицензии=%s
                    WHERE код_лицензии=%s
                    """, (наименование_лицензии, тип_лицензии, счёт_списания, версия_лицензии, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('licence_list'))
    
@app.route('/delete_licence/<string:id>', methods=['POST', 'GET'])
def delete_licence_from_list(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Справочник_лицензий WHERE код_лицензии={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('licence_list'))

@app.route('/partners_list')
def partners_list():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        string = "SELECT * FROM Контрагенты"
        cur.execute(string)
        partner_list = cur.fetchall()
        return render_template('partner.html', partner_list=partner_list)
    return redirect(url_for('login'))

@app.route('/add_partner', methods=['POST'])
def add_partner():
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        код_контрагента = request.form['код_контрагента']
        наименование_контрагента = request.form['наименование_контрагента']
        договор = request.form['договор']
        cur.execute('INSERT INTO Контрагенты (код_контрагента, наименование_контрагента, договор) VALUES(%s,%s,%s)', (код_контрагента, наименование_контрагента, договор))
        conn2.commit()
        flash('Запись успешно создана!')
        return redirect(url_for('partners_list'))
    
@app.route('/edit_partner/<id>', methods=['POST', 'GET'])
def edit_partner(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM Контрагенты WHERE код_контрагента=%s', (id))
    partners = cur.fetchall()
    print(partners[0])
    return render_template('edit_partner.html', partner = partners[0])

@app.route('/update_partner/<id>', methods=['POST'])
def update_partner(id):
    if request.method == 'POST':
        наименование_контрагента = request.form['наименование_контрагента']
        договор = request.form['договор']
        cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(""" UPDATE Контрагенты
                    SET наименование_контрагента=%s,
                    договор=%s
                    WHERE код_контрагента=%s
                    """, (наименование_контрагента, договор, id))
        flash('Запись успешно обновлена!')
        conn2.commit()
        return redirect(url_for('partners_list'))
    
@app.route('/delete_partner/<string:id>', methods=['POST', 'GET'])
def delete_partner(id):
    cur = conn2.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('DELETE FROM Контрагенты WHERE код_контрагента={0}'.format(id))
    conn2.commit()
    flash('Запись успешно удалена!')
    return redirect(url_for('partners_list'))

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
    idx = 0
    for row in result_partner:
        sh_partner.write(idx+1, 0, str(row['код_контрагента']))
        sh_partner.write(idx+1, 1, row['наименование_контрагента'])
        sh_partner.write(idx+1, 2, row['договор'])
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
    idx = 0  
    for row in result_licence:
        sh_licence.write(idx+1, 0, str(row['код_лицензии']))
        sh_licence.write(idx+1, 1, row['наименование_лицензии'])
        sh_licence.write(idx+1, 2, row['тип_лицензии'])
        sh_licence.write(idx+1, 3, row['счёт_списания'])
        sh_licence.write(idx+1, 4, row['версия_лицензии'])
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
    sh.write(0, 5, 'Срок полезного использования (мес)')
    sh.write(0, 6, 'Стоимость за единицу')
    sh.write(0, 7, 'Итоговая стоимость')
    sh.write(0, 8, 'Заказчик ПО')
    sh.write(0, 9, 'Признак ПО')
    sh.write(0, 10, 'Количество ПО')
    sh.write(0, 11, 'Срок действия лицензии')
    sh.write(0, 12, 'Тип ПО')
    idx = 0
    for row in result:
        sh.write(idx+1, 0, str(row['номер_пп']))
        sh.write(idx+1, 1, row['наименование_ПО'])
        sh.write(idx+1, 2, row['вендор'])
        sh.write(idx+1, 3, row['начало_действия_лицензии'])
        sh.write(idx+1, 4, row['окончание_действия_лицензии'])
        sh.write(idx+1, 5, row['срок_полезного_использования_мес'])
        sh.write(idx+1, 6, row['стоимость_за_единицу'])
        sh.write(idx+1, 7, row['итоговая_стоимость'])
        sh.write(idx+1, 8, row['заказчик_ПО'])
        sh.write(idx+1, 9, row['признак_ПО'])
        sh.write(idx+1, 10, row['количество_ПО'])
        sh.write(idx+1, 11, row['срок_действия_лицензии'])
        sh.write(idx+1, 12, row['тип_ПО'])
        idx += 1
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=total_report.xls"})


@app.route('/user_change_password', methods = ['POST', 'GET'])
def user_change_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        email = request.form.get('email')
        cur.execute('SELECT * FROM users WHERE email=%s', (email,))
        account = cur.fetchone()
        if request.method == 'POST':
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            if not email or not old_password or not new_password:
                flash('Пожалуйста, заполните форму!')
            else:
                if account:
                    if email == account['email']:
                        if not check_password_hash(account['password'], old_password):
                            flash('Неверный старый пароль!')
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
                    flash('Введен некорректный адрес электронной почты!')
                    return redirect(url_for('usser_change_password'))
                
        return render_template('change_password.html', title="Поменять пароль")

@app.route('/user_change_email', methods=['POST', 'GET'])
def user_change_email():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if not 'loggedin' in session:
        return redirect(url_for('login'))
    else:
        old_email = request.form.get('old_email')
        cur.execute('SELECT * FROM users WHERE email=%s', (old_email,))
        account = cur.fetchone()
        if request.method == 'POST':
            new_email = request.form.get('new_email')
            if not old_email or not new_email:
                flash("Пожалуйста, заполните форму!")
            else:
                if account:
                    if new_email == old_email:
                        flash('Новый адрес электронной почты совпадает с предыдущим!')
                        return redirect(url_for('user_change_email'))
                    id = account['id']
                    cur.execute("""UPDATE users
                                SET email=%s
                                WHERE id=%s""", (new_email, id))
                    flash('Запись успешно обновлена!')
                    conn.commit()
                    return redirect(url_for('profile'))
                else:
                    flash('Введен некорректный алдрес электронной почты!')
                    return redirect(url_for('user_change_email'))
        return render_template('change_email.html', title='Поменять адрес электронной почты')
    
@app.route('/reset_password', methods = ['POST', 'GET'])
def reset_password():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        email = request.form.get('email')
        cur.execute('SELECT * FROM users WHERE email=%s', (email,))
        user = cur.fetchone()
        if not user:
            flash('Неправильный адрес электронной почты! Пожалуйста, попробуйте еще раз.')
            return render_template('reset_password.html')
        id = user['id']
        new_password = request.form.get('new_password')
        _hashed_password = generate_password_hash(new_password)
        cur.execute("""UPDATE users
                    SET password=%s
                    WHERE id=%s""", (_hashed_password, id))
        flash('Пароль успешно обновлен!')
        conn.commit()
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Пользователь забыл пароль')
        
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
