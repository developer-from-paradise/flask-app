from peewee import SqliteDatabase
from hashlib import sha256
from config import salt

print("""
[0] - Добавить админа
[1] - Удалить админа
""")

mode = int(input("Выберите режим: "))
login = input('Логин: ')

if mode == 0:
    password = salt + input('Пароль: ')
    password = sha256(password.encode('utf-8')).hexdigest()
    try:
        with SqliteDatabase('./users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO admins(`username`, `password_hash`) VALUES('{login}', '{password}')")
            conn.commit()

        print('Успешно!')
    except Exception as e:
        print(e)
        print('Ошибка')
else:
    try:
        with SqliteDatabase('./users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM admins WHERE username={login}")
            conn.commit()

        print('Успешно!')
    except Exception as e:
        print(e)
        print('Ошибка')