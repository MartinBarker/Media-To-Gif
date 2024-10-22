Forked from https://github.com/LindseyB/starwars-dot-gif

Run with linux:
`python make_gifs.py `

To generate a gif for every movie/srt file combo. 

### Setup Python3 virtualenv on linux:
`pip install virtualenv`

`python3 -m virtualenv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`pip install pysrt`

`pip install imageio`

`pip install pillow==9.5.0`

Once finished, leave virtualenv by running command: `deactivate`

### Create single gif:
`python3 make_gifs.py`

----------------------------------------------

#to run locally:
1. Setup auth values in config.cfg file
2. Source Python virtual env and run 
```
$ source .env/bin/activate
(.env) $ python3 twitter_bot.py
```

#run "sudo apt install graphicsmagick-imagemagick-compat" before

sudo apt install imagemagick-6.q16                  # version 8:6.9.10.23+dfsg-2.1ubuntu11.2, or
sudo apt install imagemagick-6.q16hdri              # version 8:6.9.10.23+dfsg-2.1ubuntu11.2
sudo apt install graphicsmagick-imagemagick-compat  # version 1.4+really1.3.35-1







##########################

# Star Wars DOT Gif

## Quickstart

### Setup

Copy the contents of ```config.cfg.example``` into ```config.cfg``` and make sure to change the relevant paths for VLC or ffmpeg and the Star Wars episodes. Any format that can be read by VLC or ffmpeg should be acceptable for the movies. Note, if you don't plan on running the twitter bot you only need to fill out the general section of the cfg file.

Install python requirements:

```bash
pip install -r requirements.txt
```

Verify you have either vlc or ffmpeg installed (we just need one of both):

```bash
$ whereis vlc
vlc: /usr/bin/vlc /usr/lib64/vlc /usr/share/vlc /usr/share/man/man1/vlc.1.gz
$ whereis ffmpeg
ffmpeg: /usr/bin/ffmpeg /usr/share/ffmpeg /usr/share/man/man1/ffmpeg.1.gz
```

### Usage

#### To Run with search UI [(sample run)](http://www.youtube.com/watch?v=n387eBqnw1o)

By default the gif is created as **star_wars.gif**

```bash
python star_wars_gif.py
```

#### To get a random gif

```bash
python make_gifs.py
```

### Embedding in another python-script

If you want to use ```make_gifs``` elsewhere use:

```python
from make_gifs import make_gif
# source should be a slug from config.cfg
# index is the index of the quote in the SRT
# for more options see make_gifs.py
make_gif(source, index)
```

### Running the twitter bot

- make sure you create API accounts for both twitter and imgur
- update **config.cfg** to have the keys for both
- run ```python twitter_bot.py```

The bot will tweet once every hour.

### Notes

- if you know what a [virtualenv](https://virtualenv.pypa.io/en/stable/userguide/) is, we recommend you use one
- for more options on creating gifs, please read the [embbeded documentation](make_gifs.py)

## In detail

It is assumed you have [virtualenv](https://virtualenv.pypa.io/en/stable/installation/) installed. If not, it is not very difficult to install or use and will keep your system-python free of fancy packages we are using here.

### Requirements

- python (tested with 2.7 and 3.6)
- ffmpeg or vlc
- video-files for movies/videos you want to extract from

### Setup Procedure

Create a virtalenv and install python requirements:

```bash
cd starwars-dot-gif
virtualenv .env
source .env/bin/activate
(.env)$ pip install -r requirements.txt
```

Now copy the example config provided and edit with your favourite editor:

```bash
cp config.cfg.example config.cfg
vim config.cfg
```

You must set a path for vlc or ffmpeg, if both are set, ffmpeg will be preferred over vlc. Setting 'vlc' or 'ffmpeg' instead of a path is acceptable if those are executable as-is on your system.

The repository currently includes subtitles for Star Wars episode IV to VIII, you are free to add more video-files with corresponding subtitles (see [config.cfg.example](config.cfg.example)). It is recommended that you remove any entires which you do not want to use from the videos-list in the config.

To test the configuration you may run the script with the ```--help```-option, which will give you an extensive explanation of options.

```bash
(.env)$ python make_gifs.py --help
usage: make_gifs.py [-h] [--movie [MOVIE [MOVIE ...]]] [--index [INDEX]]
...
```

### Detailed Usage

You may use the script with your config.cfg either with an interactive [commandline-tool](star_wars_gif.py) or directly pass options on the commandline.

#### Commandline-tool

The commandline-tool has a GUI of sorts and allows you to search in the subtitles. This allows you to look for specific words or quotes you are looking for.

```bash
(.env)$ python star_wars_gif.py
```

This script will ignore any arguments passed to it.

#### Direct

The direct method can be called from the commandline or from another python script. These options are nearly equally powerful. Using the commandline you may pass any number of options (call with ```--help``` to see all of them).

The following command will create a gif with the quote "Aren't you a little short for a stormtrooper?".

```bash
(.env)$ python make_gifs.py --movie hope --index 848
```

Now adding some options:

```bash
(.env)$ python make_gifs.py --movie hope --index 848 --padding 0 0.6 --subtitle "I have been expecting you"
```

This added 0.6 seconds (and a confused Luke) to the end of the gif and changed the rendered subtitle to "I have been expecting you". As previously mentioned there are many more options available.

When called from python usage follows a general pattern:

```python
from make_gifs import make_gif
# source should be a slug from config.cfg
# index is the index of the SRT
# for more options see make_gifs.py
make_gif('hope', 848, padding=[0, 0.6], custom_subtitle="I have been expecting you", filename="say_what.gif")
```

This example will reproduce the above shell example and save it as "say_what.gif". Feel free to try this example in [ipython](http://ipython.readthedocs.io/en/stable/).
