import datetime
from aiogram import types
from inlines.default_inlines import cancel_inline
from database.users import get_user


async def shorter_tasks(tasks: list) -> list:
    for i in range(len(tasks)):
        tasks[i] = {
            'id': tasks[i]['_id'],
            'subject': tasks[i]['subject'],
            'description': tasks[i]['description'][:20] + '...' if len(tasks[i]['description']) > 20 else tasks[i]['description'],
            'photos': len(tasks[i]['photos']),
            'files': len(tasks[i]['files']),
            'deadline': '.'.join(tasks[i]['deadline'].split('-')[::-1])
        }
    return tasks


async def filter_tasks(tasks: list) -> list:
    filtered_tasks = []
    for task in tasks:
        if datetime.datetime.strptime(task['deadline'], '%Y-%m-%d') >= datetime.datetime.today():
            filtered_tasks.append(task)
    return filtered_tasks


async def filter_finished_tasks(tasks: list) -> list:
    filtered_tasks = []
    for task in tasks:
        if datetime.datetime.strptime(task['deadline'], '%Y-%m-%d') < datetime.datetime.today():
            filtered_tasks.append(task)
    return filtered_tasks


async def filter_deadlines(deadlines: list) -> list:
    filtered_deadlines = list()
    for deadline in deadlines:
        if datetime.datetime.strptime(deadline, '%Y-%m-%d') >= datetime.datetime.today():
            filtered_deadlines.append(deadline)
    return filtered_deadlines


async def get_tasks_with_offset(tasks: list, offset: int = 0) -> list:
    new_tasks = []
    length = offset * 6 + 6 - len(tasks)
    if length < 0:
        length = 0
    for i in range(offset * 6, offset * 6 + 6 - length):
        new_tasks.append(tasks[i])
    return new_tasks


async def put_together_message(tasks: list, s: str = 'Вот ваши задания:\n') -> str:
    if len(tasks) == 0:
        s = 'Задания не были найдены.'
    for i in range(len(tasks)):
        s += f'{i + 1}) {tasks[i]["subject"]} на {tasks[i]["deadline"]}\nОписание: {tasks[i]["description"]}\nИзображений: {tasks[i]["photos"]}\nФайлов: {tasks[i]["files"]}\n\n'
    return s


async def check_deadline(data: dict, message: types.Message):
    try:
        data['deadline'] = str(datetime.datetime.strptime(message.text, '%d.%m.%Y').date())
    except ValueError:
        try:
            s = message.text + f'.{datetime.date.today().year}'
            data['deadline'] = str(datetime.datetime.strptime(s, '%d.%m.%Y').date())
        except ValueError:
            inline_buttons = await cancel_inline()
            await message.answer('Введите дату в правильном формате: DD.MM.YYYY или DD.MM:',
                                 reply_markup=inline_buttons)
            return False
    return data['deadline']


async def get_solution_message_together(task: dict) -> str:
    s = 'Решений: {}\n'.format(len(task['solution']))
    if len(task['solution']) == 0:
        s = 'Решения не были найдены'
    else:
        for i in range(len(task['solution'])):
            sender = await get_user(task['solution'][i]['sender'])
            s += f'{i + 1}) Решение от {sender["full_name"].split()[0]} {sender["full_name"].split()[1][0]}.\n\n'
    return s


async def get_solution_message(task: dict, number: int) -> str:
    sender = await get_user(task['solution'][number]['sender'])
    s = f'Решение задания от {datetime.datetime.strptime(task["deadline"],"%Y-%m-%d").strftime("%d.%m.%Y")} по предмету {task["subject"]}:\n\n'
    s += f'Описание: {task["solution"][number]["description"]}\n\n'
    s += f'Отправитель: {sender["full_name"]}'
    return s
