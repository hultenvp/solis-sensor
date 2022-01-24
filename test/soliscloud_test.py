import hashlib
from hashlib import sha1
import hmac
import base64
from datetime import datetime
from datetime import timezone
import requests
import json

KeyId = "xxxxx"
secretKey = b'xxxxx'


VERB="POST"
now = datetime.now(timezone.utc)
Date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

#Body = '{"userId":"xxxxx"}'
#Body = '{"id":"xxxxx"}'
#Body = '{"stationId":"xxxxxx"}'
Body='{"id":"xxxxx","sn":"xxxxx"}'
#Body='{"userName":"xxxxx","userType":0}'

Content_MD5 = base64.b64encode(hashlib.md5(Body.encode('utf-8')).digest()).decode('utf-8')
Content_Type = "application/json"

#CanonicalizedResource = "/v1/api/userStationList"
#CanonicalizedResource = "/v1/api/stationDetail"
#CanonicalizedResource = "/v1/api/inveterList"
CanonicalizedResource = "/v1/api/inveterDetail"
#CanonicalizedResource = "/v1/api/addUser"

encryptStr = (VERB + "\n"
    + Content_MD5 + "\n"
    + Content_Type + "\n"
    + Date + "\n"
    + CanonicalizedResource)

h = hmac.new(secretKey, msg=encryptStr.encode('utf-8'), digestmod=hashlib.sha1)

Sign = base64.b64encode(h.digest())

Authorization = "API " + KeyId + ":" + Sign.decode('utf-8')

requestStr = (VERB + " " + CanonicalizedResource + "\n"
    + "Content-MD5: " + Content_MD5 + "\n"
    + "Content-Type: " + Content_Type + "\n"
    + "Date: " + Date + "\n"
    + "Authorization: "+ Authorization + "\n"
    + "Body：" + Body)

header = { "Content-MD5":Content_MD5,
            "Content-Type":Content_Type,
            "Date":Date,
            "Authorization":Authorization
            }
header1 = { "Content-Type":Content_Type,
            "Date":Date,
            "Authorization":Authorization
            }

print (requestStr)

url = 'https://www.soliscloud.com:13333'
req = url + CanonicalizedResource
x = requests.post(req, data=Body, headers=header)
print ("")
print(json.dumps(x.json(),indent=4, sort_keys=True))