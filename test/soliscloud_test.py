import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from hashlib import sha1

import requests

# Provided by Solis Support
KeyId = "xxxxx"
secretKey = b"xxxxx"

VERB = "POST"
now = datetime.now(timezone.utc)
Date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
# Date = "Mon, 24 Jan 2022 11:32:43 GMT"
# Date2 = now.strftime("%Y-%m-%d")
Date2 = "2022-02-14"

# Un comment the next block in pairs
# need matching CanonicalizedResource and Body

# CanonicalizedResource = "/v1/api/userStationList"
# Body = '{"userId":"xxxxx"}' # userId = id number from the url bar of your inverter detail page

# CanonicalizedResource = "/v1/api/stationDetail"
# Body = '{"id":"xxxxx"}'  # id = id number from the url bar of your station overview

# CanonicalizedResource = "/v1/api/inveterList"
# Body = '{"stationId":"xxxxxx"}'  # id = id number from the url bar of your station overview

CanonicalizedResource = "/v1/api/inveterDetail"
Body = '{"id":"xxxxx","sn":"xxxxx"}'  # userId = id number from the url bar of your inverter detail page; sn = the serial number of your inverter

# CanonicalizedResource = "/v1/api/stationDayEnergyList"
# Body = '{"time":"' + Date2 +'"}'

# CanonicalizedResource = "/v1/api/stationDay"
# Body = '{"id":"xxxxx","money":"GBP","timezone":0,"time":"' + Date2 +'"}'  # id = id number from the url bar of your station overview

# CanonicalizedResource = "/v1/api/stationAll"
# Body = '{"id":"xxxxx","money":"GBP"}' # id = id number from the url bar of your station overview

# CanonicalizedResource = "/v1/api/addUser"
# Body='{"userName":"xxxxx","userType":0}' # Username field from https://www.soliscloud.com/#/my

Content_MD5 = base64.b64encode(hashlib.md5(Body.encode("utf-8")).digest()).decode("utf-8")
# Content_MD5 = ""
Content_Type = "application/json"

encryptStr = VERB + "\n" + Content_MD5 + "\n" + Content_Type + "\n" + Date + "\n" + CanonicalizedResource

h = hmac.new(secretKey, msg=encryptStr.encode("utf-8"), digestmod=hashlib.sha1)

Sign = base64.b64encode(h.digest())

Authorization = "API " + KeyId + ":" + Sign.decode("utf-8")

requestStr = (
    VERB
    + " "
    + CanonicalizedResource
    + "\n"
    + "Content-MD5: "
    + Content_MD5
    + "\n"
    + "Content-Type: "
    + Content_Type
    + "\n"
    + "Date: "
    + Date
    + "\n"
    + "Authorization: "
    + Authorization
    + "\n"
    + "Body："
    + Body
)

header = {
    "Content-MD5": Content_MD5,
    "Content-Type": Content_Type,
    "Date": Date,
    "Authorization": Authorization,
}

# print (requestStr)
# print (header)

url = "https://www.soliscloud.com:13333"
req = url + CanonicalizedResource
x = requests.post(req, data=Body, headers=header)
print("")
# output the response
# print(json.dumps(x.json(),indent=4, sort_keys=True)) # Most Human Readable with alpha sorted keys
# print(json.dumps(x.json(),indent=4, sort_keys=False)) # Most Human Readable with unsorted keys
print(json.dumps(x.json(), sort_keys=True))  # Most Compact but still sorted - Probably the best for posting to github.
# print(x.json()) # Raw JSON - also good for posting to github.
