import requests
from config import *


class CloudFlare:
    def __init__(self, email, api_key, account_id):
        self.headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_key,
            'Content-Type': 'application/json'
        }

        self.account_id = account_id
        


    def getDomains(self):
        url = 'https://api.cloudflare.com/client/v4/zones'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            zones = response.json()['result']
            return zones
        else:
            print(response.text)
            return False
    

    def AddDomain(self, domain):
        url = f'https://api.cloudflare.com/client/v4/zones'
        data = {
            'name': domain,
            'account': {
                'id': self.account_id
            },
            'name': domain,
            'type': "full"
        }

        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False
        
    def GetAccount(self):
        url = 'https://api.cloudflare.com/client/v4/accounts'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(response.text)
            return False



    def RemoveDomain(self, zone_id):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}'

        response = requests.delete(url, headers=self.headers)

        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False


    def BindDomain(self, zone_id, domain):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'

        data = {
            'type': 'A',  # Change to 'CNAME' for a CNAME record
            'name': domain,  # Replace with the name of the DNS record (e.g., subdomain.example.com)
            'content': server_domain,
            'proxied': True
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False