import time
import os
from PIL import Image
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import shutil
import pandas as pd

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nПришли мне фотографию полок в магазине!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Когда пришлешь фото, я скажу, сколько на ней полок!")

@dp.message_handler(content_types=['photo'])
async def process_photo_command(message: types.Message):
    file_path = f"""{time.strftime("%Y%m%d%H%M%S")}ID{message.from_user.id}.jpg"""
    
    await message.photo[-1].download(file_path)
    await message.reply("Подождите 5 секунд...")

    os.system(f"python /content/gdrive/MyDrive/TheCodingBug/yolov7/detect.py --weights best.pt --conf 0.5 --img-size 640 --source {file_path} --save-txt --classes 1 0 ")
    await bot.send_photo(message.chat.id, open(f"/content/gdrive/MyDrive/TheCodingBug/runs/detect/exp/{file_path}", 'rb'))

    os.rename(f"/content/gdrive/MyDrive/TheCodingBug/runs/detect/exp/labels/{file_path.replace('jpg', 'txt')}",
                f"/content/gdrive/MyDrive/TheCodingBug/runs/detect/exp/labels/{file_path.replace('txt', 'csv')}")
    df = pd.read_csv(f"/content/gdrive/MyDrive/TheCodingBug/runs/detect/exp/labels/{file_path}", delimiter=' ', names=['class', 'x', 'y', 'w', 'h'])
    first_class = 0
    second_class = 1

    first_n = df[df['class'] == first_class]
    second_n = df[df['class'] == second_class]

    await bot.send_message(message.chat.id, f"Without discount: {len(first_n)}, with discount: {len(second_n)}")

    arr = df.to_numpy()
    arr = arr[arr[:, 2].argsort()]

    shelfs = []
    k = 0

    shelfs.append(arr[0][2])
    k += 1

    for i in range(len(arr) - 1):
        if (arr[i+1][2] - arr[i][2] > 0.1):
            shelfs.append(arr[i + 1][2])
            k += 1

    await bot.send_message(message.chat.id, f"Coordinates of shelfs: {shelfs}, count of shelfs: {k}")

    shutil.rmtree('/content/gdrive/MyDrive/TheCodingBug/runs')   
    os.remove(file_path)

if __name__ == '__main__':
    executor.start_polling(dp)

