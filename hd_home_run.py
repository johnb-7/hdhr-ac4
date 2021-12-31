"""Class to represent a HD Home Run device on the network"""
import requests
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from subprocess import Popen, PIPE
from requests import Response
from threading import Thread
from time import sleep


def stream_requests_to_ffmpeg(response: Response, ffmpeg: Popen):
    try:
        for data in response.iter_content(chunk_size=1024 * 128):
            if ffmpeg.poll() != None:
                break
            written = ffmpeg.stdin.write(data)
            if written <= 0:
                break
            # sleep(0.01)
    except:
        pass


async def stream_ffmpeg_to_response(ffmpeg: Popen, feeder: Thread, request: Request):
    while 1:
        try:
            data = ffmpeg.stdout.read(1024 * 128)
            if (
                len(data) <= 0
                or not feeder.is_alive()
                or await request.is_disconnected()
            ):
                break
            yield data
            # sleep(0.01)
        except:
            break
    await request.close()
    ffmpeg.kill()


class HdHomeRun:
    _base_url: str

    def __init__(self, ip: str) -> None:
        """Init the class with the device IP"""
        self._base_url = "http://" + ip

    def discover(self) -> str:
        """Gets the hd home run info"""
        return requests.get(self._base_url + "/discover.json").text

    def lineup(self) -> str:
        """Gets the hd home run channel list"""
        return requests.get(self._base_url + "/lineup.json").text

    def lineup_status(self) -> str:
        """Gets the hd home run status"""
        return requests.get(self._base_url + "/lineup_status.json").text

    def tune(self, channel: str, stream_out: Request) -> None:
        """Streams channel from hdhr until device disconnects"""
        stream_in = requests.get(self._base_url + ":5004/auto/" + channel, stream=True)
        if stream_in.status_code == 200:
            ffmpeg = Popen(
                [
                    "ffmpeg",
                    "-nostats",
                    "-hide_banner",
                    "-loglevel",
                    "warning",
                    "-i",
                    "pipe:",
                    "-c:a",
                    "ac3",
                    "-c:v",
                    "copy",
                    "-f",
                    "mpegts",
                    "-async",
                    "5000",
                    "-",
                ],
                stdout=PIPE,
                stdin=PIPE,
            )
            feeder = Thread(target=stream_requests_to_ffmpeg, args=(stream_in, ffmpeg))
            feeder.start()
            return StreamingResponse(
                stream_ffmpeg_to_response(ffmpeg, feeder, stream_out),
                headers=stream_in.headers,
            )
        else:
            stream_in.close()
            del stream_in.headers["Content-Length"]
            raise HTTPException(
                status_code=stream_in.status_code, headers=stream_in.headers
            )
