from .base import group_collection
from services.groups import get_subject_list


async def add_group(data: dict) -> bool:
    try:
        data['subjects'] = await get_subject_list(data['id'])
    except KeyError:
        print(data['id'])
        return False
    await group_collection.insert_one(data)
    return True


async def get_group(id: int) -> dict:
    return await group_collection.find_one({'id': id})


async def update_group(id: int, data: dict) -> bool:
    await group_collection.update_one({'id': id}, {'$set': data})
    return True


async def delete_group(id: int) -> bool:
    await group_collection.delete_one({'id': id})
    return True
