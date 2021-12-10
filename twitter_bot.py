import base64
import json
import requests
import configparser
import random
import os
import time
import subprocess

import OpenSSL
from twython import Twython
from base64 import b64encode
from make_gifs import make_gif, check_config

################################
# Initial Script Run
################################

#get credendials from config
config = configparser.ConfigParser()
config.read("config.cfg")
config.sections()
slugs = check_config("config.cfg")[3]
#get credentials from config
CLIENT_ID = config.get("imgur", "client_id")
API_KEY = config.get("imgur", "api_key")
APP_KEY = config.get("twitter", "app_key")
APP_SECRET = config.get("twitter", "app_secret")
OAUTH_TOKEN = config.get("twitter", "oauth_token")
OAUTH_TOKEN_SECRET = config.get("twitter", "oauth_token_secret")
headers = {"Authorization": "Client-ID " + CLIENT_ID}
url = "https://api.imgur.com/3/upload.json"
#begin while loop
while True:

    # -------------------
    # Create new gif 
    # -------------------
    while True:
        try:
            # you can set many more options, check the make_gif-function
            gifResp = make_gif()
            quote = gifResp["subs"][0]
        except Exception as ex:
            print('something went wrong during gif-generation: ', ex)
            continue
        else:
            break
    
    
    # -------------------
    # first pass reduce the amount of colors 
    # -------------------
    try:
        if(os.path.getsize('sopranos.gif') > 5242880):
            subprocess.call(['convert',
                            'sopranos.gif',
                            '-layers',
                            'optimize',
                            '-colors',
                            '128',
                            '-loop',
                            '0',
                            'sopranos.gif']) #, shell=True
    except Exception as ex:
        print('first pass reduce the amount of colors err: ', ex)
        continue    

    # -------------------
    # second pass reduce the amount of colors 
    # -------------------
    if(os.path.getsize('sopranos.gif') > 5242880):
        subprocess.call(['convert',
                         'sopranos.gif',
                         '-layers',
                         'optimize',
                         '-colors',
                         '64',
                         '-loop',
                         '0',
                         'sopranos.gif'])

    # -------------------
    # first pass reduce the size 
    # -------------------
    while(os.path.getsize('sopranos.gif') > 5242880):
        subprocess.call(['convert',
                         'sopranos.gif',
                         '-resize',
                         '90%',
                         '-coalesce',
                         '-layers',
                         'optimize',
                         '-loop',
                         '0',
                         'sopranos.gif'])
    
    #
    # not sure?
    #
    try:
        response = requests.post(
            url,
            headers=headers,
            data={
                'key': API_KEY,
                'image': b64encode(open('sopranos.gif', 'rb').read()),
                'type': 'base64',
                'name': 'sopranos.gif',
                'title': 'sopranos gif bot twitter'
            }
        )
    except (requests.exceptions.ConnectionError, OpenSSL.SSL.SysCallError):
        # try again.
        continue

    try:
        res_json = response.json()
        link = res_json['data']['link']
    except (KeyError, ValueError):
        # try again.
        continue

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # twitter: upload media
    gif = open('sopranos.gif', 'rb')
    response = twitter.upload_media(media=gif)

    #twitter: shorten quote
    if len(quote) > 70:
        quote = (quote[:67] + '...')

    if len(quote) == 0:
        quote = "..."
    #print("twitter quote = ", quote)
    #status = '"' + quote + '" ' + link + ' #sopranosgif'
    status = '"' + quote + '" ' + link + ' #sopranosgif'
   
    print("tweeting with this text = ", status)

    try:
        twitter.update_status(status=status, media_ids=[response['media_id']])
    except Exception as ex:
        print("TWEETING ERR:", ex)
        # error with twitter sleep a bit and try again
        #time.sleep(1800)
        continue

    print("sleeping 1 hour")
    # sleep 1 hour
    sleepThisManyHours = 2
    time.sleep((sleepThisManyHours)*3600)
