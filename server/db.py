"""В данном файле созданы функции, которые меняют содержимое БД"""

from datetime import datetime

from server.src.log_config import client_log
from server.src.models import (
    Base,
    Department,
    Follow,
    Media,
    Profile,
    Tweet,
    TweetLike,
    User,
    engine,
    session,
)


def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    new_user = User(username="Alice", email="alice@example.com")
    new_user2 = User(username="Nik", email="nik@example.com")
    session.add(new_user)
    session.add(new_user2)
    session.commit()

    new_profile = Profile(
        user_id=new_user.id,
        nickname="Ali",
        age=22,
        photo=b"photo_data",
        country="Russia",
        phone_number="81234567890",
    )
    new_profile2 = Profile(
        user_id=new_user2.id,
        nickname="N",
        age=18,
        photo=b"photo_data",
        country="Belarus",
        phone_number="81234567890",
    )
    session.add(new_profile)
    session.add(new_profile2)
    session.commit()

    new_tweet = Tweet(
        tweet_data="Hello, Twitter!",
        date=datetime.now(),
        tweet_media_ids={1, 2},
        user_id=new_user.id,
    )
    session.add(new_tweet)
    session.commit()

    new_department = Department(name="IT Department")
    session.add(new_department)
    session.commit()

    new_profile.departments.append(new_department)
    session.commit()

    new_media = Media(
        media_data=b"binary_data",
        file_size=165902,
        url="http://yourdomain.com/uploads/123.png",
    )

    new_media2 = Media(
        media_data=b"binary_data",
        file_size=165902,
        url="http://yourdomain.com/uploads/456.png",
    )
    session.add(new_media)
    session.add(new_media2)
    session.commit()


def add_new_tweet(tweet_data, tweet_media_ids, user_id):
    new_tweet = Tweet(
        tweet_data=tweet_data,
        date=datetime.now(),
        tweet_media_ids=tweet_media_ids,
        user_id=user_id,
    )
    session.add(new_tweet)
    session.commit()
    client_log.info(f"Клиент с ID {new_tweet.user_id} создал твит №{new_tweet.id}")

    return new_tweet


def add_new_media(file_data, file_size, url):
    media = Media(media_data=file_data, file_size=file_size, url=url)
    session.add(media)
    session.commit()
    client_log.info(f"Добавлен новый файл {media.media_data} в БД")

    return media


def delete_tweet(tweet):
    session.delete(tweet)
    session.commit()
    client_log.info(f"Твит №{tweet.id} удален пользователем {tweet.user_id}")


def add_like(tweet_id, user_id):
    new_tweet_like = TweetLike(tweet_id=tweet_id, author_id=user_id)
    session.add(new_tweet_like)
    session.commit()
    client_log.debug(f"Пользователь {user_id} лайкнул твит №{tweet_id}")


def delete_like(tweet_like, tweet_id, user_id):
    session.delete(tweet_like)
    session.commit()
    client_log.debug(f"Пользователь {user_id} дизлайкнул твит №{tweet_id}")


def add_follow(follower_id, followed_id):
    new_follow = Follow(follower_id=follower_id, followed_id=followed_id)
    session.add(new_follow)
    session.commit()
    client_log.debug(
        f"Пользователь {follower_id} подписался на пользователя {followed_id}"
    )


def delete_follow(follow, follower_id, followed_id):
    session.delete(follow)
    session.commit()
    client_log.debug(
        f"Пользователь {follower_id} отписался от пользователя {followed_id}"
    )
