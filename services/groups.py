import json
import requests

async def get_group_id(group: int) -> int:
    with open('groups.json', 'r') as f: 
        return json.load(f)[f'{group}']

async def get_subject_list(id: int) -> list:
    api_id = await get_group_id(id)

    url = f'https://digital.etu.ru/api/schedule/objects/publicated?groups={api_id}&withSubjectCode=false&withURL=false'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 
           "Upgrade-Insecure-Requests": "1",
           "DNT": "1",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.9, ru;q=0.8",
           "Accept-Encoding": "gzip, deflate, br"}
    request = requests.get(url, headers=headers)
    response = request.json()
    
    subjects = set()
    for i in response[0]['scheduleObjects']:
        subjects.add(i['lesson']['subject']['shortTitle'])
    return list(subjects)
