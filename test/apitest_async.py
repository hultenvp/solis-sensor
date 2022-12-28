import sys
import hashlib
from hashlib import sha1
import hmac
import base64
from datetime import datetime
from datetime import timezone
import requests
import json
import asyncio
import aiohttp
from soliscloud_api.soliscloud_api import *

DELAY = 1 #seconds

# Provided by Solis Support
KeyId = "YOUR KEY GOES HERE"
secretKey = b'YOUR KEY GOES HERE'

async def details_per_station(api, station_ids):
    for sid in station_ids:
        try:
            await asyncio.sleep(DELAY)
            response = await api.station_detail(KeyId, secretKey, station_id=sid)
            print("station_detail(station_id=",sid,"): [OK]")
            if verbose: print(json.dumps(response,sort_keys=True))
            await asyncio.sleep(DELAY)
        except SoliscloudAPI.SolisCloudError as err:
            print("station_detail(station_id=",sid,"): Failed with:",err)

async def collector_details_per_station(api, station_ids):
    for sid in station_ids:
        try:
            response = await api.collector_list(KeyId, secretKey, station_id=sid)
            if verbose: print(json.dumps(response,sort_keys=True))
            if response is not None:
                print("collector_list(station_id=",sid,"): [OK]")
                for record in response:
                    await asyncio.sleep(DELAY)
                    try:
                        response = await api.collector_detail(KeyId, secretKey, collector_sn=record["sn"])
                        if response is not None:
                            print("collector_detail(station_id=",sid,", collector_sn=",record["sn"],"): [OK]")
                            if verbose: print(json.dumps(response,sort_keys=True))
                    except SoliscloudAPI.SolisCloudError as err:
                        print("collector_detail(station_id=",sid,", collector_sn=",record["sn"],"):  Failed with:",err)
        except SoliscloudAPI.SolisCloudError as err:
            print("collector_list(",sid,"): Failed with:",err)

async def inverter_details_per_station(api, station_ids):
    for sid in station_ids:
        try:
            await asyncio.sleep(DELAY)
            response = await api.inverter_list(KeyId, secretKey, station_id=sid)
            if response is not None:
                print("inverter_list(",sid,"): [OK]")
                if verbose: print(json.dumps(response,sort_keys=True))
                for record in response:
                    await asyncio.sleep(DELAY)
                    try:
                        response = await api.inverter_detail(KeyId, secretKey, inverter_sn=record["sn"])
                        if response is not None:
                            print("inverter_detail(station_id =",sid,", inverter_sn =",record["sn"],"): [OK]")
                            if verbose: print(json.dumps(response,sort_keys=True))
                    except SoliscloudAPI.SolisCloudError as err:
                        print("inverter_detail(station_id=",sid,", inverter_sn=",record["sn"],"):  Failed with:",err)
        except SoliscloudAPI.SolisCloudError as err:
            print("inverter_list(station_id =",sid,"): Failed with:",err)

async def station_graphs(api, station_ids):
    for sid in station_ids:
        try:
            await asyncio.sleep(DELAY)
            response = await api.station_day(KeyId, secretKey, currency="EUR", time="2022-12-27", time_zone=1, station_id=sid)
            if response is not None:
                print("station_day(",sid,"): [OK]")
                if verbose: print(json.dumps(response,sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("inverter_list(station_id =",sid,"): Failed with:",err)
        try:
            response = await api.station_month(KeyId, secretKey, currency="EUR", month="2022-12", station_id=sid)
            if response is not None:
                print("station_month(",sid,"): [OK]")
                if verbose: print(json.dumps(response,sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("inverter_list(station_id =",sid,"): Failed with:",err)
        try:
            response = await api.station_year(KeyId, secretKey, currency="EUR", year="2022", station_id=sid)
            if response is not None:
                print("station_year(",sid,"): [OK]")
                if verbose: print(json.dumps(response,sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("inverter_list(station_id =",sid,"): Failed with:",err)
        try:
            response = await api.station_all(KeyId, secretKey, currency="EUR", station_id=sid)
            if response is not None:
                print("station_all(",sid,"): [OK]")
                if verbose: print(json.dumps(response,sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("inverter_list(station_id =",sid,"): Failed with:",err)

async def call_solis(api):
    response = await api.user_station_list(KeyId, secretKey)
    if response is not None:
        print("user_station_list: [OK]")
        if verbose: print(json.dumps(response,sort_keys=True))
    station_ids = [record["id"] for record in response]
    await details_per_station(api, station_ids)
    await collector_details_per_station(api, station_ids)
    await station_graphs(api, station_ids)

async def main():
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        api = SoliscloudAPI('https://www.soliscloud.com:13333', session)
        cwlist = [loop.create_task(call_solis(api)) for i in range(1)]
        responses = await asyncio.gather(*cwlist, return_exceptions=True)

        print("Exceptions: ",responses)

verbose = False
if len(sys.argv) > 1 and (sys.argv[1] == '--verbose' or sys.argv[1] == '-v'):
    print("Verbose")
    verbose = True
asyncio.run(main())
