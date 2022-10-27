from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_scheduled_tasks_inline(tasks: list) -> InlineKeyboardMarkup:
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
            f'{i + 1}) {tasks[i]["subject"]} {str(datetime.strptime(tasks[i]["deadline"], "%Y-%m-%d").strftime("%d.%m"))} {weekdays.get(str(datetime.strptime(tasks[i]["deadline"], "%Y-%m-%d").weekday()))}',
            callback_data=f'/get_task?id={str(tasks[i]["_id"])}')
        if i == len(tasks) - 1:
            inline_buttons.add(button1)
        else:
            button2 = InlineKeyboardButton(
                f'{i + 2}) {tasks[i]["subject"]} {str(datetime.strptime(tasks[i + 1]["deadline"], "%Y-%m-%d").strftime("%d.%m"))} {weekdays.get(str(datetime.strptime(tasks[i + 1]["deadline"], "%Y-%m-%d").weekday()))}',
                callback_data=f'/get_task?id={str(tasks[i + 1]["_id"])}')
            inline_buttons.row(button1, button2)
    inline_buttons.add(InlineKeyboardButton('Меню', callback_data='/menu'))
    return inline_buttons
