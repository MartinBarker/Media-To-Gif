#!env python

import ast
import argparse
import imageio
import random
import re
import os
import pysrt
import subprocess
import configparser    
import time
import tempfile
import ffmpeg
import os
import time
import subprocess
import pysrt
from PIL import Image, ImageDraw, ImageFont
import imageio
from numpy import array
from numpy import array
from PIL import Image, ImageFont, ImageDraw

# defaults

PALLETSIZE = 256  # number of colors used in the gif, rounded to a power of two
WIDTH = 1280  # of the exports/gif, aspect ratio 2.35:1
HEIGHT = 536  # of the exports/gif, aspect ratio 2.35:1
FRAME_DURATION = 0.1  # how long a frame/image is displayed
PADDING = [0]  # seconds to widen the capture-window
DITHER = 2  # only every <dither> image will be used to generate the gif
FRAMES = 0  # how many frames to export, 0 means as many as are available
SCREENCAP_PATH = os.path.join(os.path.dirname(__file__), "screencaps")
FONT_PATH = "fonts/DejaVuSansCondensed-BoldOblique.ttf"
FONT_SIZE = 16

# Add ffmpeg_path as a global variable
ffmpeg_path = "ffmpeg"  # Assuming ffmpeg is in the system PATH

def movie_sanity_check(movie):
    # see if video_path is set
    if 'movie_path' not in movie or not os.path.exists(movie['movie_path']):
        print('Movie \'{}\' has no readable video_path set'.format(
            movie['title'] if 'title' in movie else 'unknown'))
        return False

    if 'subtitle_path' not in movie or not os.path.exists(
            movie['subtitle_path']):
        candidate = movie['movie_path'][:-3] + "srt"
        if os.path.exists(candidate):
            movie['subtitle_path'] = candidate
            return movie

        candidate = movie['movie_path'][:-3] + "eng.srt"
        if os.path.exists(candidate):
            movie['subtitle_path'] = candidate
            return movie
        return False

    return movie


def get_movie_by_slug(slug, movies):
    for movie in movies:
        if (movie['slug'] == slug):
            return movie
    print('movie with slug "{}" not found in config.'.format(slug))
    exit(1)


