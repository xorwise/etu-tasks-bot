import motor.motor_asyncio
from core.config import DATABASE_URL

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)

database = client.bot

user_collection = database.get_collection('users')
group_collection = database.get_collection('groups')
task_collection = database.get_collection('tasks')
