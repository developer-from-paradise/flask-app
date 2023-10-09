import os

path = 'sex'
host = 'depian.online'
domains = os.listdir(f'templates/domains/')
for domain in domains:
    if host in domain:
        print(domain)