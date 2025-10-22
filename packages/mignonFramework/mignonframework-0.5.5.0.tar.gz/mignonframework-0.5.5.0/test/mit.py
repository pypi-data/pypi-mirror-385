import json

import requests

print(requests.post(url='http://127.0.0.1:12340/info/123',
                    json={'data': 'hello world'}
                    ).text)


print(requests.get(
    url='http://127.0.0.1:12340/test?data=123',
).text)