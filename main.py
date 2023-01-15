"""main file tha launches fastapi and created hdhr instance"""
from typing import Any, List
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from hd_home_run import HdHomeRun
from threading import Thread
import uvicorn
from pydantic import BaseModel
import json
import re

# TODO: move to config file?
# You must configure tese two parameters for your network
HDHR_IP = "192.168.1.161"
HOST_IP = "192.168.1.253"

# These config options are optionl
# Set to 1 to reverse the DeviceID of the original HDHR.
# This is needed for some systems like PLEX that track the DeviceID
DeviceID_swap = 0

# End config options, changes below this line are not required

app = FastAPI()
tune = FastAPI()
hdhr_instance = HdHomeRun(HDHR_IP)


@app.get("/discover.json")
async def get_discover():
    original = hdhr_instance.discover()
    modified = original.replace(HDHR_IP, HOST_IP)

    if DeviceID_swap:
        DID_search = re.search(r'"DeviceID":"([A-F0-9]+)"', modified)
        if DID_search:
             modified = re.sub(r'"DeviceID":"([A-F0-9]+)"',r'"DeviceID":"'+DID_search.group(1)[::-1]+'"', modified)
    return json.loads(modified)


@app.get("/lineup.json")
async def get_lineup():
    original_txt = hdhr_instance.lineup()
    modified_txt = original_txt.replace(HDHR_IP, HOST_IP).replace(
        '"ATSC3":1', '"AudioCodec":"AC3"'
    )
    original_json = json.loads(modified_txt)
    modified_json = []
    for entry in original_json:
        if "VideoCodec" in entry and entry["VideoCodec"] == "HEVC":
            print(entry)
            modified_json.append(entry)
    return modified_json

@app.get("/lineup_status.json")
async def get_lineup_status():
    original_json = hdhr_instance.lineup_status()
    return json.loads(original_json)

@tune.get("/auto/{channel}")
async def in_channel(channel: str, request: Request) -> Any:
    return hdhr_instance.tune(channel, request)


if __name__ == "__main__":
    # only for dev, prod runs through uvicorn command line 
    app_thread = Thread(
        target=uvicorn.run, kwargs={"app": app, "port": 80, "host": "0.0.0.0"}
    )
    tune_thread = Thread(
        target=uvicorn.run, kwargs={"app": tune, "port": 5004, "host": "0.0.0.0"}
    )
    app_thread.start()
    tune_thread.start()
    app_thread.join()
    tune_thread.join()
