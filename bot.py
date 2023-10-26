from requests import post


class Bot:

    def __init__(self, chat_id, bot_token):
        self.chat_id = chat_id
        self.bot_token = bot_token


    def sendMessage(self, text):
        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = post(url, data=data)
        if response.status_code == 200:
            return True
        else:
            return False, response.text