# hdhr-ac4 v1.5.0

## Update

> **May 2024** Added docker image to GitHub Container Registry. This can be used instead of building your own. It was built using the latest repo and "emby-server-deb_4.8.0.21_amd64.deb" for ffmpeg.

>> ### Quick start:

>> `docker run -p 80:80 -p 5004:5004 -e "HDHR_IP=192.168.1.1" -e "HOST_IP=192.168.1.2" -e "DEVICEID_SWAP=1" ghcr.io/johnb-7/hdhr-ac4:1.5`

> I have been using this with Plex DVR for quite some time. It has been rock solid and reliable. DRM has been enabled on all but one channel in Atlanta. Maybe one day DRM will be sorted out and I can get all the channels again. It was fun while it lasted.
 
## Description

>This project aims to emulate an HDHomerun tuner that supplies ATSC 3.0 programs with AC3 audio.

## About

>This project started as a way for me to support ATSC 3.0 programs on my home netowrk. I already have an HDHR5-4k tuner and thought the transition would be straight forward when ATSC 3.0 programs went live in Atlanta. The signal and video quality were much better, but the AC4 audio every program was using was supported by nothing I owned.

>This application pretends to be an HDHomerun device that offers ATSC 3.0 programs. When a request comes in to tune one of the programs, it forwards that request to a real HDHomerun device and passes the resulting stream back to the original requester after converting the AC4 audio stream to AC3 audio.

## Why?

>This allows my HDHR5-4K to serve ATSC 3.0 programs to my Emby server(now native support?) and PLEX server with Live TV and DVR functionality. Converting audio to AC3 before the server receives it allows everything to work as it always has with HDHomerun tuners.

## Configuration 
>Set in docker environent
>>- HDHR_IP - REQUIRED. The IP address of your real HDHomerun device
>>- HOST_IP - REQUIRED. The IP address where hdhr-ac4 is running
>>- DEVICEID_SWAP - OPTIONAL (1 or 0, default 0) If the Device of the HDHomerun you are connecting to should be reversed. This ensures you have a unique DeviceID to prevent any collision with your physical HDHomerun device.

>### hd_home_run.py
>>Contains the ffmpeg command:
```
[
    "/bin/usr/ffmpeg",
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
    "-",
]
```
>>This should not need to be changed, but can be modified if the ATSC 3.0 streams needs specifi ffmpeg handling.

## Build Docker Container
>Download the latest Emby installer from https://emby.media/linux-server.html and save it in the docker build directory. Update Dockerfile to point to the file. Currently using emby-server-deb_4.8.0.21_amd64.deb
>Example Dockerfile build command:

>`docker build -f Dockerfile -t hdhr-ac4 .`

>This build uses ffmpeg binary from Emby. The Emby team has a custom version of ffmpeg tha has several improvements over the original ffmpeg branch. 
>Version 1.0.0 of this docker build created the custom ffmpeg from scratch which took much longer and is a little dated at this point. 
>A quick explanation for the docker build that is based on ubuntu 20:
>1. The ffmpeg container extracts Emby installer
>2. The final container copies in ffmpeg binaries. Python is installed and a few python modules added. The 2 python files are copied over and the launch command is set.

## Run Docker container
>Example container run command:

>`docker run -p 80:80 -p 5004:5004 -e "HDHR_IP=10.1.1.2" -e "HOST_IP=10.0.0.100" -e "DEVICEID_SWAP=1" hdhr-ac4`

>The HDHomerun API being implemented is here: https://info.hdhomerun.com/info/http_api 

>The container runs HTTP servers on port 80 and 5004 and supports the following HTTP requests:
>>- http://HOST:80/ - returns info and version about hdhr-ac4 docker
>>- http://HOST:80/discover.json - returns the same response as the real HDHomerun device, but substitutes the hdhr-ac4 IP address in the appropriate locations.
>>- http://HOST:80/lineup.json - queries the real HDHomerun device for its service list and then does the following:
>>>1. replaces all the IP addresses with the hdhr-ac4 IP address
>>>2. strips out all non ATSC3 programs
>>- http://HOST:5004/auto/{program} - forwards the request to the real HDHomerun device, and then pipes the stream through ffmpeg and then back to the orignal requester
>>- http://HOST:80/lineup_status.json - returns the same response as the real HDHomerun device

## Notes
>- Please report issues or send pull requests here: https://github.com/johnb-7/hdhr-ac4
>- Channel changes are a little slower due to the extra step
>- VLC was used a lot in the early testing. Example URL for host 192.168.1.1 with program 111.1: http://192.168.1.1:5004/auto/v111.1
>- The development container (Dockerfile-dev) is very similar but does not automatically launch the application and can be mounted using your editor of choice for debugging the Python application or ffmpeg. It also installs some extra software specifically for development.
>- Many thanks to the Emby team for the ffmpeg with working AC4. Since its open source software, there should not be any problems here.


## License
>This project is release under the Apache 2.0 license
