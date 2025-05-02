import asyncio
import base64
import hashlib
import hmac
import json
import sys
from datetime import datetime, timezone
from hashlib import sha1

import aiohttp
import requests
from soliscloud_api.soliscloud_api import *

DELAY = 1  # seconds

plant_ids = None
inverter_ids = {}
# Provided by Solis Support
KeyId = "XXXXXXXXXXXXXX"
secretKey = b"YYYYYYYYYYYY"
# plant_ids = [1234567891234567891] # 19-digit value, separate multiple ID's with a comma ([ID1, ID2, ID3])


async def details_per_station(api, station_ids):
    for sid in station_ids:
        try:
            await asyncio.sleep(DELAY)
            response = await api.station_detail(KeyId, secretKey, station_id=sid)
            print("station_detail(station_id=", sid, "): [OK]")
            if verbose:
                print(json.dumps(response, sort_keys=True))
            await asyncio.sleep(DELAY)
        except SoliscloudAPI.SolisCloudError as err:
            print("station_detail(station_id=", sid, "): Failed with:", err)


async def collector_details_per_station(api, station_ids):
    for sid in station_ids:
        try:
            response = await api.collector_list(KeyId, secretKey, station_id=sid)
            if verbose:
                print(json.dumps(response, sort_keys=True))
            if response is not None:
                print("collector_list(station_id=", sid, "): [OK]")
                for record in response:
                    await asyncio.sleep(DELAY)
                    try:
                        response = await api.collector_detail(KeyId, secretKey, collector_sn=record["sn"])
                        if response is not None:
                            print(
                                "collector_detail(station_id=",
                                sid,
                                ", collector_sn=",
                                record["sn"],
                                "): [OK]",
                            )
                            if verbose:
                                print(json.dumps(response, sort_keys=True))
                    except SoliscloudAPI.SolisCloudError as err:
                        print(
                            "collector_detail(station_id=",
                            sid,
                            ", collector_sn=",
                            record["sn"],
                            "):  Failed with:",
                            err,
                        )
        except SoliscloudAPI.SolisCloudError as err:
            print("collector_list(", sid, "): Failed with:", err)


async def inverter_details_per_station(api, station_ids):
    global inverter_ids
    for sid in station_ids:
        inverter_ids[sid] = []
        try:
            await asyncio.sleep(DELAY)
            response = await api.inverter_list(KeyId, secretKey, station_id=sid)
            if response is not None:
                print("inverter_list(", sid, "): [OK]")
                if verbose:
                    print(json.dumps(response, sort_keys=True))
                for record in response:
                    await asyncio.sleep(DELAY)
                    try:
                        inverter_ids[sid].append(record["sn"])
                        response = await api.inverter_detail(KeyId, secretKey, inverter_sn=record["sn"])
                        if response is not None:
                            print(
                                "inverter_detail(station_id =",
                                sid,
                                ", inverter_sn =",
                                record["sn"],
                                "): [OK]",
                            )
                            if verbose:
                                print(json.dumps(response, sort_keys=True))
                    except SoliscloudAPI.SolisCloudError as err:
                        print(
                            "inverter_detail(station_id=",
                            sid,
                            ", inverter_sn=",
                            record["sn"],
                            "):  Failed with:",
                            err,
                        )
        except SoliscloudAPI.SolisCloudError as err:
            print("inverter_list(station_id =", sid, "): Failed with:", err)


