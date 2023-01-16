>1.5.0
>- major docker build update uses Emby pre-built ffmpeg binaries with excellent AC4 support
>- removed async argument no longer needed with Emby ffmpeg
>- updated modules to latest versions
>- added multiple workers to uvicorn for faster tune time and better handling of multiple tunes
>- configuration is now done through docker environment variables
>- added info API that also reports version
>- documentation update


>1.0.0
>- initial release
>- hdhr proxy that supplies ATSC 3.0 channels and supports streaming them with audio re-encoded to AC3
>- docker build does full compile of ffmprg ac4 branch
>- special thanks to gunsuka for adding lineup_status.json API and DeviceID_swap
>- tested on Emby and Plex
