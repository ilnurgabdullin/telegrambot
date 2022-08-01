from aiogram import Bot #, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()


bot = Bot(token = '5347235715:AAEHEFFLyjPoH-WNCJnhVZxJFf1PuJAcrxw')
dp = Dispatcher(bot, storage= storage)



