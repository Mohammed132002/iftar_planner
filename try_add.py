from urllib.request import urlopen
from urllib.parse import urlencode
import json

body = urlencode({"name": "Lentil soup", "category": "Soup", "cost": "6.5"}).encode("utf-8")
with urlopen("http://127.0.0.1:5050/dishes/add", data=body, timeout=5) as reply:
    print(json.loads(reply.read().decode("utf-8")))
with urlopen("http://127.0.0.1:5050/dishes", timeout=5) as reply:
    print(json.loads(reply.read().decode("utf-8")))