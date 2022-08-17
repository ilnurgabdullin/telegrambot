from create_bot import dp
from aiogram.utils import executor
from handlers import client, admin


admin.register_handlers_admin(dp)
client.register_handlers_client(dp)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
