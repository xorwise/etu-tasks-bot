from services.deadlines_check import is_deadline
from time import sleep
import asyncio
from datetime import datetime
import nest_asyncio


async def schedule_check():
    while True:
        try:
            if datetime.now().strftime('%H:%M') == '20:00':
                count = await is_deadline(mode=1)
                print(f'{count} messages were sent to students...')
            if datetime.now().weekday() == 5 and datetime.now().strftime('%H:%M') == '13:15':
                count = await is_deadline(mode=2)
                print(f'{count} messages were sent to students...')
        except:
            print(f'Error at {datetime.now().strftime("%H:%M")}')
        finally:
            sleep(60)

nest_asyncio.apply()
asyncio.run(schedule_check())



