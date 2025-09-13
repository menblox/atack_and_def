import aiohttp
import asyncio
import aiofiles

import time

import random
import string

target = "http://192.168.0.185:8000/register/"
target_token = "http://192.168.0.185:8000/token/"
target_get = "http://192.168.0.185:8000/users/me/"

REQUESTS = 1000
limit = asyncio.Semaphore(300)
limit_get = asyncio.Semaphore(300)

def random_string(length=8):
            letters = string.ascii_lowercase + string.digits
            return ''.join(random.choice(letters) for _ in range(length))

async def atack(i, session):
    
    async with limit:
        try:     
            email = f"{random_string()}@gmail.com"
            password = random_string(10)

            payload = {
                "name": f"user_{random_string(4)}",
                "age": 25,
                "town": random.choice(["Moscov", "New York", "Rostov", "Kazan"]),
                "email": email,
                "password": password
            }

            start_time = time.perf_counter()
            async with session.post(target, json=payload) as resp:
                latency = time.perf_counter() - start_time
                print(f"[{i}] REG status={resp.status}, latency={latency:.4f}s")

                try:
                    data = await resp.json()  # пробуем прочитать JSON
                    async with aiofiles.open("log_post.txt", "a") as f:
                        await f.write(f"[{i}] status={resp.status}, response={data}, password={password} latency={latency:.4f}s\n\n")

                except Exception:
                    text = await resp.text()
                    async with aiofiles.open("log_post.txt", "a") as f:
                        await f.write(f"[{i}] status={resp.status}, latency={latency:.4f}s, response (not JSON): {text}\n")
                    
            log_pay = {"username": email, "password": password}
            start_time = time.perf_counter()
            async with session.post(target_token, data=log_pay) as resp:
                latency = time.perf_counter() - start_time
                print(f"[{i}] LOGIN status={resp.status}, latency={latency:.4f}s")
                 
                if resp.status == 200:
                    try:
                        login_data = await resp.json()
                        async with aiofiles.open("log_login.txt", "a") as f:
                            await f.write(f"[{i}] LOGIN status={resp.status}, response={login_data}, latency={latency:.4f}s\n\n")
                            print(f"[{i}] LOGIN status={resp.status}, latency={latency:.4f}s, body={login_data}")
                    except Exception:
                        login_data = await resp.text()
                        async with aiofiles.open("log_login.txt", "a") as f:
                            await f.write(f"[{i}] LOGIN status={resp.status}, response={login_data}, latency={latency:.4f}s\n\n")
                            print(f"[{i}] LOGIN_not_json status={resp.status}, latency={latency:.4f}s, body={login_data}")                    

                    # 4) Попытка извлечь токен из ответа
                    token = None
                    if isinstance(login_data, dict):
                        token = login_data.get("access_token")

                    if token:
                        headers = {"Authorization": f"Bearer {token}"}
                        async with limit_get:

                            try:
                                start_time = time.perf_counter()
                                async with session.get(target_get, headers=headers) as resp:
                                    latency = time.perf_counter() - start_time
                                    print(f"[{i}] GET status={resp.status}, latency={latency:.4f}s")
                                    try:
                                        data = await resp.json()
                                        async with aiofiles.open("log_get.txt", "a") as f:
                                            await f.write(f"[{i}] status={resp.status}, response={data}, latency={latency:.4f}s\n\n")

                                    except Exception:
                                        data = await resp.text()
                                        async with aiofiles.open("log_get.txt", "a") as f:
                                            await f.write(f"[{i}] status={resp.status}, response={data}, latency={latency:.4f}s\n\n")
                                            
                            except Exception as e:
                                print(f"[GET {i}] Error: {e}")

        except Exception as e:
            print(f"[{i}] Error: {e}")
    

async def main():
    async with aiohttp.ClientSession() as session:
        task = []

        for i in range(REQUESTS):
            task.append(asyncio.create_task(atack(i, session)))

        if task:
            await asyncio.gather(*task)

if __name__ == "__main__":
    asyncio.run(main())
