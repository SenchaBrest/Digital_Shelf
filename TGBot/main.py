import time
import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from Recognition.crop import crop
from Recognition.db import db

import algo
from config import TOKEN, yoloPath

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nПришли мне фотографию полок в магазине!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Когда пришлешь фото, я дам информацию:\n"
                        "Сколько на ней ценников разных типов\n"
                        "Сколько на фотографии полок, а так же их относительные координаты!")


@dp.message_handler(content_types=['photo'])
async def process_photo_command(message: types.Message):
    file_path = f"""{time.strftime("%Y%m%d%H%M%S")}ID{message.from_user.id}.jpg"""

    await message.photo[-1].download(file_path)
    await message.reply("Подождите...")
    algo.open_image(file_path)

    os.system(
        f"python {yoloPath}detect.py --weights {yoloPath}tags.pt --conf 0.50 --img-size 640 --source {file_path} "
        f"--save-txt --classes 1 0 ")  # ценники
    if not os.path.exists(f"detect_res/tags/labels/{file_path.replace('.jpg', '.txt')}"):
        await bot.send_message(message.chat.id, "Упс. На фотографии нет стеллажа.")
        return
    await bot.send_photo(message.chat.id, open(f"detect_res/tags/{file_path}", 'rb'))

    os.system(
        f"python {yoloPath}detect.py --weights {yoloPath}3.pt {yoloPath}4.pt {yoloPath}5.pt {yoloPath}6.pt --conf 0.80 --img-size 640 --source {file_path} "
        f"--save-txt")  # объекты

    p_to_photo_obj = crop(file_path, f"detect_res/objects/labels/{file_path.replace('.jpg', '.txt')}")
    await bot.send_photo(message.chat.id, open(p_to_photo_obj, 'rb'))

    algo.preparePhoto(labelOfPrices=f"detect_res/tags/labels/{file_path.replace('.jpg', '.txt')}",
                      labelOfProducts=f"res_rec_obj.txt")

    countOfShelves, Shelves = algo.calcShelvesCount()
    algo.fillShelvesByPrices()
    algo.fillShelvesByProducts()
    # algo.removeBackLayout()
    lengths = algo.calcLengthOfLayout()
    tags = algo.calcTagsCount()
    prices = algo.calcPricesCount()

    await bot.send_message(message.chat.id, f"Количество полок: {countOfShelves}.\n")
    await bot.send_message(message.chat.id, f"Общее количество классов: {len(tags)}.\n")

    sendMessage = f"🏷Общее количество ценников:🏷\n"
    for price in prices:
        sendMessage += f"▸ {price}: {prices[price]}\n"
    await bot.send_message(message.chat.id, sendMessage)

    sendMessage = f"📏Длина поклассовой выкладки:📏\n"
    for i in range(len(Shelves)):
        sendMessage += f"{i + 1} полка\n{10 * '—'}\n"
        for length in lengths[i]:
            sendMessage += f"▸ {db[length[0]]} {length[1]} см;\n"
        sendMessage += "\n"
    await bot.send_message(message.chat.id, sendMessage)

    sendMessage = "🛒Общее количество продуктов:🛒\n"
    for tag in tags:
        sendMessage += f"▸ {db[tag]}: {tags[tag]}\n"
    await bot.send_message(message.chat.id, sendMessage)

    algo.findVoids()
    errorsPath = algo.findMistakes()
    await bot.send_photo(message.chat.id, open(errorsPath, 'rb'))

    algo.clear()


if __name__ == '__main__':
    executor.start_polling(dp)
