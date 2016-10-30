from flask import Flask
import time
app = Flask(__name__)

@app.route("/<string:word>")
@app.route("/")
def hello(word=""):
    t = len(word) / 10
    time.sleep(t)
    return "Word: `{}` cost {}s to process!".format(word, t)

if __name__ == "__main__":
    app.run()