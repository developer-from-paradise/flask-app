from peewee import SqliteDatabase
from hashlib import sha256
from config import salt

print("""
[0] - Добавить админа
[1] - Удалить админа
[2] - Список админов
""")

mode = int(input("Выберите режим: "))


if mode == 0:
    login = input('Логин: ')
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
elif mode == 2:
    try:
        with SqliteDatabase('./users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM admins")
            conn.commit()
            data = cursor.fetchall()
            for da in data:
                print(da)
        print('Успешно!')
    except Exception as e:
        print(e)
        print('Ошибка')
else:
    login = input('Логин: ')
    try:
        with SqliteDatabase('./users.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM admins WHERE username={login}")
            conn.commit()

        print('Успешно!')
    except Exception as e:
        print(e)
        print('Ошибка')