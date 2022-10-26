from database.base import group_collection


async def name_validation(name: str) -> bool:
    full_name = name.split()
    if len(full_name) in [2, 3]:
        b = True
        for part in full_name:
            if (ord(part[0]) < 65 or ord(part[0]) > 90) and (ord(part[0]) < 1040 or ord(part[0]) > 1071):
                b = False
                break
        return b
    return False

async def group_validation(group: str) -> bool:
    try:
        if 1000 <= int(group) <= 9999:
            return True
        else:
            return False
    except:
        return False

async def is_sender_validation(response: str) -> bool:
    if response in ['Да', 'Нет']:
        return True
    return False


async def get_users_from_groups(groups: list) -> dict:
    print(groups)
    users = dict()
    for group in groups:
        new_group = await group_collection.find_one({'id': group})
        users[group] = new_group['students']
    return users
