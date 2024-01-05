# Setup

Launch the simple-yt-dlp-gui executable. If this is your first time running, it should ask where you have ffmpeg installed. Point it to the your ffmpeg executable. 
- On Windows, this will be inside the "bin" folder wherever you installed ffmpeg
- On Linux it's probably stored at /bin/ffmpeg

This directory will be saved inside **app_config.json** in the same directory as the simple-yt-dlp-gui executable. If anything weird happens, you can always enter the filepath manually, like this:

``` json
{"ffmpeg_directory": "D:/ffmpeg/bin/ffmpeg.exe"}
```
``` json
{"ffmpeg_directory": "/bin/ffmpeg"}
```

Use forward slashes in your filepath. If you absolutely must use backslashes, then do double backslashes like this:

``` text
D:\\ffmpeg\\bin
```

<br><br>

# Usage

You can paste one or more URLs in the text box. You should have one URL per line.

**I have only tested YouTube and Soundcloud URLs. YMMV if using other types of URLs.**

Tinker with the options (or don't) noting that they will apply to all URLs provided. When you click "Start Download" the app will ask you to select a folder where it will save your downloads. 

You can monitor progress in the command prompt window. I have future plans to integrate a console output window in the UI itself.

<br>

Here's a brief overview of the available options:

| Category | Option | Description |
|---|---|---|
| Thumbnail | No thumbnails | No thumbnails will be downloaded |
| Thumbnail | Embedded thumbnails | Thumbnails will be downloaded and embedded inside the media file |
| Thumbnail | Standalone thumbnails | Thumbnails will be downloaded and stored as a separate file alongside the media file. You can specify the format of the thumbnail with the dropdown menu |
| Video | Convert Video | If checked, it will attempt to convert your video to the format selected in the dropdown box |
| Video | Preferred quality | Selecting a specific resolution (like 1080p) will cause yt-dlp to try and grab a 1080p version. If unavailable, it will grab the next best quality option |
| Audio | Keep audio only | If checked, then only the audio will be downloaded. You can optionally select a desired format for the output  |
| Audio | Bitrate in kbps | You can specify your desired bitrate. For mp3, either VBR (0, 1, 2, etc) or CBR (128, 192, 320, etc) values are accepted |

<br><br>

# Future Features & TODOs
- Add a console output window inside of the UI to monitor progress of the downloads
- Add a separate tab to set/update your ffmpeg directory
- Add the ability to set a default download directory instead of asking every time
- Improve preferred quality selection logic
