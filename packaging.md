To package this up:

1. While at the root simple-yt-dlp-gui directory, run pyinstaller to package up the script
2. ~~Copy the settings.json file into the same directory as the .exe file~~ App will now create the app_config.json file if it's missing
3. Copy the README into the directory
4. Zip the whole thing up

<br>

## Windows
```powershell
# Compile package
pyinstaller ./source/yt-dlp_gui.py -F --name="simple-yt-dlp-gui" --workpath="./build" --distpath="./dist" --specpath="./spec" --icon="../icon/simple-yt-dlp-gui.ico"

# Copy README
copy-item -path "./README.md" -destination "./dist"
```
<br>

## Linux
```bash
# Compile package
pyinstaller ./source/yt-dlp_gui.py -F --name="simple-yt-dlp-gui" --workpath="./build" --distpath="./dist" --specpath="./spec"

# Copy README
cp ./README.md ./dist
```

<br><br>

| Arg           | Explanation                                       | Notes                  |
|---------------|---------------------------------------------------|------------------------|
| yt-dlp_gui.py | Script to package/compile                         |                        |
| -F            | Indicates we want a single binary as output       |                        |
| name          | Specify the name of the binary                    |                        |
| workpath      | Directory where temporary build files will go     |                        |
| distpath      | Directory the binary will be saved                |                        |
| specpath      | Directory where the generated spec files go       |                        |
| icon          | Filepath for icon that will be embedded in binary | Not supported on Linux |