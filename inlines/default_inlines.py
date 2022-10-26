from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.groups import get_group
from datetime import datetime


async def default_inline(user):
    if user['is_sender']:
        button1 = InlineKeyboardButton('Создать задание✅', callback_data='/create_task')
        button2 = InlineKeyboardButton('Показать задания📋', callback_data='/show_tasks')
        button3 = InlineKeyboardButton('Показать профиль👨', callback_data='/get_profile')
        inline_buttons = InlineKeyboardMarkup(row_width=2)
        inline_buttons.row(button1, button2).add(button3)
    else:
        button2 = InlineKeyboardButton('Показать задания📋', callback_data='/show_tasks')
        button3 = InlineKeyboardButton('Показать профиль👨', callback_data='/get_profile')
        inline_buttons = InlineKeyboardMarkup(row_width=2)
        inline_buttons.add(button2).add(button3)
    return inline_buttons


async def subject_inline(group):
    group = await get_group(group)
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    for i in range(1, len(group['subjects']), 2):
        button1 = InlineKeyboardButton(group['subjects'][i - 1], callback_data=group['subjects'][i - 1])
        button2 = InlineKeyboardButton(group['subjects'][i], callback_data=group['subjects'][i])
        inline_buttons.row(button1, button2)

    return inline_buttons


async def choose_subject_inline(group):
    group = await get_group(group)
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    for i in range(1, len(group['subjects']), 2):
        button1 = InlineKeyboardButton(group['subjects'][i - 1], callback_data=f"{group['subjects'][i - 1]}?offset=0")
        button2 = InlineKeyboardButton(group['subjects'][i], callback_data=f"{group['subjects'][i]}?offset=0")
        inline_buttons.row(button1, button2)

    return inline_buttons


async def change_options(id):
    button1 = InlineKeyboardButton('Описание', callback_data=f'/update_description?id={id}')
    button2 = InlineKeyboardButton('Изображения', callback_data=f'/update_photos?id={id}')
    button3 = InlineKeyboardButton('Дедлайн', callback_data=f'/update_deadline?id={id}')
    button4 = InlineKeyboardButton('Завершить', callback_data=f'/finish?id={id}')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2).row(button3, button4)
    return inline_buttons


async def show_filter(user):
    button1 = InlineKeyboardButton('По предмету', callback_data='/show_by_subject')
    button2 = InlineKeyboardButton('По дедлайну', callback_data='/show_by_deadline')
    button3 = InlineKeyboardButton('Показать все задания', callback_data='/show_by_group?offset=0')
    inline_buttons = InlineKeyboardMarkup(row_width=2).row(button1, button2).add(button3)
    if user['is_sender']:
        inline_buttons.add(InlineKeyboardButton('Показать свои задания', callback_data='/show_by_user?offset=0'))
    inline_buttons.add(InlineKeyboardButton('Показать завершенные задания', callback_data='/show_by_timeout?offset=0'))
    inline_buttons.add(InlineKeyboardButton('Меню', callback_data='/menu'))
    return inline_buttons


async def get_tasks_inline(length, tasks: list, offset: int, parameter: str) -> InlineKeyboardMarkup:
    weekdays = {
        '0': 'Пн.',
        '1': 'Вт.',
        '2': 'Ср.',
        '3': 'Чт.',
        '4': 'Пт.',
        '5': 'Сб.',
        '6': 'Вс.'
    }
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(tasks), 2):
        button1 = InlineKeyboardButton(
            f'{i + 1}) {tasks[i]["subject"]} {str(datetime.strptime(tasks[i]["deadline"], "%d.%m.%Y").strftime("%d.%m"))} {weekdays.get(str(datetime.strptime(tasks[i]["deadline"], "%d.%m.%Y").weekday()))}',
            callback_data=f'/get_task?id={tasks[i]["id"]}')
        if i == len(tasks) - 1:
            inline_buttons.add(button1)
        else:
            button2 = InlineKeyboardButton(
                f'{i + 2}) {tasks[i + 1]["subject"]} {str(datetime.strptime(tasks[i + 1]["deadline"], "%d.%m.%Y").strftime("%d.%m"))} {weekdays.get(str(datetime.strptime(tasks[i + 1]["deadline"], "%d.%m.%Y").weekday()))}',
                callback_data=f'/get_task?id={tasks[i + 1]["id"]}')
            inline_buttons.row(button1, button2)
    if offset > 0:
        inline_buttons.add(InlineKeyboardButton('Назад', callback_data=f'{parameter}?offset={offset - 1}'))
    if length > 6 * offset + 6:
        inline_buttons.insert(InlineKeyboardButton('Вперёд', callback_data=f'{parameter}?offset={offset + 1}'))
    inline_buttons.add(InlineKeyboardButton('Меню', callback_data='/menu'))
    return inline_buttons


