import discord
import requests
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_stock():
    r = requests.get("https://blox-fruit-api.vercel.app/api/stock", timeout=10)
    return r.json()["stock"]

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)

    stock = get_stock()

    msg = "**🍏 Blox Fruits Stock**\n\n"
    msg += "\n".join(f"• {fruit}" for fruit in stock)

    await channel.send(msg)
    await client.close()

client.run(TOKEN)
