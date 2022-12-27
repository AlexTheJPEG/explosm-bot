import json
import os

import boto3
import requests
import tweepy
from PIL import Image


def get_twitter_keys() -> dict:
    aws_client = boto3.client("ssm")

    parameters = aws_client.get_parameters(
        Names=[
            "twitter_api_key",
            "twitter_api_secret",
            "twitter_access_token",
            "twitter_access_secret",
        ],
        WithDecryption=True,
    )

    keys = {parameter["Name"]: parameter["Value"] for parameter in parameters["Parameters"]}
    return keys


def twitter_api() -> tweepy.API:
    keys = get_twitter_keys()

    auth = tweepy.OAuthHandler(keys["twitter_api_key"], keys["twitter_api_secret"])
    auth.set_access_token(keys["twitter_access_token"], keys["twitter_access_secret"])
    return tweepy.API(auth)


def combine_images(image_names, border_size=0) -> None:
    combined_image_width = sum(Image.open(name).size[0] for name in image_names) + 2 * border_size
    combined_image_height = max(Image.open(name).size[1] for name in image_names) + 2 * border_size
    combined_image = Image.new(
        "RGB", (combined_image_width, combined_image_height), color=(255, 255, 255)
    )

    x_offset = border_size
    y_offset = border_size
    for name in image_names:
        image = Image.open(name)
        combined_image.paste(image, (x_offset, y_offset))
        x_offset += image.size[0]

    combined_image.save("/tmp/comic.png", format="PNG")


def tweet_comic() -> None:
    # Get the three panels from the randomly-generated comic
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
    }

    with requests.get("https://explosm.net/api/get-random-panels", headers=headers) as response:
        panels_json = json.loads(response.text)

    # Save each panel as a temporary file
    panels = panels_json["panels"]
    filenames = [f"/tmp/{panel['filename']}" for panel in panels]
    for filename in filenames:
        with requests.get(f"https://rcg-cdn.explosm.net/panels/{filename.removeprefix('/tmp/')}", "wb") as panel_image:
            with open(filename, "wb") as file:
                file.write(panel_image.content)

    # Combine the three panels into one image
    combine_images(filenames, 20)

    # Remove the panel files
    for filename in filenames:
        os.remove(filename)

    # Upload the image onto Twitter
    api = twitter_api()
    upload = api.media_upload("/tmp/comic.png")
    media_id = [upload.media_id]

    # Post the image with its permalink
    permalink = "".join(panel["slug"] for panel in panels)
    api.update_status(status=f"https://explosm.net/rcg/{permalink}", media_ids=media_id)

    # Remove the temporary file
    os.remove("/tmp/comic.png")


def lambda_handler(event, context):
    tweet_comic()
