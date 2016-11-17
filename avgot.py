import re
import asyncio
import aiohttp
import async_timeout

from collections import namedtuple
Node = namedtuple("Node", ["url", "re", "callback", "parent"])

class AvBrowser(object):
    _ENTRY = "ENTRY"
    def __init__(self, loop=None):
        self.loop = loop
        self.headers = {
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1)"
                           " AppleWebKit/537.36 (KHTML, like Gecko)"
                           " Chrome/54.0.2840.87 Safari/537.36"),
        }
        self.conn = aiohttp.TCPConnector(verify_ssl=False)
        self.session = aiohttp.ClientSession(loop=loop,
                                             connector=self.conn,
                                             headers=self.headers)
        self.prev_node = None
        self.pipe = {}
        self.max_workers = 2
        self.queue = asyncio.Queue()

    async def get(self, url=""):
        print("LOGINFO av.GET ", url)
        with async_timeout.timeout(10):
            async with self.session.get(url) as resp:
                return await resp.text()
    async def extract(self, url, regexp):
        html = await self.get(url)
        matches = re.findall(regexp, html)
        return matches
    def close(self):
        self.session.close()
        self.loop.close()
    def entry(self, url="", regexp=r''):
        def wrapper(callback):
            node = Node(url, regexp, callback, None)
            if self.pipe.get(self._ENTRY) is None:
                self.pipe[self._ENTRY] = node
            else:
                self.pipe[self.prev_node.callback] = node
            self.prev_node = node
        return wrapper
    def register(self, regexp=r''):
        return self.entry("", regexp)

    def run(self):
        self.queue.put_nowait(self.pipe.get(self._ENTRY))
        async def _run():
            # workers = [asyncio.Task(self.work()) for _ in range(self.max_workers)]
            producer = asyncio.ensure_future(self.work())
            await self.queue.join()
            # for w in workers:
            #     w.cancel()
            producer.cancel()

        self.loop.run_until_complete(_run())

    async def work(self):
        while True:
            node = await self.queue.get()
            results = await node.callback(await self.extract(node.url, node.re), node.parent)
            if results is not None:
                for item in results:
                    p = self.pipe.get(node.callback)
                    if p is not None:
                        next_node = Node(item[0], p.re, p.callback, item)
                        self.queue.put_nowait(next_node)
            self.queue.task_done()
if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    av = AvBrowser(loop)

    @av.entry("https://movie.douban.com/tag/", re.compile('<a href="(\/tag\/.*?)">(.*?)<\/a>'))
    async def entry_parser(result, *info):
        result = result[:2]
        print(result)
        return list(map(lambda x: ("https://movie.douban.com{}".format(x[0]), x[1]), result))

    @av.register(re.compile('<a href="(https:\/\/movie\.douban\.com\/subject\/\d+/)".*?>([\s\S]*?)<\/a>'))
    async def subpage_parser(result, *info):
        print(result)
        def clean(row):
            return (row[0], re.sub(re.compile("<.*?>|\s"), "", row[1]))
        res = list(map(clean, result))
        print(res)
        return res
    @av.register(re.compile('<span property="v:runtime" content="(\d+)">[\s\S]*?<strong class="ll rating_num" property="v:average">(.*?)<\/strong>'))
    async def detail_parser(result, *info):
        print(*info, result)

    av.run()
    av.close()