async def station_graphs(api, station_ids):
    for sid in station_ids:
        try:
            await asyncio.sleep(DELAY)
            response = await api.station_day(
                KeyId,
                secretKey,
                currency="EUR",
                time="2022-12-27",
                time_zone=1,
                station_id=sid,
            )
            if response is not None:
                print("station_day(", sid, "): [OK]")
                if verbose:
                    print(json.dumps(response, sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("station_day(station_id =", sid, "): Failed with:", err)
        try:
            response = await api.station_month(KeyId, secretKey, currency="EUR", month="2022-12", station_id=sid)
            if response is not None:
                print("station_month(", sid, "): [OK]")
                if verbose:
                    print(json.dumps(response, sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("station_month(station_id =", sid, "): Failed with:", err)
        try:
            response = await api.station_year(KeyId, secretKey, currency="EUR", year="2022", station_id=sid)
            if response is not None:
                print("station_year(", sid, "): [OK]")
                if verbose:
                    print(json.dumps(response, sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("station_year(station_id =", sid, "): Failed with:", err)
        try:
            response = await api.station_all(KeyId, secretKey, currency="EUR", station_id=sid)
            if response is not None:
                print("station_all(", sid, "): [OK]")
                if verbose:
                    print(json.dumps(response, sort_keys=True))
        except SoliscloudAPI.SolisCloudError as err:
            print("station_all(station_id =", sid, "): Failed with:", err)


async def inverter_graphs(api, station_ids):
    for sid in station_ids:
        for isn in inverter_ids[sid]:
            try:
                await asyncio.sleep(DELAY)
                response = await api.inverter_day(
                    KeyId,
                    secretKey,
                    currency="EUR",
                    time="2022-12-27",
                    time_zone=1,
                    inverter_sn=isn,
                )
                if response is not None:
                    print("inverter_day(", isn, "): [OK]")
                    if verbose:
                        print(json.dumps(response, sort_keys=True))
            except SoliscloudAPI.SolisCloudError as err:
                print("inverter_day(inverter_id =", isn, "): Failed with:", err)
            try:
                await asyncio.sleep(DELAY)
                response = await api.inverter_month(KeyId, secretKey, currency="EUR", month="2022-12", inverter_sn=isn)
                if response is not None:
                    print("inverter_month(", isn, "): [OK]")
                    if verbose:
                        print(json.dumps(response, sort_keys=True))
            except SoliscloudAPI.SolisCloudError as err:
                print("inverter_month(inverter_id =", isn, "): Failed with:", err)
            try:
                await asyncio.sleep(DELAY)
                response = await api.inverter_year(KeyId, secretKey, currency="EUR", year="2022", inverter_sn=isn)
                if response is not None:
                    print("inverter_year(", isn, "): [OK]")
                    if verbose:
                        print(json.dumps(response, sort_keys=True))
            except SoliscloudAPI.SolisCloudError as err:
                print("inverter_year(inverter_id =", isn, "): Failed with:", err)
            try:
                await asyncio.sleep(DELAY)
                response = await api.inverter_all(KeyId, secretKey, currency="EUR", inverter_sn=isn)
                if response is not None:
                    print("inverter_all(", isn, "): [OK]")
                    if verbose:
                        print(json.dumps(response, sort_keys=True))
            except SoliscloudAPI.SolisCloudError as err:
                print("inverter_all(inverter_id =", isn, "): Failed with:", err)


async def call_solis(api):
    global plant_ids
    if plant_ids is None:
        try:
            response = await api.user_station_list(KeyId, secretKey)
            if response is not None:
                print("user_station_list: [OK]")
                if verbose:
                    print(json.dumps(response, sort_keys=True))
                plant_ids = [int(record["id"]) for record in response]
                print(plant_ids)
        except SoliscloudAPI.SolisCloudError as err:
            print("user_station_list(): Failed with:", err)
            print("Falling back to station_detail_list")
            try:
                response = await api.station_detail_list(KeyId, secretKey)
                if response is not None:
                    print("station_detail_list: [OK]")
                    if verbose:
                        print(json.dumps(response, sort_keys=True))
                    plant_ids = [record["id"] for record in response]
            except SoliscloudAPI.SolisCloudError as err:
                print("station_detail_list(): Failed with:", err)
    else:
        print("Using predefined station list")
    if plant_ids is None:
        print("Cannot retrieve station ID's, giving up")
        return
    await details_per_station(api, plant_ids)
    await collector_details_per_station(api, plant_ids)
    await inverter_details_per_station(api, plant_ids)
    await station_graphs(api, plant_ids)
    await inverter_graphs(api, plant_ids)


async def main():
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        api = SoliscloudAPI("https://www.soliscloud.com:13333", session)
        cwlist = [loop.create_task(call_solis(api)) for i in range(1)]
        responses = await asyncio.gather(*cwlist, return_exceptions=True)

        print("Exceptions: ", responses)


verbose = False
if len(sys.argv) > 1 and (sys.argv[1] == "--verbose" or sys.argv[1] == "-v"):
    print("Verbose")
    verbose = True
asyncio.run(main())
