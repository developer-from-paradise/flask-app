from config import clf


domains = 'depian.online'

zones = clf.getDomains()

for domain in zones:
    if domain['name'] == domains:
        clf.BindDomain(domain['id'], domains, 'https://depian.ru/ismoil')