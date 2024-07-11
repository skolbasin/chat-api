import os
from pathlib import Path

from flask import Flask, jsonify, request, render_template, send_from_directory

from server.db import (
    add_follow,
    add_like,
    add_new_media,
    add_new_tweet,
    delete_follow,
    delete_like,
    delete_tweet,
)
from server.decorators import check_api_key, check_user_exists
from server.src.config import enter_user_id
from server.src.models import Follow, Media, Tweet, TweetLike, User, session

app = Flask(__name__)

root_dir = Path(__file__).resolve().parent.parent
template_folder = os.path.join(root_dir, "static/templates")
static_folder = os.path.join(root_dir, "static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<path:path>")
def send_static(path):
    return send_from_directory(static_folder, path)


@app.route("/api/tweets", methods=["POST"])
@check_api_key
@check_user_exists
def add_tweet():
    data = request.json
    tweet_data = data.get("tweet_data")
    tweet_media_ids = data.get("tweet_media_ids", [])
    user_id = data.get("user_id")

    if not tweet_data:
        return jsonify({"error": "Текст твита обязателен"}), 400

    new_tweet = add_new_tweet(tweet_data, tweet_media_ids, user_id)

    return jsonify({"result": True, "tweet_id": new_tweet.id}), 200


@app.route("/api/media", methods=["POST"])
@check_api_key
def add_media():
    if "file" not in request.files:
        return jsonify({"error": "Файл не был передан"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Пустое имя файла"}), 400

    file_data = file.stream.read()
    file_size = len(file_data)
    url = "http://yourdomain.com/uploads/" + file.filename
    new_media = add_new_media(file_data, file_size, url)

    return jsonify({"result": True, "media_id": new_media.id}), 200


@app.route("/api/tweets/<int:tweet_id>", methods=["DELETE"])
@check_api_key
@check_user_exists
def del_tweet(tweet_id):
    tweet = session.query(Tweet).filter_by(id=tweet_id).first()

    if not tweet:
        return jsonify({"error": "Твит не найден"}), 404

    user_id = request.json.get("user_id")

    if tweet.user_id != user_id:
        return jsonify({"error": "Невозможно удалить чужой твит"}), 403

    delete_tweet(tweet)

    return jsonify({"result": True}), 200


@app.route("/api/tweets/<int:id>/likes", methods=["POST"])
@check_api_key
@check_user_exists
def like_tweet(id):
    user_id = request.json.get("user_id")
    tweet_like = (
        session.query(TweetLike).filter_by(tweet_id=id, author_id=user_id).first()
    )
    if tweet_like is None:
        add_like(id, user_id)
        message = {"result": True}
    else:
        message = {
            "result": False,
            "error": "Этот пользователь уже поставил лайк под данным твитом",
        }

    return jsonify(message)


@app.route("/api/tweets/<int:id>/likes", methods=["DELETE"])
@check_api_key
@check_user_exists
def unlike_tweet(id):
    user_id = request.json.get("user_id")
    tweet_like = (
        session.query(TweetLike).filter_by(tweet_id=id, author_id=user_id).first()
    )
    if tweet_like is not None:
        delete_like(tweet_like, id, user_id)
        message = {"result": True}
    else:
        message = {
            "result": False,
            "error": "Данный пользователь не лайкал данный твит'",
        }

    return jsonify(message)


@app.route("/api/users/<int:id>/follow", methods=["POST"])
@check_api_key
@check_user_exists
def follow_user(id):
    follower_id = request.json.get("user_id")

    user_to_follow = session.query(User).filter_by(id=id).first()
    if user_to_follow is None:
        return jsonify(
            {
                "result": False,
                "error": f"На пользователя №{id} не подписаться, т.к. его нет в базе",
            }
        )

    follow = (
        session.query(Follow).filter_by(follower_id=follower_id, followed_id=id).first()
    )
    if follow is None:
        add_follow(follower_id, id)
        return jsonify({"result": True})
    else:
        return jsonify(
            {
                "result": False,
                "error": "Этот пользователь уже подписан на указанного пользователя",
            }
        )


@app.route("/api/users/<int:id>/follow", methods=["DELETE"])
@check_api_key
@check_user_exists
def delete_follow_user(id):
    follower_id = request.json.get("user_id")

    user_to_follow = session.query(User).filter_by(id=id).first()
    if user_to_follow is None:
        return jsonify(
            {
                "result": False,
                "error": f"На пользователя №{id} не подписаться, т.к. его нет в базе",
            }
        )

    follow = (
        session.query(Follow).filter_by(follower_id=follower_id, followed_id=id).first()
    )
    if follow:
        delete_follow(follow, follower_id, id)
        return jsonify({"result": True})
    else:
        return jsonify(
            {
                "result": False,
                "error": f"Пользователь №{follower_id} не подписан на пользователя №{user_to_follow}",
            }
        )


@app.route("/api/tweets", methods=["GET"])
@check_api_key
def get_tweets():
    try:
        tweets = session.query(Tweet).outerjoin(Tweet.likes).all()
        tweet_list = []

        for tweet in tweets:
            media_ids = [media for media in tweet.tweet_media_ids]
            media_urls = [
                media.url
                for media in session.query(Media).filter(Media.id.in_(media_ids)).all()
            ]
            tweet_data = {
                "id": tweet.id,
                "content": tweet.tweet_data,
                "attachments": media_urls,
                "author": {"id": tweet.user_id, "name": tweet.user.username},
                "likes": [
                    {"user_id": like.author_id, "name": like.user.username}
                    for like in tweet.likes
                ],
            }

            tweet_list.append(tweet_data)

        return jsonify({"result": True, "tweets": tweet_list})

    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        response = jsonify(
            {"result": False, "error_type": error_type, "error_message": error_message}
        )
        return response


@app.route("/api/tweets/follow", methods=["GET"])
@check_api_key
def get_follow_tweets():
    # ЗДЕСЬ ВСЕ ИЗИ ДУМАЙ САМ
    try:
        followers = session.query(Follow).filter_by(follower_id=enter_user_id).all()
        followers_ids = [result.followed_id for result in followers]
        tweets = (
            session.query(Tweet)
            .filter(Tweet.id.in_(followers_ids))
            .outerjoin(Tweet.likes)
            .all()
        )

        tweet_list = []

        for tweet in tweets:
            media_ids = [media for media in tweet.tweet_media_ids]
            media_urls = [
                media.url
                for media in session.query(Media).filter(Media.id.in_(media_ids)).all()
            ]
            tweet_data = {
                "id": tweet.id,
                "content": tweet.tweet_data,
                "attachments": media_urls,
                "author": {"id": tweet.user_id, "name": tweet.user.username},
                "likes": [
                    {"user_id": like.author_id, "name": like.user.username}
                    for like in tweet.likes
                ],
            }

            tweet_list.append(tweet_data)

        # если необходимо в ленту добавить остальные твиты неподписанных пользователей
        # tweets_not_followed = session.query(Tweet).filter(~Tweet.id.in_(followers_ids))
        # for tweet in tweets_not_followed:
        #     media_ids = [media for media in tweet.tweet_media_ids]
        #     media_urls = [
        #         media.url
        #         for media in session.query(Media).filter(Media.id.in_(media_ids)).all()
        #     ]
        #     tweet_data = {
        #         "id": tweet.id,
        #         "content": tweet.tweet_data,
        #         "attachments": media_urls,
        #         "author": {"id": tweet.user_id, "name": tweet.user.username},
        #         "likes": [
        #             {"user_id": like.author_id, "name": like.user.username}
        #             for like in tweet.likes
        #         ],
        #     }
        #
        #     tweet_list.append(tweet_data)

        return jsonify({"result": True, "tweets": tweet_list})

    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        response = jsonify(
            {"result": False, "error_type": error_type, "error_message": error_message}
        )
        return response


@app.route("/api/users/me", methods=["GET"])
@check_api_key
def get_my_profile():
    user = session.query(User).filter_by(id=enter_user_id).first()
    followers = (
        session.query(User)
        .join(Follow, Follow.followed_id == User.id)
        .filter(Follow.follower_id == user.id)
        .all()
    )
    following = (
        session.query(User)
        .join(Follow, Follow.follower_id == User.id)
        .filter(Follow.followed_id == user.id)
        .all()
    )

    response = {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.username,
            "followers": [
                {"id": follower.id, "name": follower.username} for follower in followers
            ],
            "following": [
                {"id": followed.id, "name": followed.username} for followed in following
            ],
            "nickname": user.profile.nickname,
            "age": user.profile.age,
            "country": user.profile.country,
            "phone_number": user.profile.phone_number,
        },
    }
    return jsonify(response)


@app.route("/api/users/<int:id>", methods=["GET"])
@check_api_key
def get_user_profile(id):
    user = session.query(User).filter_by(id=id).first()
    followers = (
        session.query(User)
        .join(Follow, Follow.followed_id == User.id)
        .filter(Follow.follower_id == user.id)
        .all()
    )
    following = (
        session.query(User)
        .join(Follow, Follow.follower_id == User.id)
        .filter(Follow.followed_id == user.id)
        .all()
    )

    response = {
        "result": "true",
        "user": {
            "id": user.id,
            "name": user.username,
            "followers": [
                {"id": follower.id, "name": follower.username} for follower in followers
            ],
            "following": [
                {"id": followed.id, "name": followed.username} for followed in following
            ],
            "nickname": user.profile.nickname,
            "age": user.profile.age,
            "country": user.profile.country,
            "phone_number": user.profile.phone_number,
        },
    }
    return jsonify(response)


# @app.route("/")
# def hello():
#     return "Добро пожаловать, всё работает!"

