import discord
from discord.ext import commands, tasks
import aiohttp
import json as jsonlib
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import os
from flask import Flask
from threading import Thread


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = "https://nepalstock.onrender.com/securityDailyTradeStat/58"

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kathmandu'))

# --- Watchlist Handling ---
def load_watchlist():
    try:
        with open("watchlist.json", "r") as f:
            return jsonlib.load(f)
    except (FileNotFoundError, jsonlib.JSONDecodeError):
        return {"users": {}}

def save_watchlist(data):
    with open("watchlist.json", "w") as f:
        jsonlib.dump(data, f, indent=4)

# --- Safe API Fetch ---
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            text = await resp.text()
            print(f"[DEBUG] API Response:\n{text}")  # For Debugging
            
            if not text.strip():
                raise ValueError("API returned an empty response.")
            if text.lstrip().startswith("<"):  # HTML error page
                raise ValueError("API returned invalid (HTML) response.")
            
            try:
                return jsonlib.loads(text)
            except jsonlib.JSONDecodeError:
                raise ValueError("Failed to parse API response as JSON.")

# --- Price Check and DM ---
async def check_prices():
    data = load_watchlist()
    try:
        nepse_data = await fetch_data()
    except Exception as e:
        print(f"[ERROR] Failed to fetch NEPSE data: {e}")
        return
    
    for user_id, goals in data["users"].items():
        user = await bot.fetch_user(int(user_id))
        for symbol, goal_price in goals.items():
            stock = next((s for s in nepse_data if s["symbol"].upper() == symbol.upper()), None)
            if stock and stock["lastTradedPrice"] >= goal_price:
                await user.send(f"📈 **{symbol.upper()}** reached **{stock['lastTradedPrice']}** (Goal: {goal_price})")

# --- Scheduler Task ---
@scheduler.scheduled_job('cron', day_of_week='sun,mon,tue,wed,thu', hour=15, minute=0)
async def scheduled_check():
    await check_prices()

# --- Events ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    scheduler.start()

# --- Commands ---

@bot.command()
async def addgoal(ctx, symbol: str, price: float):
    data = load_watchlist()
    user_id = str(ctx.author.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {}
    data["users"][user_id][symbol.upper()] = price
    save_watchlist(data)
    await ctx.send(f"✅ Goal added: {symbol.upper()} ≥ {price}")

@bot.command()
async def removegoal(ctx, symbol: str):
    data = load_watchlist()
    user_id = str(ctx.author.id)
    if user_id in data["users"] and symbol.upper() in data["users"][user_id]:
        del data["users"][user_id][symbol.upper()]
        save_watchlist(data)
        await ctx.send(f"❌ Goal removed: {symbol.upper()}")
    else:
        await ctx.send("⚠️ Goal not found.")

@bot.command()
async def mygoals(ctx):
    data = load_watchlist()
    user_id = str(ctx.author.id)
    goals = data["users"].get(user_id, {})
    if not goals:
        await ctx.send("📭 You have no goals set.")
    else:
        msg = "\n".join(f"• {sym}: {price}" for sym, price in goals.items())
        await ctx.send(f"📋 Your Goals:\n{msg}")

@bot.command()
async def price(ctx, symbol: str):
    try:
        nepse_data = await fetch_data()
    except Exception as e:
        await ctx.send(f"⚠️ Could not fetch NEPSE data.\nError: `{e}`")
        return

    stock = next((s for s in nepse_data if s["symbol"].upper() == symbol.upper()), None)
    if stock:
        await ctx.send(f"💹 **{stock['symbol']}** — Last Traded Price: **{stock['lastTradedPrice']}**")
    else:
        await ctx.send(f"❓ Symbol **{symbol.upper()}** not found.")

# --- Run the Bot ---
bot.run(TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()
