# hdhr-ac4

## Description

>This project aims to emulate an HDHomerun tuner that supplies ATSC 3.0 programs with AC3 audio.

## About

>This project started as a way for me to support ATSC 3.0 programs on my home netowrk. I already have an HDHR5-4k tuner and thought the transition would be straight forward when ATSC 3.0 programs went live in Atlanta. The signal and video quality were much better, but the AC4 audio every program was using was supported by nothing I owned.

>This application pretends to be an HDHomerun device that offers ATSC 3.0 programs. When a request comes in to tune one of the programs, it forwards that request to a real HDHomerun device and passes the resulting stream back to the original requester after converting the AC4 audio stream to AC3 audio.

## Why?

>This allows my HDHR5-4K to serve ATSC 3.0 programs to my Emby server with Live TV and DVR functionality. Converting audio to AC3 before Emby receives it (or other clients) allows everything to work as it always has with HDHomerun tuners.

## Configuration 
>Currently hardcoded in the Python scripts.
>### main.py
>>- HDHR_IP - the IP address of your real HDHomerun device
>>- HOST_IP - the IP address where hdhr-ac4 is running
>>- DeviceID_swap - If the Device of the HDHomerun you are connecting to should be reversed. This ensures you have a unique DeviceID to prevent any collision with your physical HDHomerun device.

>### hd_home_run.py
>>Contains the ffmpeg command:
```
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
]
```
>>Most of the command should remain the same, but it is worth noting I had to add the "-async 5000" argument to fix the audio skipping from Atlanta's ATSC 3.0 programs. Use ffmpeg to play around with your ATSC 3.0 programs until you find something that works before changing anything here

## Build Docker Container
>Example Dockerfile build command:

>`docker build -f Dockerfile -t hdhr-ac4 .`

>This build takes a while since it builds ffmpeg from scratch.
>1. Builds ffmpeg branch with experimental AC4 support in an Ubuntu Docker container. Please note the ffmpeg source is not included in this repository, but is downloaded from here during the build: https://github.com/richardpl/FFmpeg/tree/ac4
>2. Large portions of the Dockerfiles that builds ffmpeg originated from Julien Rottenberg and where modified to suit this project: https://github.com/jrottenberg/ffmpeg Apache 2.0 License attached.
>3. An empty Ubuntu container is created and the ffmpeg binaries copied in. Python is installed and a few python modules added. The 2 python files are copied over and the launch command is set.

## Run Docker container
>Example container run command:

>`docker run -p 80:80 -p 5004:5004 hdhr-ac4`

>The HDHomerun API being implemented is here: https://info.hdhomerun.com/info/http_api 

>The container runs HTTP servers on port 80 and 5004 and supports the following HTTP requests:
>>- http://HOST:80/discover.json - returns the same response as the real HDHomerun device, but substitutes the hdhr-ac4 IP address in the appropriate locations.
>>- http://HOST:80/lineup.json - queries the real HDHomerun device for its service list and then does the following:
>>>1. replaces all the IP addresses with the hdhr-ac4 IP address
>>>2. replaces the ATSC3=1 entry with AudioCodec=AC3
>>>3. strips out all non ATSC3 programs
>>- http://HOST:5004/auto/{program} - forwards the request to the real HDHomerun device, and then pipes the stream through ffmpeg and then back to the orignal requester

## Notes
>- Please report issues or send pull requests here: https://github.com/johnb-7/hdhr-ac4
>- Channel changes are a little slower due to the extra step
>- On my setup, the conversion occasionally suffers very minor pitch changes due to the audio sync correction. Hopefully, ffmpeg will get better at AC4 decoding in the future.
>- VLC was used a lot in the early testing. Example URL for host 192.168.1.1 with program 111.1: http://192.168.1.1:5004/auto/v111.1
>- The development container (Dockerfile-dev) is very similar but does not automatically launch the application and can be mounted using your editor of choice for debugging the Python application or ffmpeg. It also installs some extra software specifically for development.
>- We have been using this for about a week watching live TV (no recordings yet) and it has proven very reliable. On a cloudy day we can watch football for hours withuot losing the signal like we would on ATSC 1.0 programs.
>- I am intentionally not distributing ffmpeg binaries with AC4 support for legal reasons. Everything is included to build them yourself.

## TODO
>- Add version and a version API
>- Strip all the unused stuff from the ffmpeg build
>- Pull configuration stuff out of Python files to a file/argument/webAPI
>- Improve the complex streaming data pipe


## License
>This project is release under the Apache 2.0 license