def striptags(data):
    #  I'm a bad person, don't ever do this.
    #  Only okay, because of how basic the tags are.
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def draw_text(draw, image_width, image_height, text, font):
    """Draws text within the image bounds."""
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Ensure the text always fits within the image width
    x = max(0, min((image_width - text_width) // 2, image_width - text_width))
    # Position text at the bottom of the image but above the lower edge with a margin
    y = image_height - text_height - 20  # Add a margin of 20 pixels
    
    # Draw shadow for better visibility
    draw.text((x-1, y), text, font=font, fill="black")
    draw.text((x+1, y), text, font=font, fill="black")
    draw.text((x, y-1), text, font=font, fill="black")
    draw.text((x, y+1), text, font=font, fill="black")
    # Draw the main text
    draw.text((x, y), text, font=font, fill="white")


def getDetails():
    # Get location of video file and subtitles
    seriesLocation = "/mnt/f/sopranos/The Sopranos - The Complete Series (Season 1, 2, 3, 4, 5 & 6) + Extras/"
    randomSeason = random.choice(os.listdir(seriesLocation))
    
    #print("getEpisode randomSeason = ", randomSeason)
    randomSeasonLocation = seriesLocation + randomSeason
    #print("getEpisode randomSeasonLocation = ", randomSeasonLocation)
    randomEpisode = random.choice(os.listdir(randomSeasonLocation))
    #print("getEpisode randomEpisode = ", randomEpisode)
    randomEpisodeLocation = randomSeasonLocation + "/" + randomEpisode
    #print("getEpisode randomEpisodeLocation = ", randomEpisodeLocation)
    subsLocation = "/mnt/f/sopranos/The Sopranos Subtitles/" + randomSeason + "/" + os.path.splitext(randomEpisode)[0] + ".srt"
    #print("getEpisode subsLocation = ", subsLocation)

    d = dict()
    d['subsLocation'] = subsLocation
    d['vidLocation'] = randomEpisodeLocation
    d['vidName'] = os.path.splitext(randomEpisode)[0]
    return d
    # Create gif
    #gifFilename = "sopranos_gif_" + str(uuid.uuid4()) + ".gif"
    #respText = make_gif_new(randomEpisodeLocation, subsLocation)

def generate_gifs(movie_path, subtitle_path, output_dir='/mnt/x/28dayslatergifs/', interval=5, start_time_str="00:00:00", max_filesize=None, debug=False, random_times=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(SCREENCAP_PATH):
        os.makedirs(SCREENCAP_PATH)

    # Clear the screencaps folder
    for file in os.listdir(SCREENCAP_PATH):
        file_path = os.path.join(SCREENCAP_PATH, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    font_path = os.path.join(os.path.dirname(__file__), FONT_PATH)
    subs = pysrt.open(subtitle_path, encoding='iso-8859-1')  # Specify the correct encoding
    font = ImageFont.truetype(font_path, FONT_SIZE)

    duration = get_video_duration(movie_path)
    if random_times:
        start_times = random.sample(range(0, duration, interval), duration // interval)
    else:
        start_times = range(sum(int(x) * 60 ** i for i, x in enumerate(reversed(start_time_str.split(":")))), duration, interval)

    for current_time in start_times:
        end_time = min(current_time + interval, duration)
        quote = get_quote(subs, current_time, end_time)
        filename = os.path.join(output_dir, generate_filename(movie_path, current_time, end_time, quote))
        create_gif(movie_path, current_time, end_time, quote, filename, font, max_filesize, debug)

def get_video_duration(movie_path):
    result = subprocess.run(
        [ffmpeg_path, '-i', movie_path, '-hide_banner'],
        stderr=subprocess.PIPE, universal_newlines=True
    )
    match = re.search(r"Duration: (\d+):(\d+):(\d+)\.(\d+)", result.stderr)
    if match:
        hours, minutes, seconds, _ = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0

def get_quote(subs, start_time, end_time):
    for sub in subs:
        if sub.start.ordinal >= start_time * 1000 and sub.end.ordinal <= end_time * 1000:
            return striptags(sub.text)
    return ""

def generate_filename(movie_path, start_time, end_time, quote):
    media_name = os.path.splitext(os.path.basename(movie_path))[0]
    start_str = time.strftime('%H-%M-%S', time.gmtime(start_time))
    end_str = time.strftime('%H-%M-%S', time.gmtime(end_time))
    quote_str = re.sub(r'[^a-zA-Z0-9]', '', quote)[:30]
    return f"{media_name}-Start[{start_str}]-End[{end_str}]-Quote[{quote_str}].gif"


def create_gif(movie_path, start_time, end_time, quote, filename, font, max_filesize, debug):
    images = []
    duration = end_time - start_time
    start_str = time.strftime('%H:%M:%S', time.gmtime(start_time))

    subprocess.call([
        ffmpeg_path, '-ss', start_str, '-i', movie_path, '-t', str(duration),
        '-vf', f"scale={WIDTH}:{HEIGHT}", '-pix_fmt', 'rgb24', '-r', f"{1 / FRAME_DURATION}", SCREENCAP_PATH + '/thumb%05d.png'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    file_names = sorted(fn for fn in os.listdir(SCREENCAP_PATH) if fn.endswith('.png'))
    for f in file_names:
        image = Image.open(os.path.join(SCREENCAP_PATH, f)).convert("RGB")
        draw = ImageDraw.Draw(image)
        if quote:
            text_bbox = font.getbbox(quote)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (image.size[0] - text_width) / 2
            y = image.size[1] - text_height - 10
            draw_text(draw, image.size[0], image.size[1], quote, font)
        images.append(image.resize((WIDTH, HEIGHT)))

    imageio.mimsave(filename, [array(img) for img in images], palettesize=PALLETSIZE, duration=FRAME_DURATION)

    # Log the initial file size
    initial_filesize = os.path.getsize(filename)
    print(f"Initial GIF size: {initial_filesize} bytes")

    # Ensure the GIF does not exceed the specified maximum file size
    if max_filesize:
        max_filesize_bytes = int(max_filesize * 1024 * 1024)  # Convert MB to bytes
        while os.path.getsize(filename) > max_filesize_bytes:
            print(f"GIF size {os.path.getsize(filename)} exceeds limit of {max_filesize_bytes} bytes. Reducing resolution and retrying...")
            reduce_resolution()
            regenerate_gif(images, filename)
            optimize_gif(filename, max_filesize_bytes, debug)

    # Log details about the generated GIF
    print(f"Generated GIF: {filename}")
    print(f"Start Time: {start_str}")
    print(f"End Time: {time.strftime('%H:%M:%S', time.gmtime(end_time))}")
    print(f"Number of Frames: {len(images)}")
    print(f"Frame Duration: {FRAME_DURATION} seconds")
    print(f"FPS: {1 / FRAME_DURATION}")
    print(f"Quote: {'Yes' if quote else 'No'}")
    print(f"Output Filename: {filename}")

def reduce_resolution():
    global WIDTH, HEIGHT, PALLETSIZE
    WIDTH = max(WIDTH // 2, 320)
    HEIGHT = max(HEIGHT // 2, 180)
    PALLETSIZE = max(PALLETSIZE // 2, 64)
    print(f"New resolution: {WIDTH}x{HEIGHT}, Palettesize: {PALLETSIZE}")

def regenerate_gif(images, filename):
    imageio.mimsave(filename, [array(img.resize((WIDTH, HEIGHT))) for img in images], palettesize=PALLETSIZE, duration=FRAME_DURATION)

def optimize_gif(filename, max_filesize_bytes, debug):
    iteration = 1
    temp_filename = filename.replace('.gif', f'_temp_{iteration}.gif')
    subprocess.call([
        ffmpeg_path, '-i', filename, '-vf', f"scale={WIDTH}:{HEIGHT}", '-pix_fmt', 'rgb24', '-r', f"{1 / FRAME_DURATION}", '-fs', str(max_filesize_bytes), temp_filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    while os.path.getsize(temp_filename) > max_filesize_bytes:
        iteration += 1
        new_temp_filename = filename.replace('.gif', f'_temp_{iteration}.gif')
        subprocess.call([
            ffmpeg_path, '-i', temp_filename, '-vf', f"scale={WIDTH}:{HEIGHT}", '-pix_fmt', 'rgb24', '-r', f"{1 / FRAME_DURATION}", '-fs', str(max_filesize_bytes), new_temp_filename
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if os.path.getsize(new_temp_filename) <= max_filesize_bytes:
            if debug:
                print(f"Optimization iteration {iteration}: {new_temp_filename} (size: {os.path.getsize(new_temp_filename)} bytes)")
            os.replace(new_temp_filename, filename)
            break
        else:
            if debug:
                print(f"Optimization iteration {iteration}: {new_temp_filename} (size: {os.path.getsize(new_temp_filename)} bytes)")
            os.remove(temp_filename)
            temp_filename = new_temp_filename

    # Log the final file size
    final_filesize = os.path.getsize(filename)
    print(f"Final GIF size: {final_filesize} bytes")

    # Clean up temp files
    for file in os.listdir(os.path.dirname(filename)):
        if file.startswith(os.path.basename(filename).replace('.gif', '_temp_')):
            os.remove(os.path.join(os.path.dirname(filename), file))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--movie', type=str, required=True, help='Path to the movie file')
    parser.add_argument('--subtitles', type=str, required=True, help='Path to the subtitles file')
    parser.add_argument('--output', type=str, default='/mnt/x/28dayslatergifs/', help='Output directory for GIFs')
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds for GIF generation')
    parser.add_argument('--startTime', type=str, default="00:00:00", help='Start time for GIF generation in hh:mm:ss format')
    parser.add_argument('--maxFilesize', type=float, help='Maximum file size for the GIF in MB')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to save each iteration of the optimization process')
    parser.add_argument('--randomTimes', action='store_true', help='Generate GIFs from different random start times')
    args = parser.parse_args()

    generate_gifs(args.movie, args.subtitles, args.output, args.interval, args.startTime, args.maxFilesize, args.debug, args.randomTimes)
