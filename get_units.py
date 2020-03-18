from requests_in_rnis import get_token
from requests_in_rnis import get_org_name
from requests_in_rnis import get_orgs_list

RNIS_URL  = 'https://api-rnis.t1-group.ru/ajax/request'
LOGIN = 'NalizkoA'
PASSWORD = 'NalizkoA'

# 1) Получить токен для доступа в РНИС
rnis_token = get_token(LOGIN,PASSWORD,RNIS_URL)
print(rnis_token)

# 2) Получить по uuid предприятия его название и ИНН
org_name = get_org_name('eb9d43f4-5b5c-11e9-9c84-029975ec7d0e',rnis_token,RNIS_URL)
print(org_name[0])
print(org_name[1])
print(org_name[2])

orgs = get_orgs_list(rnis_token,RNIS_URL)
print(orgs)






