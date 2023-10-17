from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, FloodWaitError, SessionPasswordNeededError, PhoneCodeExpiredError

class ClientTG:
    client: TelegramClient
    phone: str

    def __init__(self, API_ID, API_HASH, phone: str = None,):
        self.client = TelegramClient(
            session=f'./sessions/{phone[1:]}.session',
            api_id=API_ID,
            api_hash=API_HASH,
            device_model="Iphone",
            system_version="6.12.0",
            app_version="10 P (28)")