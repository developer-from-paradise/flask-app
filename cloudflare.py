import requests, json


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
            print(response.text)
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


    def BindDomain(self, zone_id, domain, server_domain):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'

        data = {
            'type': 'A',
            'name': domain,
            'content': server_domain,
            'proxied': True
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False
        

    def CountryFirewall(self, zone_id, countries):
        formatted_countries = ' '.join([f'"{country}"' for country in countries])
        expression = f"(not ip.geoip.country in {{{formatted_countries}}})"

        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
        response = requests.get(url, headers=self.headers)
        res = json.loads(response.text)
        ruleset_id = res['result'][4]['id']


        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{ruleset_id}/rules'

        data = {
            "action": "block",
            "description": "Allow only countries",
            "enabled": True,
            "expression": expression,
        }

        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False



    def SetUnderAttack(self, zone_id):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level'
        
        data = {
            "value": "under_attack"
        }

        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False