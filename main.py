from create_bot import dp
from aiogram.utils import executor
from handlers import client, admin
from flask_bot import app
import asyncio


admin.register_handlers_admin(dp)
client.register_handlers_client(dp)


async def on_startup(x):
    print("Bot are working")
    asyncio.create_task(asyncio.to_thread(app.run))


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
