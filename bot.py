import discord
import requests
import os
import json
import asyncio

# ================== CONFIG ==================

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

STOCK_FILE = "stock_data.json"
RARE_FRUITS = ["Kitsune", "Dragon"]
API_URL = "https://blox-fruit-api.vercel.app/api/stock"

# ================== DISCORD ==================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ================== HELPERS ==================

def fetch_stock():
    try:
        r = requests.get(API_URL, timeout=15)

        if r.status_code != 200:
            print("API returned status:", r.status_code)
            return None

        data = r.json()

        return {
            "normal": data.get("stock", []),
            "mirage": data.get("mirageStock", [])
        }

    except Exception as e:
        print("Failed to fetch stock:", e)
        return None


def load_old_stock():
    if not os.path.exists(STOCK_FILE):
        return {"normal": [], "mirage": []}

    try:
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except:
        return {"normal": [], "mirage": []}


def save_stock(stock):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=2)

# ================== EMBEDS ==================

def stock_embed(title, stock, color):
    embed = discord.Embed(
        title=title,
        description="\n".join(f"• {fruit}" for fruit in stock) or "No fruits",
        color=color
    )
    embed.set_footer(text="Blox Fruits Stock Bot")
    return embed


def rare_embed(dealer, fruits):
    embed = discord.Embed(
        title="🔥 RARE FRUIT ALERT 🔥",
        description=f"**{dealer} Dealer**\n\n" +
                    "\n".join(f"🟡 {fruit}" for fruit in fruits),
        color=0xFF0000
    )
    embed.set_footer(text="Hurry before reset!")
    return embed

# ================== BOT LOGIC ==================

@client.event
async def on_ready():
    channel = await client.fetch_channel(CHANNEL_ID)


    new_stock = fetch_stock()
    if not new_stock:
        await client.close()
        return

    old_stock = load_old_stock()

    # -------- NORMAL STOCK CHANGE --------
    if new_stock["normal"] != old_stock["normal"]:
        await channel.send(
            embed=stock_embed(
                "🍏 Normal Dealer Stock Updated",
                new_stock["normal"],
                0x00FF99
            )
        )

    # -------- MIRAGE STOCK CHANGE --------
    if new_stock["mirage"] != old_stock["mirage"]:
        await channel.send(
            embed=stock_embed(
                "🌊 Mirage Dealer Stock Updated",
                new_stock["mirage"],
                0x3399FF
            )
        )

    # -------- RARE FRUIT ALERTS --------
    for dealer in ["normal", "mirage"]:
        new_rare = [f for f in new_stock[dealer] if f in RARE_FRUITS]
        old_rare = [f for f in old_stock.get(dealer, []) if f in RARE_FRUITS]

        if new_rare and new_rare != old_rare:
            await channel.send(
                embed=rare_embed(dealer.capitalize(), new_rare)
            )

    save_stock(new_stock)
    await client.close()

# ================== RUN ==================

client.run(TOKEN)
