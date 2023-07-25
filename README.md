<p align="center">
    <img width="200" src="./assets/explosm-bot.png" alt="Explosm Favicon">
</p>

# Explosm Bot
A Mastodon bot (https://botsin.space/@explosmbot) that prints randomly-generated comics (http://explosm.net/rcg)

## 🐘 Why Mastodon?
This was originally a Twitter bot, but because Twitter doesn't care about its users, they're starting to add a paywall for their API starting February 9th. Because I don't want to pay to run a little side project, I moved to a Mastodon instance [specifically made to host bots](https://botsin.space). Feel free to follow the bot and add it to your timeline!

## 🛠 Dev Setup
To get started, create a Mastodon account in your instance of choice. I used **botsin.space** as mentioned above. Then go into **Preferences > Profile** and make sure that **"This is a bot account"** is checked.

Go into **Development** and click on the **New application** button. Create a name for your bot and make sure it has at least the following scopes: `read write write:media write:statuses follow`. It should now generate an **access token**. Store this in a safe place, and DO NOT SHARE IT WITH ANYONE.

Now, clone this repo somewhere on your machine, then create the following environment variables: (you can use an `.env` file if you want, but be sure to uncomment a few lines at the bottom of the main Python file)
```
MASTODON_ACCESS_TOKEN=<your access token>
MASTODON_URL=<instance URL>
```

As for dependencies, they are all handled by [Poetry](https://github.com/python-poetry/poetry). Install Poetry on your machine if you haven't already, then simply run `poetry install` in the project directory.

To run the bot, activate the virtual environment created by Poetry using `poetry shell` and run `python bot.py` in the project directory.

### 🐋 Docker
You can also run this bot as a Docker container. To do this, first create an `.env` file with all of the environment variables listed above. Then, if it hasn't been created already, create a `requirements.txt` file by running `poetry export -f requirements.txt --output requirements.txt --without-hashes`.

Finally, run the following Docker commands:
```
docker build . -t explosm-bot
docker run --env-file .env explosm-bot
```

This will create a container named `explosm-bot` that will run your Mastodon bot!

## 💬 Notes
An alternative way to run your bot without explicitly activating the virtual environment is by running `poetry run python bot.py`. If you're running the bot on VSCode or a Python IDE, the virtual environment may be activated automatically.