async def choose_deadline_inline(deadlines: list) -> InlineKeyboardMarkup:
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    weekdays = {
        '0': 'Пн.',
        '1': 'Вт.',
        '2': 'Ср.',
        '3': 'Чт.',
        '4': 'Пт.',
        '5': 'Сб.',
        '6': 'Вс.'
    }
    for i in range(len(deadlines)):
        d = '.'.join(deadlines[i].split("-")[::-1])
        if i % 2 == 0:
            inline_buttons.add(
                InlineKeyboardButton(f'{i + 1}) {d} {weekdays[str(datetime.strptime(d, "%d.%m.%Y").weekday())]}',
                                     callback_data=f'{deadlines[i]}?offset=0'))
        else:
            inline_buttons.insert(
                InlineKeyboardButton(f'{i + 1}) {d} {weekdays[str(datetime.strptime(d, "%d.%m.%Y").weekday())]}',
                                     callback_data=f'{deadlines[i]}?offset=0'))
    return inline_buttons


async def cancel_inline():
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    button = InlineKeyboardButton('Отмена', callback_data='/cancel')
    inline_buttons.add(button)
    return inline_buttons


async def task_options(id, task, user):
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Изменить задание', callback_data=f'/update_task?id={id}')
    inline_buttons.add(button1)
    if user == task['sender']:
        button2 = InlineKeyboardButton('Удалить задание', callback_data=f'/remove_task?id={id}')
        inline_buttons.insert(button2)
    if task['is_solvable']:
        button3 = InlineKeyboardButton('Посмотреть решения', callback_data=f'/get_solutions?id={id}')
        button4 = InlineKeyboardButton('Добавить решение', callback_data=f'/add_solution?id={id}')
        inline_buttons.row(button3, button4)
    inline_buttons.add(InlineKeyboardButton('Меню', callback_data='/menu'))
    return inline_buttons


async def get_solution_inline(task):
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton('Посмотреть решения', callback_data=f'/get_solutions?id={task}')
    button3 = InlineKeyboardButton('Посмотреть задание', callback_data=f'/get_task?id={task}')
    button4 = InlineKeyboardButton('Меню', callback_data='/menu')
    inline_buttons.row(button1).add(button3).add(button4)
    return inline_buttons


async def solutions_options(task, user):
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    for i in range(len(task['solution'])):
        if i % 2 == 0:
            inline_buttons.add(InlineKeyboardButton(f'{i + 1}) {user["full_name"].split()[0]} {user["full_name"].split()[1]}.',
                                                    callback_data=f'/get_solution?id={task["_id"]}?number={i}'))
        else:
            inline_buttons.insert(InlineKeyboardButton(f'{i + 1}) {user["full_name"].split()[0]} {user["full_name"].split()[1]}.',
                                                       callback_data=f'/get_solution?id={task["_id"]}?number={i}'))
    inline_buttons.add(InlineKeyboardButton('Посмотреть задание', callback_data=f'/get_task?id={task["_id"]}')).insert(InlineKeyboardButton('Меню', callback_data='/menu'))
    return inline_buttons


async def solution_options(task, user, number):
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    if user['user_id'] == task['solution'][number]['sender']:
        inline_buttons.add(InlineKeyboardButton('Изменить решение', callback_data=f'/update_solution?id={task["_id"]}?number={number}'))
        inline_buttons.insert(InlineKeyboardButton('Удалить решение',
                                                callback_data=f'/remove_solution?id={task["_id"]}?number={number}'))
    inline_buttons.add(InlineKeyboardButton('Посмотреть задание', callback_data=f'/get_task?id={task["_id"]}'))
    inline_buttons.add(InlineKeyboardButton('Посмотреть другие решения', callback_data=f'/get_solutions?id={task["_id"]}'))
    inline_buttons.add(InlineKeyboardButton('Меню', callback_data='/menu'))
    return inline_buttons


async def update_solution_options(task, number):
    inline_buttons = InlineKeyboardMarkup(row_width=2)
    inline_buttons.add(InlineKeyboardButton('Описание', callback_data=f'/update_sol_description?id={task}?number={number}'))
    inline_buttons.insert(InlineKeyboardButton('Изображения', callback_data=f'/update_sol_photos?id={task}?number={number}'))
    inline_buttons.add(InlineKeyboardButton('Завершить', callback_data=f'/get_solution?id={task}?number={number}'))
    return inline_buttons
