from .base import user_collection


async def add_user(data: dict) -> bool:
    await user_collection.insert_one(data)
    return True


async def get_user(user_id: int) -> dict:
    return await user_collection.find_one({'user_id': user_id})


async def update_user(user_id: int, data: dict) -> bool:
    await user_collection.update_one({'user_id': user_id}, {'$set': data})
    return True


async def delete_user(user_id: int) -> bool:
    await user_collection.delete_one({'user_id': user_id})
    return True



