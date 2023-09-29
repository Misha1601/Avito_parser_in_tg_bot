import asyncio
from datetime import datetime
import random
import aioschedule
from environs import Env
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, ForwardedMessageFilter
from config import CHECK_FREQUENCY
import parser
import database
import re


env = Env()
env.read_env(".env")
BOT_TOKEN=env.str("BOT_TOKEN")
ADMIN_ID=env.str("ADMIN_ID")
USERNAME_ADMINE=env.str("USERNAME_ADMINE")

bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

# если БД не создана, создаем её, добавляя администратора
if not database.user_in_tabel_users(user_id=int(ADMIN_ID)):
    database.insert_user(user_id=int(ADMIN_ID), user_nikname=USERNAME_ADMINE)

@dp.message_handler(commands=['start', 'help'])
async def start_command(msg: types.Message):
    """
        обработка команд start и help
    """
    await msg.answer(f'Бот который присылает новые объявления с avito.ru.\n\
Бот работает для Авто и Недвижимости, в остальных категориях может не работать. \
Чтобы отслеживать объявления - отправьте настроенную ссылку из браузера. \
Для отмены - отправьте ссылку повторно.\n\
Комманда /all показывает все Ваши ссылки.\n\
Бот закрытый, для его разблокировки напишите админу {USERNAME_ADMINE}\n\
Новые объявления приходят с периодичностью в 60 минут, \
с 9.00 до 21.00')
    if int(msg.from_id) == int(ADMIN_ID):
        await msg.answer('Команды для управления ботом\n\
После команды /all выводится список активных подписчиков.\n\
Для изменения количества подписок пишем боту по шаблону: \n"Username число"\n \
Username - всегда начинается с @\n\
Число - положительное или отрицательное')


@dp.message_handler(commands=['all'])
async def all_command(msg: types.Message):
    """
        обработка команды all для получения ссылок на все подписки
    """
    user_id=int(msg.from_id)
    user_in_db = database.user_in_tabel_users(user_id)
    if user_in_db:
        all_subscriptions = database.get_all_subscriptions(user_id=user_id)
        if all_subscriptions:
            for subscription in all_subscriptions:
                await msg.answer(subscription.subscription) #, disable_web_page_preview=True)
        else:
            await msg.answer("Активных подписок нет!")
    else:
        await msg.answer(f"Ты не авторизованный пользователь, для доступа напиши админу чата {USERNAME_ADMINE}")
    if user_id == int(ADMIN_ID):
        users = database.all_users_in_table_users()
        for user in users:
            await msg.answer(user.user_nikname)


# @dp.message_handler(is_forwarded=True)
@dp.message_handler(ForwardedMessageFilter(True))
async def handle_forwarded_message(msg: types.Message):
    """
        Обработка пересланных сообщений от Админа
        Предоставление доступа пользователю
    """
    text = msg.text # получите текст исходного сообщения, которое было переслано
    user_id = msg.forward_from.id # id пользывателя из пересланного сообщения
    user_nikname = msg.forward_from.username # username пользывателя из пересланного сообщения
    user_my_id = msg.from_id
    if user_my_id == int(ADMIN_ID):
        user = database.user_in_tabel_users(user_id=user_id)
        if user:
            await msg.answer('Пользователь уже есть в БД')
        else:
            database.insert_user(user_id=user_id, user_nikname=f'@{user_nikname}')
            await msg.answer(f'Пользователь @{user_nikname} добавлен в БД')
            await bot.send_message(user_id, "Чат бот разблокирован")


