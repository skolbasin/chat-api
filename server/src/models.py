from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Table,
    create_engine,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine("postgresql://postgres:1122@db/db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):  # type: ignore
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)

    profile = relationship(
        "Profile", backref="user", uselist=False, cascade="all, delete"
    )


class Profile(Base):  # type: ignore
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint("LENGTH(photo) <= 1048576", name="check_photo_size"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nickname = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    photo = Column(LargeBinary, nullable=True)
    country = Column(String(50), nullable=True)
    phone_number = Column(String(15), nullable=True)

    departments = relationship("Department", secondary="profile_department")

    def __repr__(self):
        return f"Профиль {self.id} пользователя №{self.user_id}"


class Tweet(Base):  # type: ignore
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    tweet_data = Column(String(280), nullable=False)
    date = Column(DateTime, nullable=False)
    tweet_media_ids = Column(ARRAY(Integer), nullable=True)  # type: ignore
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", backref="tweets")
    likes = relationship("TweetLike", lazy="dynamic", cascade="all, delete")

    def __repr__(self):
        return f"Твит №{self.id} {self.tweet_data}"


class Department(Base):  # type: ignore
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Media(Base):  # type: ignore
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    media_data = Column(LargeBinary, nullable=False)
    file_size = Column(Integer, CheckConstraint("file_size <= 10000000"))
    url = Column(String)


profile_department = Table(
    "profile_department",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("profiles.id")),
    Column("department_id", Integer, ForeignKey("departments.id")),
)


class TweetLike(Base):  # type: ignore
    __tablename__ = "tweet_likes"

    tweet_id = Column(ForeignKey("tweets.id"), primary_key=True)  # type: ignore
    author_id = Column(ForeignKey("users.id"), primary_key=True)  # type: ignore

    user = relationship("User", backref="users")


class Follow(Base):  # type: ignore
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    followed_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    def __repr__(self):
        return f"Пользователь {self.follower_id} подписан на пользователя {self.followed_id})"
