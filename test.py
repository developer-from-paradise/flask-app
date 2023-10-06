from config import clf


domain = 'depian.online'

zones = clf.getDomains()

for domain in zones:
    if zones['domain'] == domain:
        clf.BindDomain()