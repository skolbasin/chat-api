import io

import pytest
from werkzeug.datastructures import FileStorage


@pytest.mark.parametrize(
    "route", ["/api/tweets", "/api/tweets/follow", "/api/users/me", "/api/users/2"]
)
def test_get_endpoints(client, route, app):
    """
    Тест проверяет, что все GET-методы возвращают код 200.
    """
    resp = client.get(route)
    assert resp.status_code == 200


def test_create_tweet(client):
    """
    Тест проверяет создание твита.
    """
    tweet_data = {"tweet_data": "test", "user_id": 1}

    resp = client.post("/api/tweets", json=tweet_data, headers={"api_key": "1"})
    assert resp.status_code == 200
    assert resp.json()["result"] == True


def test_add_media(client):
    """
    Тест проверяет создание файла.
    """
    file_data = b"binary data representing a file"
    file = FileStorage(io.BytesIO(file_data), filename="test.png")

    resp = client.post("/api/media", data={"file": file})
    assert resp.status_code == 200
    assert resp.json["result"] == True
    assert "media_id" in resp.son

    assert "media_id" in resp.json
    assert resp.json["media_id"] > 0

    resp = client.post("/api/media")
    assert resp.status_code == 400
    assert resp.json["error"] == "Файл не был передан"


def test_del_tweet(client):
    """
    Тест проверяет удаление твита.
    """
    tweet_id = 1
    user_id = 5

    resp = client.delete(f"/api/tweets/{tweet_id}", json={"user_id": user_id})
    assert resp.status_code == 200
    assert resp.json["result"] == True
    assert "error" not in resp.json

    resp = client.delete(f"/api/tweets/{tweet_id}")
    assert resp.status_code == 403
    assert resp.json()["error"] == "user_id is required"

    resp = client.delete(f"/api/tweets/{tweet_id}", json={"user_id": 6})
    assert resp.status_code == 403
    assert resp.json["error"] == "Невозможно удалить чужой твит"

    resp = client.delete("/api/tweets/1000", json={"user_id": user_id})
    assert resp.status_code == 404
    assert resp.json["error"] == "Твит не найден"


def test_like_tweet(client):
    """
    Тест проверяет возможность поставить лайк под твитом.
    """
    tweet_id = 1
    user_id = 5

    resp = client.post(f"/api/tweets/{tweet_id}/likes", json={"user_id": user_id})
    assert resp.status_code == 200
    assert resp.json["result"] == True
    assert "error" not in resp.json

    resp = client.post(f"/api/tweets/{tweet_id}/likes", json={"user_id": user_id})
    assert resp.status_code == 200
    assert resp.json["result"] == False
    assert "error" in resp.json
    assert resp.json["error"] == "Этот пользователь уже поставил лайк под данным твитом"

    resp = client.post(f"/api/tweets/{tweet_id}/likes")
    assert resp.status_code == 400
    assert resp.json()["error"] == "user_id is required"


def test_unlike_tweet(client):
    """
    Тест проверяет возможность убрать лайк под твитом.
    """
    tweet_id = 1
    user_id = 5

    client.post(f"/api/tweets/{tweet_id}/likes", json={"user_id": user_id})
    resp = client.delete(f"/api/tweets/{tweet_id}/likes", json={"user_id": user_id})
    assert resp.status_code == 200
    assert resp.json["result"] == True
    assert "error" not in resp.json

    resp = client.delete(f"/api/tweets/{tweet_id}/likes", json={"user_id": user_id})
    assert resp.status_code == 200
    assert resp.json["result"] == False
    assert "error" in resp.json
    assert resp.json["error"] == "Данный пользователь не лайкал данный твит"

    resp = client.delete(f"/api/tweets/{tweet_id}/likes")
    assert resp.status_code == 400
    assert resp.json()["error"] == "user_id is required"


def test_follow_user(client):
    """
    Тест проверяет возможность подписаться на пользователя
    """
    user_id = 1
    follower_id = 5

    resp = client.post(f"/api/users/{user_id}/follow", json={"user_id": follower_id})
    assert resp.status_code == 200
    assert resp.json["result"] == True
    assert "error" not in resp.json

    resp = client.post(f"/api/users/{user_id}/follow", json={"user_id": follower_id})
    assert resp.status_code == 200
    assert resp.json["result"] == False
    assert "error" in resp.json
    assert (
        resp.json["error"]
        == "Этот пользователь уже подписан на указанного пользователя"
    )

    resp = client.post("/api/users/1000/follow", json={"user_id": follower_id})
    assert resp.status_code == 200
    assert resp.json["result"] == False
    assert "error" in resp.json
    assert (
        resp.json["error"]
        == "На пользователя №1000 не подписаться, т.к. его нет в базе"
    )

    resp = client.post(f"/api/users/{user_id}/follow")
    assert resp.status_code == 400
    assert resp.json()["error"] == "user_id is required"


def test_delete_follow_user(client):
    """
    Тест проверяет возможность отписаться от пользователя
    """
    user_id = 1
    follower_id = 5

    client.post(f"/api/users/{user_id}/follow", json={"user_id": follower_id})
    resp = client.delete(f"/api/users/{user_id}/follow", json={"user_id": follower_id})
    assert resp.status_code == 200
    assert resp.json["result"] == True
    assert "error" not in resp.json

    resp = client.delete(f"/api/users/{user_id}/follow", json={"user_id": follower_id})
    assert resp.status_code == 200
    assert resp.json["result"] == False
    assert "error" in resp.json
    assert (
        resp.json["error"]
        == f"Пользователь №{follower_id} не подписан на пользователя №{user_id}"
    )

    resp = client.delete("/api/users/1000/follow", json={"user_id": follower_id})
    assert resp.status_code == 200
    assert resp.json["result"] == False
    assert "error" in resp.json
    assert (
        resp.json["error"]
        == "На пользователя №1000 не подписаться, т.к. его нет в базе"
    )

    resp = client.delete(f"/api/users/{user_id}/follow")
    assert resp.status_code == 400
    assert resp.json()["error"] == "user_id is required"
