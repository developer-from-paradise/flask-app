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
            return response.text
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


    def BindDomain(self, zone_id, domain, server_ip):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'

        data = {
            'type': 'A',
            'name': domain,
            'content': server_ip,
            'proxied': True
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            return True
        else:
            data = json.loads(response.text)
            if data['errors'][0]['code'] == 81057:
                return True
            print(response.text)
            return False
        

    def CountryFirewall(self, zone_id, countries):
        formatted_countries = ' '.join([f'"{country}"' for country in countries])
        expression = f"(not ip.geoip.country in {{{formatted_countries}}})"

        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
        response = requests.get(url, headers=self.headers)
        res = json.loads(response.text)
        for data in res['result']:
            if data['phase'] == 'http_request_firewall_custom':
                ruleset_id = data['id']


        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{ruleset_id}/rules'

        data = {
            "action": "block",
            "description": "Allow only countries",
            "enabled": True,
            "expression": expression
        }

        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False


    
    def SetSecurityLevel(self, zone_id, mode):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level'
        
        data = {
            "value": mode
        }

        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False



    def ListOfFireWalls(self, zone_id):
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/rules"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        else:
            print(response.text)
            return False



    def UpdateFilter(self, zone_id, countries):
        filter_id = self.ListOfFireWalls(zone_id)['result'][0]['filter']['id']

        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/filters/{filter_id}"

        formatted_countries = ' '.join([f'"{country}"' for country in countries])

        expression = f"(not ip.geoip.country in {{{formatted_countries}}})"
        
        data = {
            "expression": expression
        }

        response = requests.put(url, headers=self.headers, json=data)

        if response.status_code == 200:
            return True
        else:
            print(response.text)
            return False