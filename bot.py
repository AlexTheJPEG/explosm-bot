import time
import tweepy
import requests
import os
import re

from bs4 import BeautifulSoup
from PIL import Image


def combine_images(image1, image2, image3, output):
    image1 = Image.open(image1)
    image2 = Image.open(image2)
    image3 = Image.open(image3)

    widths = [image1.size[0], image2.size[0], image3.size[0]]
    heights = [image1.size[1], image2.size[1], image3.size[1]]

    total_width = sum(widths)
    max_height = max(heights)

    images = [image1, image2, image3]
    new_image = Image.new("RGBA", (total_width, max_height))

    x_offset = 0
    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]

    new_image.save(output)


def twitter_api():
    CONSUMER_KEY = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    ACCESS_KEY = os.environ['ACCESS_KEY']
    ACCESS_SECRET = os.environ['ACCESS_SECRET']

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth)


def tweet_comic():
    api = twitter_api()
    filename_regex = re.compile(r"panels/(.*).png")
    filenames = []

    website_response = requests.get('http://explosm.net/rcg')
    if website_response.status_code == 200:
        # Get the three panels from the randomly-generated comic
        rcg_soup = BeautifulSoup(website_response.text, "html.parser")
        permalink = rcg_soup.select('input#permalink')[0]['value']
        comic_files = [img["src"] for img in rcg_soup.select('div > img')][:-1]

        # Save each panel as a temporary file
        for comic_file in comic_files:
            comic_response = requests.get(comic_file)
            filename = filename_regex.search(comic_file).group(1) + ".png"

            filenames.append(filename)

            with open(filename, 'wb') as image:
                for chunk in comic_response:
                    image.write(chunk)

        # Combine the three panels into one image
        combine_images(*filenames, "temp.png")

        # Remove the panel files
        for filename in filenames:
            os.remove(filename)

        # Upload the image onto Twitter
        upload = api.media_upload("temp.png")
        media_id = [upload.media_id]

        # Post the image with its permalink
        api.update_status(status=permalink, media_ids=media_id)

        # Remove the temporary file
        os.remove("temp.png")
    else:
        print(f"Oh noes! Something terrible happened! Error code {website_response.status_code}")


while True:
    tweet_comic()
    time.sleep(60 * 60)
