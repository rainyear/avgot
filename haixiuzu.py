from avgot import AvBrowser
import re
import asyncio
import motor.motor_asyncio
import time
client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['db_hxz']
loop = asyncio.get_event_loop()
av = AvBrowser(loop)
def lenn(n):
    return lambda x: len(x) >= n

@av.entry("https://www.douban.com/group/haixiuzu/discussion?start=0", re.compile('.'))
async def main(result, *parent):
    pages = [("https://www.douban.com/group/haixiuzu/discussion?start={}".format(p),) for p in range(0,2500,25)]
    return pages[:20]
@av.register(re.compile('<td class="title">[\s\S]*?<a href="(.*?)" title="(.*?)" class="">'))
async def page(result, *parent):
    result = filter(lambda row: '晒' in row[1], filter(lenn(2), result))
    return result
reDetail = re.compile(r'<span class="from">来自: <a href="(.*?)">(.*?)<[\s\S]*?<div class="topic-content">([\s\S]*?)<!-- via  -->')
@av.register(reDetail)
async def detail(result, *parent):
    global db
    result = filter(lenn(3), result)
    for res in result:
        doc = {}
        doc['userhome'] = res[0]
        doc['username'] = res[1]
        doc['topictitle'] = parent[0][1]
        doc['topicurl'] = parent[0][0]
        doc['imgs'] = []
        doc['ts'] = int(time.time())
        imgs = re.findall(r'<img src="(.*?)"', res[2])
        for img in imgs:
            doc['imgs'].append(img)

        exist = await db.db_hxz.find_one({'topicurl': doc['topicurl']})
        if exist is None:
            print("INSERT ", doc)
            await db.db_hxz.insert_one(doc)
        else:
            print("Exited!")
av.run()
av.close()