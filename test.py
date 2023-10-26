from db import User
from bot import Bot

db = User('./users.db', 'users')

username = 'jojo'

data = db.GetBotData(username)
chat_id = data[0][0]
bot_token = data[0][1]
bot = Bot(chat_id, bot_token)
domain = 'depian.online'
phone = '+843984934'

print(chat_id)
print(bot_token)


d = bot.sendMessage(f"""
<b>Домен: </b>{domain}
<b>Номер: </b><code>{phone}</code>
<b>Ошибка: </b><code>Смените api id и api hash</code>
""")


print(d[1])