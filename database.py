from sqlalchemy import create_engine, Column, String, Integer, distinct, Boolean
from sqlalchemy.orm import Session, DeclarativeBase
import re


try:
    engine = create_engine('sqlite:///database.db')
except Exception as error:
    pass


class Base(DeclarativeBase):
    pass

class Users(Base):
    """
        таблица пользователей имеющих доступ к боту
    """
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer, nullable=True)
    user_nikname = Column(String, nullable=True)
    max_subscriptions = Column(Integer, default=2, nullable=True)
    active = Column(Boolean, default=True)

class Subscriptions(Base):
    """
        таблица подписок пользоветеля
    """
    __tablename__ = 'subscriptions'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer, nullable=True)
    subscription = Column(String(200), nullable=False)


class Posts(Base):
    """
        таблица распарсенных объявлений
    """
    __tablename__ = 'posts'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer, nullable=True)
    post_name = Column(String(200), nullable=False)
    post_link = Column(String(200), nullable=False)


try:
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
except Exception as error:
    pass

def get_all_user_id():
    """
        Получение списка пользователей имеющих подписку
    """
    res = session.query(distinct(Subscriptions.user_id)).all()
    return [result[0] for result in res]

def check_request_in_db(request_link, user_id):
    """
        проверка наличия подписки в базе данных
    """
    request = session.query(Subscriptions).filter(Subscriptions.subscription == request_link, Subscriptions.user_id == user_id).first()
    return request

def insert_user(user_id, user_nikname):
    """
        Добавление пользователя
    """
    user = session.query(Users).filter_by(user_id=user_id).first()
    if user:
        return None
    else:
        user = Users(user_id=user_id, user_nikname=user_nikname)
        try:
            session.add(user)
            session.commit()
        except Exception as error:
            pass

def deactivate_user(user_id):
    """
        Деактивация пользователя
    """
    user = session.query(Users).filter_by(user_id=user_id).first()
    if user:
        try:
            user.active = False # type: ignore
            session.commit()
        except Exception as error:
            pass

def activate_user(user_id):
    """
        Активация пользователя
    """
    user = session.query(Users).filter_by(user_id=user_id, active=False).first()
    if user:
        try:
            user.active = True # type: ignore
            session.commit()
        except Exception as error:
            pass

def user_in_tabel_users(user_id):
    """
        Проверка пользователя в таблице Users
    """
    user = session.query(Users).filter_by(user_id=user_id, active=True).first()
    return user

def all_users_in_table_users(active=True):
    """
    Вывод всех активных пользователей в таблице Users
    """
    users = session.query(Users).filter_by(active=True).all()
    return users

def add_or_reduce_max_subscriptions(user_id, number=1):
    """
        Изменение максимального количества подписок пользователя
    """
    user = session.query(Users).filter_by(user_id=user_id, active=True).first()
    user_number = user.max_subscriptions # type: ignore
    number1 = int(number)
    if user:
        try:
            user.max_subscriptions = user_number + number1 # type: ignore
            session.commit()
        except Exception as error:
            pass

def insert_request_to_subscription(request_link, user_id):
    """
        добавление подписки в базу данных
    """
    subscriptions = Subscriptions(subscription=request_link, user_id=user_id)
    try:
        session.add(subscriptions)
        session.commit()
    except Exception as error:
        pass

def check_post_in_db(post_link, user_id):
    """
        проверка нахождения объявления в базе данных
    """
    request = session.query(Posts).filter(Posts.post_link == post_link, Posts.user_id == user_id).first()
    return request

def insert_post_to_posts(post_name, post_link, user_id):
    """
        вставка объявления в базу данных
    """
    posts = Posts(post_name=post_name, post_link=post_link, user_id=user_id)
    try:
        session.add(posts)
        session.commit()
    except Exception as error:
        pass

def get_all_subscriptions(user_id):
    """
        получение списка всех подписок пользователя
    """
    all_subscriptions = session.query(Subscriptions).filter(Subscriptions.user_id == user_id).all()
    return all_subscriptions

def unsubscription(request_link, user_id):
    """
        удаление подписки из базы данных
    """
    subscription = session.query(Subscriptions).filter(Subscriptions.subscription == request_link, Subscriptions.user_id == user_id).first()
    try:
        session.delete(subscription)
        session.commit()
    except Exception as error:
        pass

if __name__ == '__main__':
    # insert_request_to_subscription('link111111', 111)
    # insert_request_to_subscription('link222222', 222)
    # insert_request_to_subscription('link333333', 333)
    # insert_request_to_subscription('link444444', 111)
    # insert_request_to_subscription('link555555', 222)
    # post = check_request_in_db('link111111')
    # print(post.subscription)
    # insert_post_to_posts('11', 'qqqq', user_id=111)
    # insert_post_to_posts('111', 'wwww', user_id=111)
    # insert_post_to_posts('22', 'eeee', user_id=222)
    # print(check_post_in_db('qqqq', user_id=111))
    # print([(i.user_id, i.subscription) for i in get_all_subscriptions()])
    # print(unsubscription('link222222', user_id=333))
    # print(get_all_user_id())
    # insert_user(12)
    # activate_user(23232)
    # user = all_users_in_table_users()
    # print([a.user_nikname for a in user])
    text_user = "@Nikiforov1601 1".split()
    print(text_user)
    activ_users = all_users_in_table_users()
    activ_user = [activ_user.user_nikname for activ_user in activ_users]
    print(activ_user)
    print(re.match(r'^-?\d+$', text_user[-1]))
    if (len(text_user) != 2) or (not re.match(r'^-?\d+$', text_user[-1])):
        print('В введенной команде ошибка')
    else:
        if text_user[0] not in activ_user:
            print('Или пользователь введен с ошибкой, или его нет в автивных подписчиках')
        else:
            user_id_in_text = [a.user_id for a in activ_users if a.user_nikname == text_user[0]][0] # type: ignore
            print(user_id_in_text)
            if user_id_in_text: # type: ignore
                add_or_reduce_max_subscriptions(user_id=user_id_in_text, number=text_user[-1]) # type: ignore
                max_sub = user_in_tabel_users(user_id=user_id_in_text).max_subscriptions # type: ignore
                print(f'Пользователю {text_user[0]} изменено максимальное количество подписок на {text_user[1]}, теперь оно = {max_sub}')