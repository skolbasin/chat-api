from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.src.routes import app as myapp

from ..src.models import Base, Department, Media, Profile, Tweet, User

_app = myapp
_app.config["TESTING"] = True
_app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1122@unit_test_db/db"

with _app.app_context():
    engine = create_engine(_app.config["SQLALCHEMY_DATABASE_URI"])
    Session = sessionmaker(bind=engine)
    session = Session()


@pytest.fixture
def app():
    """Фикстура для запуска приложения"""

    Base.metadata.create_all(engine)

    new_user = User(username="Bob", email="bob@example.com")
    new_user2 = User(username="Alice", email="alice@example.com")
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

    yield _app


@pytest.fixture
def client(app):
    """Фикстура для работы с  запросами к приложению"""
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    """Фикстура для работы с БД"""
    with app.app_context():
        engine = create_engine("postgresql://postgres:1122@unit_test_db/db")
        Session = sessionmaker(bind=engine)
        session = Session()

        yield session

        session.close()
        engine.dispose()