@dp.message_handler(Text)
async def text_gandler(msg: types.Message):
    """
        обработка сообщений пользователя
    """
    user_id = int(msg.from_id)
    user_activate = database.user_in_tabel_users(user_id)
    if not user_activate:
        await msg.answer(f'Ты не авторизованный пользователь, для доступа напиши админу чата {USERNAME_ADMINE}')
    else:
        if 'avito.ru' in str(msg.text).lower():
            request_link = msg.text
            result = database.check_request_in_db(request_link=msg.text, user_id=user_id)
            if result is None:
                user_max_sub = database.user_in_tabel_users(user_id=user_id).max_subscriptions
                count_user_sub = len(database.get_all_subscriptions(user_id=user_id))
                if count_user_sub < user_max_sub:
                    database.insert_request_to_subscription(request_link, user_id=user_id)
                    await msg.answer('Теперь все новые объявления будут приходить в этот чат. Ждите!')
                    # Собираем все текущие объявления в БД
                    posts_data = parser.get_posts_data(request_link)
                    for post_data in posts_data:
                        post_name = post_data['post_name']
                        post_link = post_data['post_link']
                        post = database.check_post_in_db(post_link, user_id=user_id)
                        if not post:
                            database.insert_post_to_posts(post_name, post_link, user_id=user_id)
                    print('Проверка постов после подписки завершена')
                else:
                    await msg.answer(f'Максимальное количество подписок = 2, если нужно ещё больше подписок, пиши {USERNAME_ADMINE}')
            else:
                database.unsubscription(request_link=msg.text, user_id=user_id)
                await msg.answer('Вы отписались от этой подписки!')
        else:
            if user_id != int(ADMIN_ID):
                await msg.answer('Я понимаю только ссылки на avito')
            else:
                if msg.text[0] == '@':
                    text_user = msg.text.split()
                    activ_users = database.all_users_in_table_users()
                    activ_user = [activ_user.user_nikname for activ_user in activ_users]
                    if (len(text_user) != 2) or (not re.match(r'^-?\d+$', text_user[-1])):
                        await msg.answer('В введенной команде ошибка')
                    else:
                        if text_user[0] not in activ_user:
                            await msg.answer('Или пользователь введен с ошибкой, или его нет в автивных подписчиках')
                        else:
                            user_id_in_text = [a.user_id for a in activ_users if a.user_nikname == text_user[0]][0]
                            if user_id_in_text:
                                database.add_or_reduce_max_subscriptions(user_id=user_id_in_text, number=text_user[-1])
                                max_sub = database.user_in_tabel_users(user_id=user_id_in_text).max_subscriptions
                                await msg.answer(f'Пользователю {text_user[0]} изменено максимальное количество подписок на {text_user[1]}, теперь оно = {max_sub}')
                else:
                    await msg.answer('Я понимаю только ссылки на avito')


async def task():
    """
        получение новых постов с авито
    """
    all_user_id = database.get_all_user_id()
    print('-------Началась проверка новых постов------')
    for user_id in all_user_id:
        all_subscriptions = database.get_all_subscriptions(user_id=user_id)
        if all_subscriptions != []:
            for subscription in all_subscriptions:
                request_link = subscription.subscription
                posts_data = parser.get_posts_data(request_link)
                await send_new_posts(posts_data, user_id)
                seconds = random.randint(1, 5)
                await asyncio.sleep(seconds)
    print('-------------------------------------------')
    print('------Проверка новых постов завершена------')


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
        result = database.check_post_in_db(post_link, user_id=user_id)
        if not result:
            await bot.send_message(user_id,
                                   f'<a href="{post_link}">{post_name}</a>\n\
{post_price} {post_budge}\n\
{post_params}\n\
{post_description}\n\
район: {post_geo}', disable_web_page_preview=True)
            database.insert_post_to_posts(post_name, post_link, user_id=user_id)


async def scheduller():
    aioschedule.every(CHECK_FREQUENCY).minutes.do(task)
    while True:
        # Получаем текущее время в виде часа
        current_time = datetime.now().time().hour
        # выполняем основную функцию
        await aioschedule.run_pending()
        # каждый час засыпаем на час, если время с 21 до 9
        if current_time == 21:
            await asyncio.sleep(43200)
        else:
            # Генерируем случайное число от 1 до 30, что бы авито не заподозрило парсинг
            random_number = random.randint(1, 30)
            # Заснули на random_number секунд
            await asyncio.sleep(random_number)


async def on_startup(_):
    asyncio.create_task(scheduller())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
