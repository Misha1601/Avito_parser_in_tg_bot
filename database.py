from sqlalchemy import create_engine, Column, String, Integer, distinct
from sqlalchemy.orm import Session, DeclarativeBase


try:
    engine = create_engine('sqlite:///database.db')
except Exception as error:
    pass


class Base(DeclarativeBase):
    pass


class Subscriptions(Base):
    """
        таблица подписок пользоветеля
    """
    __tablename__ = 'subscriptions'
    id = Column(Integer(), primary_key=True)
    chat_id = Column(Integer, nullable=True)
    subscription = Column(String(200), nullable=False)


class Posts(Base):
    """
        таблица распарсенных объявлений
    """
    __tablename__ = 'posts'
    id = Column(Integer(), primary_key=True)
    chat_id = Column(Integer, nullable=True)
    post_name = Column(String(200), nullable=False)
    post_link = Column(String(200), nullable=False)


try:
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
except Exception as error:
    pass

def get_all_chat_id():
    """
        Получение списка пользователей имеющих подписку
    """
    get_all_chat_id = [result[0] for result in session.query(distinct(Subscriptions.chat_id)).all()]
    return get_all_chat_id

def check_request_in_db(request_link, chat_id=False):
    """
        проверка наличия подписки в базе данных
    """
    if chat_id:
        request = session.query(Subscriptions).filter(Subscriptions.chat_id == chat_id).first()
    else:
        request = session.query(Subscriptions).filter(Subscriptions.subscription == request_link).first()
    return request

def insert_request_to_subscription(request_link, chat_id=False):
    """
        добавление подписки в базу данных
    """
    if chat_id:
        subscriptions = Subscriptions(subscription=request_link, chat_id=chat_id)
    else:
        subscriptions = Subscriptions(subscription=request_link)
    try:
        session.add(subscriptions)
        session.commit()
    except Exception as error:
        pass

def check_post_in_db(post_link, chat_id=False):
    """
        проверка нахождения объявления в базе данных
    """
    if chat_id:
        request = session.query(Posts).filter(Posts.post_link == post_link, Posts.chat_id == chat_id).first()
    else:
        request = session.query(Posts).filter(Posts.post_link == post_link).first()
    return request

def insert_post_to_posts(post_name, post_link, chat_id=False):
    """
        вставка объявления в базу данных
    """
    if chat_id:
        posts = Posts(post_name=post_name, post_link=post_link, chat_id=chat_id)
    else:
        posts = Posts(post_name=post_name, post_link=post_link)
    try:
        session.add(posts)
        session.commit()
    except Exception as error:
        pass

def get_all_subscriptions(chat_id=False):
    """
        получение списка всех подписок пользователя
    """
    if chat_id:
        all_subscriptions = session.query(Subscriptions).filter(Subscriptions.chat_id == chat_id).all()
    else:
        all_subscriptions = session.query(Subscriptions).all()
    return all_subscriptions

def unsubscription(request_link, chat_id=False):
    """
        удаление подписки из базы данных
    """
    if chat_id:
        subscription = session.query(Subscriptions).filter(Subscriptions.subscription == request_link, Subscriptions.chat_id == chat_id).first()
    else:
        subscription = session.query(Subscriptions).filter(Subscriptions.subscription == request_link).first()
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
    # insert_post_to_posts('11', 'qqqq', chat_id=111)
    # insert_post_to_posts('111', 'wwww', chat_id=111)
    # insert_post_to_posts('22', 'eeee', chat_id=222)
    # print(check_post_in_db('qqqq', chat_id=111))
    # print([(i.chat_id, i.subscription) for i in get_all_subscriptions()])
    # print(unsubscription('link222222', chat_id=333))
    print(get_all_chat_id())
