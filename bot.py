import asyncio
from datetime import datetime
import random
import aioschedule
from environs import Env
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, ForwardedMessageFilter
from config import CHECK_FREQUENCY
from parser import get_posts_data
from database import *


env = Env()
env.read_env(".env")
BOT_TOKEN=env.str("BOT_TOKEN")
ADMIN_ID=env.str("ADMIN_ID")

bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

if not user_in_tabel_users(user_id=int(ADMIN_ID)):
    insert_user(user_id=int(ADMIN_ID))

@dp.message_handler(commands=['start', 'help'])
async def start_command(msg: types.Message):
    """
        обработка команд start и help
    """
    await msg.answer('Бот который присылает новые объявления с avito.ru по запросу.\
Чтобы отслеживать объявления - отправьте настроенную ссылку из браузера.\
Для отмены - отправьте ссылку повторно.\
Комманда /all показывает все Ваши ссылки.\
Бот закрытый, для его разблокировки напишите админу @Nikiforov1601\
Новые объявления приходят с периодичностью в 60 минут,\
с 9.00 до 21.00')


@dp.message_handler(commands=['all'])
async def all_command(msg: types.Message):
    """
        обработка команды all для получения ссылок на все подписки
    """
    user_id=int(msg.from_id)
    # print(user_id)
    user_in_db = user_in_tabel_users(user_id)
    if user_in_db:
        all_subscriptions = get_all_subscriptions(user_id=user_id)
        if all_subscriptions:
            for subscription in all_subscriptions:
                await msg.answer(subscription.subscription, disable_web_page_preview=True)
        else:
            await msg.answer("Активных подписок нет!")
    else:
        await msg.answer("Ты не авторизованный пользователь, для доступа напиши админу чата @Nikiforov1601")

# @dp.message_handler(is_forwarded=True)
@dp.message_handler(ForwardedMessageFilter(True))
async def handle_forwarded_message(msg: types.Message):
    """
        Обработка пересланных сообщений от Админа
        Предоставление доступа пользователю
    """
    text = msg.text # получите текст исходного сообщения, которое было переслано
    user_id = msg.forward_from.id # id пользывателя из пересланного сообщения
    user_my_id = msg.from_id
    print(f'Текст пересланного сообщения: {text}')
    print(f'Id пользователя, чье сообщение переслали: {user_id}')
    print(f'Id пользователя, кто переслал сообщение: {user_my_id}')
    if user_my_id == int(ADMIN_ID):
        user = user_in_tabel_users(user_id=user_id)
        print(user)
        if user:
            await msg.answer('Пользователь уже есть в БД')
        else:
            insert_user(user_id=user_id)
            await msg.answer('Пользователь добавлен в БД')
            await bot.send_message(user_id, "Вас добавили в бота")


@dp.message_handler(Text)
async def text_gandler(msg: types.Message):
    """
        обработка сообщений пользователя
    """
    user_id = int(msg.from_id)
    user_activate = user_in_tabel_users(user_id)
    # if user_id != int(ADMIN_ID):
    if not user_activate:
        await msg.answer('Ты не авторизованный пользователь, для доступа напиши админу чата @Nikiforov1601')
    else:
        if 'avito.ru' in str(msg.text).lower():
            request_link = msg.text
            result = check_request_in_db(request_link, user_id=user_id)
            if result is None:
                insert_request_to_subscription(request_link,user_id=user_id)
                await msg.answer('Теперь все новые объявления будут приходить в этот чат. Ждите!')
                posts_data = get_posts_data(request_link)
                for post_data in posts_data:
                    post_name = post_data['post_name']
                    post_link = post_data['post_link']
                    insert_post_to_posts(post_name, post_link, user_id=user_id)
                print('Проверка постов после подписки завершена')
            else:
                unsubscription(request_link=msg.text, user_id=user_id)
                await msg.answer('Вы отписались')
        else:
            await msg.answer('Я понимаю только ссылки на avito')


async def task():
    """
        получение новых постов с авито
    """
    # all_subscriptions = get_all_subscriptions()
    all_user_id = get_all_user_id()
    print('-------------------------------------------')
    print('-------Началась проверка новых постов------')
    print('-------------------------------------------')
    # if all_subscriptions != []:
    #     for subscription in all_subscriptions:
    #         request_link = subscription.subscription
    #         posts_data = get_posts_data(request_link)
    #         await send_new_posts(posts_data)

    for user_id in all_user_id:
        all_subscriptions = get_all_subscriptions(user_id=user_id)
        if all_subscriptions != []:
            for subscription in all_subscriptions:
                request_link = subscription.subscription
                posts_data = get_posts_data(request_link)
                await send_new_posts(posts_data, user_id)
    print('-------------------------------------------')
    print('------Проверка новых постов завершена------')
    print('-------------------------------------------')


async def send_new_posts(posts_data, user_id):
    """
        отправка новых постов с авито пользователю
    """
    for post_data in posts_data:
        post_name = post_data['post_name']
        post_price = post_data['post_price']
        post_budge = post_data['post_budge']
        post_params = post_data['post_params']
        post_description = post_data['post_description']
        post_geo = post_data['post_geo']
        post_link = post_data['post_link']
        result = check_post_in_db(post_link)
        if result is None:
            await bot.send_message(user_id,
                                   f'<a href="{post_link}">{post_name}</a>\n\
{post_price} {post_budge}\n\
{post_params}\n\
{post_description}\n\
район: {post_geo}', disable_web_page_preview=True)
            insert_post_to_posts(post_name, post_link, user_id=user_id)


async def scheduller():
    aioschedule.every(CHECK_FREQUENCY).minutes.do(task)
    while True:
        # Получаем текущее время
        current_time = datetime.now().time().hour
        # выполняем основную функцию
        await aioschedule.run_pending()
        # если время 21 час, засыпаем на 12 часов
        if current_time == 21:
            await asyncio.sleep(43200)
        else:
            # Генерируем случайное число от 1 до 30, что бы авито не заподозрило парсинг
            random_number = random.randint(1, 30)
            # print(f'Заснули на {random_number} секунд')
            await asyncio.sleep(random_number)


async def on_startup(_):
    asyncio.create_task(scheduller())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
