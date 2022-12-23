import os
import shutil

import requests
import tweepy
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
    consumer_key = os.environ['CONSUMER_KEY']
    consumer_secret = os.environ['CONSUMER_SECRET']
    access_key = os.environ['ACCESS_KEY']
    access_secret = os.environ['ACCESS_SECRET']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return tweepy.API(auth)


def tweet_comic():
    # Get the three panels from the randomly-generated comic

    # Save each panel as a temporary file

    # Combine the three panels into one image

    # Remove the panel files

    # Upload the image onto Twitter

    # Post the image with its permalink

    # Remove the temporary file

    pass