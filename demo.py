import requests as req
import time

URL = "http://127.0.0.1:8000/{}"
words = ["Hello", "Python", "!"]

start = time.perf_counter()

for word in words:
    t1 = time.perf_counter()
    resp = req.get(URL.format(word))
    # resp = req.get("http://douban.com/")
    t2 = time.perf_counter()
    print(resp.text)
    # print("Request Cost: {}\n\n".format(t2-t1))

end = time.perf_counter()

print("Total time: {}".format(end-start))
