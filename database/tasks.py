from services.tasks import filter_tasks, shorter_tasks, filter_deadlines, filter_finished_tasks
from .base import task_collection
from bson.objectid import ObjectId
from datetime import datetime, timedelta


async def add_task(data: dict) -> str:
    _id = await task_collection.insert_one(data)
    return _id.inserted_id


async def get_task(id: str) -> dict:
    task = await task_collection.find_one({'_id': ObjectId(id)})
    if task is None:
        raise KeyError
    return task


async def get_tasks_by_subject(subject: str, group: int) -> list:
    tasks = [task async for task in task_collection.find({'subject': subject, 'group': group})]
    tasks.sort(key=lambda task: datetime.strptime(task['deadline'], '%Y-%m-%d'))
    filtered_tasks = await filter_tasks(tasks)
    return await shorter_tasks(filtered_tasks)


async def get_available_deadlines(group: int) -> list:
    deadlines = [task['deadline'] async for task in task_collection.find({'group': group})]
    deadlines = list(set(deadlines))
    deadlines.sort(key=lambda deadline: datetime.strptime(deadline, '%Y-%m-%d'))
    filtered_deadlines = await filter_deadlines(deadlines)
    return filtered_deadlines


async def get_tasks_by_deadline(deadline: datetime, group: int) -> list:
    deadline = deadline.strftime('%Y-%m-%d')
    tasks = [task async for task in task_collection.find({'deadline': str(deadline), 'group': group})]
    tasks.sort(key=lambda task: datetime.strptime(task['deadline'], '%Y-%m-%d'))
    filtered_tasks = await filter_tasks(tasks)
    return await shorter_tasks(filtered_tasks)


async def get_all_current_tasks_inline(group: int) -> list:
    tasks = [task async for task in task_collection.find({'group': group})]
    tasks.sort(key=lambda task: datetime.strptime(task['deadline'], '%Y-%m-%d'))
    filtered_tasks = await filter_tasks(tasks)
    return await shorter_tasks(filtered_tasks)


async def get_tasks_by_user(user: int) -> list:
    tasks = [task async for task in task_collection.find({'sender': user})]
    tasks.sort(key=lambda task: datetime.strptime(task['deadline'], '%Y-%m-%d'))
    filtered_tasks = await filter_tasks(tasks)
    return await shorter_tasks(filtered_tasks)


async def get_all_finished_tasks(group: int) -> list:
    tasks = [task async for task in task_collection.find({'group': group})]
    tasks.sort(key=lambda task: datetime.strptime(task['deadline'], '%Y-%m-%d'))
    filtered_tasks = await filter_finished_tasks(tasks)
    return await shorter_tasks(filtered_tasks)


async def patch_task(id: str, data: dict) -> bool:
    await task_collection.update_one({'_id': ObjectId(id)}, {'$set': data})
    return True


async def delete_task(id: str) -> bool:
    await task_collection.delete_one({'_id': ObjectId(id)})
    return True


async def get_tasks_with_deadline() -> dict:
    today = datetime.now()
    tomorrow = today + timedelta(1)
    tomorrow = tomorrow.strftime('%Y-%m-%d')
    tasks = [task async for task in task_collection.find({'deadline': tomorrow})]
    print(tasks)
    new_tasks = dict()
    for task in tasks:
        try:
            new_tasks[task['group']] += [task]
        except KeyError:
            new_tasks[task['group']] = [task]
    return new_tasks


async def get_tasks_with_deadline_week() -> dict:
    today = datetime.now()
    deadlines = list()
    for delta in range(2, 7):
        day = today + timedelta(delta)
        deadlines.append(day.strftime('%Y-%m-%d'))
    tasks = list()
    for day in deadlines:
        tasks += [task async for task in task_collection.find({'deadline': day})]
    new_tasks = dict()
    for task in tasks:
        try:
            new_tasks[task['group']] += [task]
        except KeyError:
            new_tasks[task['group']] = [task]
    return new_tasks
