### NEPSEBot

This is a Discord bot designed to help users track the Nepal Stock Exchange (NEPSE) prices. The bot can set price goals for specific stock symbols and notify users via direct message when a target price is reached.

#### Features

* **Price Tracking**: The bot can fetch the last traded price for a given stock symbol from an external API.
* **Price Alerts**: Users can set price goals for specific stock symbols. The bot checks for these prices daily and sends a direct message to the user when a goal is met.
* **User-Specific Watchlist**: Goals are stored in a `watchlist.json` file, with each user having their own set of goals.
* **Discord Commands**: The bot responds to several commands, including `!addgoal`, `!removegoal`, `!mygoals`, and `!price`.
* **Web Server**: A Flask web server runs alongside the bot to ensure it stays online, listening on port `0.0.0.0`.

#### Requirements

The project uses the following Python libraries, which can be installed from `requirements.txt`:

* `discord.py`
* `aiohttp`
* `APScheduler`
* `Flask`
* `python-dotenv`
* `requests`
* `pandas`
* `numpy`
* `beautifulsoup4`
* `selenium`

#### How to Run

1.  **Set up dependencies**: Install the required libraries using pip and the `requirements.txt` file.
2.  **Configure token**: The bot requires a `DISCORD_BOT_TOKEN` environment variable to run.
3.  **Run the script**: Execute `bot.py`. The Flask server will start and the bot will connect to Discord.
