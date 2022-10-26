from aiogram import executor
from bot_create import dp
from message_handlers import users, tasks, other



if __name__ == '__main__':
    users.users_handlers_register(dp)
    tasks.tasks_handlers_register(dp)
    other.other_handlers_register(dp)
    executor.start_polling(dp, skip_updates=True)
