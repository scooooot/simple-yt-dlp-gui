To package this up:

1. Run pyinstaller to package up the script
2. ~~Copy the settings.json file into the same directory as the .exe file~~ App will now create the app_config.json file if it's missing
3. Copy the README into the directory
4. Zip the whole thing up

pyinstaller yt-dlp_gui.py -F --distpath="D:/yt-dlp/app" --icon="B:/python_venvs/yt-dlp/icon/simple-yt-dlp.ico"   


| Arg           | Explanation                                       |
|---------------|---------------------------------------------------|
| pyinstaller   |                                                   |
| yt-dlp_gui.py | Name of the script to package                     |
| -F            | Indicates we want a single binary as output       |
| distpath      | Directory the binary will be saved                |
| icon          | Filepath for icon that will be embedded in binary |