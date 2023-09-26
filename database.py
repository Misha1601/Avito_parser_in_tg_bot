from sqlalchemy import create_engine, Column, String, Integer, distinct, Boolean
from sqlalchemy.orm import Session, DeclarativeBase


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
    max_subscriptions = Column(Integer, default=3, nullable=True)
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
    get_all_user_id = [result[0] for result in session.query(distinct(Subscriptions.user_id)).all()]
    return get_all_user_id

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
            user.active = False
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
            user.active = True
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
    user_number = user.max_subscriptions
    if user:
        try:
            user.max_subscriptions = user_number + number
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
    insert_user(12)
    activate_user(23232)
