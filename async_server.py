from sanic import Sanic
from sanic.response import text
from asyncio import sleep
app = Sanic(__name__)

@app.route("/<word>")
@app.route("/")
async def index(req, word=""):
    await sleep(len(word)/10)
    return text("Hello {}".format(word))

app.run()