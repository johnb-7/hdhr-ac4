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

# TODO: move to config file?
HDHR_IP = "192.168.1.161"
HOST_IP = "192.168.1.253"

app = FastAPI()
tune = FastAPI()
hdhr_instance = HdHomeRun(HDHR_IP)


@app.get("/discover.json")
def get_discover():
    original = hdhr_instance.discover()
    modified = original.replace(HDHR_IP, HOST_IP)
    return json.loads(modified)


@app.get("/lineup.json")
def get_lineup():
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


@tune.get("/auto/{channel}")
def in_channel(channel: str, request: Request) -> Any:
    return hdhr_instance.tune(channel, request)


if __name__ == "__main__":
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
