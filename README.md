# Takes movie file and subtitles file as input
# Run script to go through movie and turn every 5 seconds into a gif, if the 5 seconds includes a quote, generate a gif of that full quote instead, and overlay subtitles onto the gif.
# Downsample, resize, change colors and framerate of gif to make it as close to 4mb as possible.
# Save gif with filename formatted like so: `${mediaName}-Start[${startTime}]-End[${endTime}]-Quote[${quote}].gif` where the vars are like so:
    mediaName: Name of movie/Tv show, ex: '28 days later'
    startTime: Start time formatted like so: hh-mm-ss
    endTime: End time formatted like so: hh-mm-ss
    quote: quote (if any) on the screen, max 30 characters, sanitized to be only text no other chars then a-z and 0-9.


## Setup Instructions

### Installing ffmpeg
The script requires `ffmpeg` to be installed on your system. Follow the instructions below to install `ffmpeg`:

#### macOS
1. Install `Homebrew` if you haven't already:
    ```sh
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2. Install `ffmpeg` using `Homebrew`:
    ```sh
    brew install ffmpeg
    ```

#### Linux
1. Install `ffmpeg` using your package manager. For example, on Ubuntu:
    ```sh
    sudo apt update
    sudo apt install ffmpeg
    ```

#### Windows
1. Download the `ffmpeg` release from the official website: https://ffmpeg.org/download.html
2. Extract the downloaded archive to a folder.
3. Add the `bin` folder from the extracted archive to your system's PATH environment variable.

### Setting up a Python Virtual Environment

#### macOS/Linux
1. Open a terminal.
2. Navigate to the project directory:
    ```sh
    cd /path/to/Media-To-Gif
    ```
3. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```
5. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

#### Windows
1. Open Command Prompt or PowerShell.
2. Navigate to the project directory:
    ```sh
    cd C:\path\to\Media-To-Gif
    ```
3. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
4. Activate the virtual environment:
    ```sh
    .\venv\Scripts\activate
    ```
5. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Script
1. Ensure the virtual environment is activated.
2. Run the script with the required arguments:
    ```sh
    python make_gifs.py --movie /path/to/movie.mp4 --subtitles /path/to/subtitles.srt --output /mnt/x/28dayslatergifs --interval 5 --startTime 01:22:23
    ```
Example:
```
python make_gifs.py --movie "media/28 Days Later (2002)/28.Days.Later.2002.720p.mp4" --subtitles "media/28 Days Later (2002)/28.Days.Later.2002.Subtitles.srt" --output /mnt/x/28dayslatergifs --interval 5 --startTime 01:22:23 --maxFilesize 15mb
```

The script will generate GIFs and save them in the specified output folder.