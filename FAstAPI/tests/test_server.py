import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.server import app, get_db

from app.db.database import Base

test_db_url = "sqlite:///:memory:"

test_engine = create_engine(
    test_db_url, connect_args={"check_same_thread": False}
)

tesingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def over_get_db():
    try:
        db = tesingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = over_get_db

@pytest_asyncio.fixture(name="client")
async def client_fixture():
    Base.metadata.create_all(bind=test_engine)  # Создание всех таблиц в тестовой базе перед запуском тестов
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    Base.metadata.drop_all(bind=test_engine)

###                    HELPER              ###
async def reg(client, data_u):
    resp = await client.post("/register/", json=data_u)

    assert resp.status_code == 201
    data = resp.json()

    assert data["name"] == data_u["name"]
    assert data["age"] == data_u["age"]
    assert data["town"] == data_u["town"]
    assert data["email"] == data_u["email"]
    assert "password" not in data
    assert "id" in data
    


async def login_user(client, data_u):
    resp1 = await client.post("/token/", data=data_u)

    assert resp1.status_code == 200
    data = resp1.json()
    
    assert "access_token" in data
    assert "token_type" in data
    assert "username" not in data
    assert "password" not in data

    return data

###                TEST                ####

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    data_u = {
        "name": "Alex", 
        "age": 20, 
        "town": "Msc", 
        "email": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    await reg(client=client, data_u=data_u)



@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    data_u = {
        "name": "Alex", 
        "age": 20, 
        "town": "Msc", 
        "email": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    await reg(client=client, data_u=data_u)

    data_u1 = {
        "username": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    await login_user(client=client, data_u=data_u1)



###              POST            ###

@pytest.mark.asyncio
async def test_posts(client: AsyncClient):
    data_u = {
        "name": "Alex", 
        "age": 20, 
        "town": "Msc", 
        "email": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    await reg(client=client, data_u=data_u)

    data_u1 = {
        "username": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    token_log = await login_user(client=client, data_u=data_u1)
    acc_token = token_log["access_token"]

    headers = {"Authorization": f"Bearer {acc_token}"}

    resp_post = await client.post(
        "/posts/", json={"title": "test_1", "body": "text_2"}, headers=headers
    )

    assert resp_post.status_code == 200

    data_post = resp_post.json()

    assert data_post["title"] == "test_1"
    assert data_post["body"] == "text_2"
    assert "id" in data_post

    responce_post_fail = await client.post(
        "/posts/", json={"title": "test_1", "body": None}, headers=headers
    )

    assert responce_post_fail.status_code in (401, 422)

    data_post_fail = responce_post_fail.json()

    assert data_post_fail["detail"] in ("Body not found", [{'input': None, 'loc': ['body', 'body'], 'msg': 'Input should be a valid string', 'type': 'string_type'}])


@pytest.mark.asyncio
async def test_get_posts(client: AsyncClient):
    #
    data_u = {
        "name": "Alex", 
        "age": 20, 
        "town": "Msc", 
        "email": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    await reg(client=client, data_u=data_u)

    #
    data_u1 = {
        "username": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    #
    token_log = await login_user(client=client, data_u=data_u1)
    acc_token = token_log["access_token"]

    headers = {"Authorization": f"Bearer {acc_token}"}

    #
    data_posts = {
        "title": "test_1", 
        "body": "text_2"
    }
    resp_post = await client.post(
        "/posts/", json=data_posts, headers=headers
    )

    assert resp_post.status_code == 200

    data_post = resp_post.json()

    assert data_post["title"] == "test_1"
    assert data_post["body"] == "text_2"
    assert "id" in data_post

    #
    resp_get = await client.get("/posts/", headers=headers)

    assert resp_get.status_code == 200

    data_get = resp_get.json()

    assert len(data_get) > 0

    first_post = data_get[0]

    assert first_post["title"] == data_posts["title"]
    assert first_post["body"] == data_posts["body"]
    assert "id" in first_post
    assert "author" in first_post


######## ПОЛУЧЕНИЕ ДАННЫХ ПОЛЬЗОВАТЕЛЯ #########
@pytest.mark.asyncio
async def test_user_info(client: AsyncClient):
    data_u = {
        "name": "Alex", 
        "age": 20, 
        "town": "Msc", 
        "email": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    await reg(client=client, data_u=data_u)

    data_u1 = {
        "username": "alex1231241vo@gmail.com",
        "password": "qwerty"
    }

    token_log = await login_user(client=client, data_u=data_u1)
    acc_token = token_log["access_token"]

    headers = {"Authorization": f"Bearer {acc_token}"}

    resp_get = await client.get(
        "/users/me/", headers=headers
    )

    assert resp_get.status_code == 200

    data_get = resp_get.json()

    assert data_get["name"] == data_u["name"]
    assert data_get["age"] == data_u["age"]
    assert data_get["town"] == data_u["town"]
    assert data_get["email"] == data_u["email"]
    assert "id" in data_get

    resp_get_fail = await client.get("/users/me/")
    
    assert resp_get_fail.status_code == 401

    data_resp_fail = resp_get_fail.json()

    assert data_resp_fail["detail"] == "Not authenticated"