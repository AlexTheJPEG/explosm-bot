import json
import logging
import os
import time

import requests
import schedule
from mastodon import Mastodon
from PIL import Image

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
CW = "Possible CW: strong language, sexual imagery, bodily fluds, references to drugs & alcohol, blood & gore"


def combine_images(image_names: list[str], border_size: int = 0) -> None:
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


def toot_comic(api: Mastodon) -> None:
    # Get the three panels from the randomly-generated comic
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"  # noqa: E501
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
    combine_images(filenames, 50)

    # Upload the image
    media_upload = api.media_post("/tmp/comic.png")

    # Post the image with its permalink
    permalink = "".join(panel["slug"] for panel in panels)
    post = api.status_post(
        status=f"https://explosm.net/rcg/{permalink}",
        spoiler_text=CW,
        media_ids=media_upload,
        sensitive=True,
    )
    
    logging.info("Explosm Bot: Posted image")
    logging.debug(post)


if __name__ == "__main__":
    # Uncomment the two lines below to use a .env file
    # from dotenv import load_dotenv
    # load_dotenv()
    api = Mastodon(
        access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
        api_base_url=os.getenv("MASTODON_URL"),
    )
    logging.info("Explosm Bot: Created API instance")

    schedule.every().hour.at(":00").do(toot_comic, api=api)
    schedule.every().hour.at(":30").do(toot_comic, api=api)
    logging.info("Explosm Bot: Created schedule")

    while True:
        schedule.run_pending()
        time.sleep(1)
