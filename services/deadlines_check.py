from bot_create import bot
from database.base import user_collection
from database.tasks import get_tasks_with_deadline, get_tasks_with_deadline_week
from inlines.schedule_inlines import get_scheduled_tasks_inline
from services.tasks import put_together_message, shorter_tasks
from services.users import get_users_from_groups


async def is_deadline(mode: int):
    if mode == 1:
        tasks = await get_tasks_with_deadline()
        start_message = 'Скоро дедлайн у следующих заданий:\n'
    else:
        tasks = await get_tasks_with_deadline_week()
        start_message = 'На следующей неделе дедлайн у заданий:\n'
    groups = list(tasks.keys())
    users = await get_users_from_groups(groups)
    count = 0
    print(users)
    for key, value in tasks.items():
        inline_buttons = await get_scheduled_tasks_inline(value)
        value1 = users[key]
        for v in value1:
            user = await user_collection.find_one({'chat_id': v})
            val = await shorter_tasks(value.copy())
            message = await put_together_message(val, f'Здравствуйте, {user["full_name"]}.\n' + start_message)
            await bot.send_message(chat_id=v, text=message, reply_markup=inline_buttons)
            count += 1
    return count

