import discord
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("Logged in as:", client.user)

    try:
        channel = await client.fetch_channel(CHANNEL_ID)
        print("Fetched channel:", channel)
    except Exception as e:
        print("FAILED TO FETCH CHANNEL:", e)
        await client.close()
        return

    try:
        await channel.send("✅ **TEST MESSAGE: BOT CAN SEND MESSAGES**")
        print("MESSAGE SENT SUCCESSFULLY")
    except Exception as e:
        print("FAILED TO SEND MESSAGE:", e)

    await client.close()

client.run(TOKEN)
