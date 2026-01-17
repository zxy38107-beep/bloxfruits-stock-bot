import discord
import requests
import os
import json

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

STOCK_FILE = "stock_data.json"
RARE_FRUITS = ["Kitsune", "Dragon"]

PRIMARY_API = "https://blox-fruit-api.vercel.app/api/stock"
BACKUP_API = "https://api.bloxfruitsapi.com/stock"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# ---------------- FETCH STOCK ----------------

def try_fetch(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def fetch_stock():
    print("Fetching stock...")

    data = try_fetch(PRIMARY_API)
    if not data:
        print("Primary API failed, trying backup...")
        data = try_fetch(BACKUP_API)

    if not data:
        print("ALL APIs FAILED")
        return None

    print("Stock fetched successfully")

    return {
        "normal": data.get("stock", []),
        "mirage": data.get("mirageStock", [])
    }

# ---------------- FILE IO ----------------

def load_old_stock():
    if not os.path.exists(STOCK_FILE):
        return {"normal": [], "mirage": []}

    with open(STOCK_FILE, "r") as f:
        return json.load(f)

def save_stock(stock):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=2)

# ---------------- EMBEDS ----------------

def stock_embed(title, stock, color):
    embed = discord.Embed(
        title=title,
        description="\n".join(f"• {f}" for f in stock) or "No fruits",
        color=color
    )
    embed.set_footer(text="Blox Fruits Stock Bot")
    return embed

def rare_embed(dealer, fruits):
    embed = discord.Embed(
        title="🔥 RARE FRUIT ALERT 🔥",
        description=f"**{dealer} Dealer**\n\n" +
                    "\n".join(f"🟡 {f}" for f in fruits),
        color=0xFF0000
    )
    return embed

# ---------------- BOT ----------------

@client.event
async def on_ready():
    print("Bot logged in")

    channel = await client.fetch_channel(CHANNEL_ID)

    new_stock = fetch_stock()
    if not new_stock:
        await channel.send("⚠️ Stock API unavailable. Will retry next run.")
        await client.close()
        return

    old_stock = load_old_stock()

    if new_stock["normal"] != old_stock["normal"]:
        await channel.send(
            embed=stock_embed("🍏 Normal Dealer Stock Updated",
                              new_stock["normal"], 0x00FF99)
        )

    if new_stock["mirage"] != old_stock["mirage"]:
        await channel.send(
            embed=stock_embed("🌊 Mirage Dealer Stock Updated",
                              new_stock["mirage"], 0x3399FF)
        )

    for dealer in ["normal", "mirage"]:
        new_rare = [f for f in new_stock[dealer] if f in RARE_FRUITS]
        old_rare = [f for f in old_stock.get(dealer, []) if f in RARE_FRUITS]

        if new_rare and new_rare != old_rare:
            await channel.send(embed=rare_embed(dealer.capitalize(), new_rare))

    save_stock(new_stock)
    await client.close()

client.run(TOKEN)
