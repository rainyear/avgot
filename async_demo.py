import asyncio
import aiohttp
import time
import uvloop

start = time.perf_counter()
words = ["Hello", "Python", "Haha", "!"]

async def getPage(session, word):
    with aiohttp.Timeout(10):
        # URL = "http://douban.com/"
        URL = "http://127.0.0.1:8000/{}"
        async with session.get(URL.format(word)) as resp:
            print(await resp.text())

# loop = uvloop.new_event_loop()
# asyncio.set_event_loop(loop)
loop = asyncio.get_event_loop()
session = aiohttp.ClientSession(loop=loop)
tasks = []
for word in words:
    tasks.append(getPage(session, word))
loop.run_until_complete(asyncio.gather(*tasks))
loop.close()
session.close()
end = time.perf_counter()
print("Total time: {}".format(end-start))
