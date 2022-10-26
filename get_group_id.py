import json
import requests


url = 'https://digital.etu.ru/api/general/dicts/groups?scheduleId=publicated'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 
           "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate"}

request = requests.get(url, headers=headers)

response = request.json()

groups = dict()
for group in response:
    pass
    groups[group['fullNumber']] = group['id']

with open('groups.json', 'w') as f:
    json.dump(groups, f)

