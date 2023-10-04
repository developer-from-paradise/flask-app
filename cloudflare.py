import requests



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
            return False
        
    def GetAccount(self):
        url = 'https://api.cloudflare.com/client/v4/accounts'

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return False



    def RemoveDomain(self, zone_id):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}'

        response = requests.delete(url, headers=self.headers)

        if response.status_code == 200:
            return True
        else:
            return False




if __name__ == '__main__':
    account_id = 'b780405629df43cca324250bc5d3e4c0'
    api_key = '94a6d32b704a6b5aacf2c138087078ffbc41f'
    email = 'kamazzcha@gmail.com'
    
    cl = CloudFlare(email, api_key, account_id)