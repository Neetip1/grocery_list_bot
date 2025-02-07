import os
import discord
from discord.ext import commands
from flask import Flask

TOKEN = os.getenv("TOKEN")

# Flask app to keep the bot alive on Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True  # Enable message content
bot = commands.Bot(command_prefix="!", intents=intents)

# Grocery List Format: { "item": False } (False = Not Bought, True = Bought)
grocery_list = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

# 📌 Add Item
@bot.command(name="add")
async def add_item(ctx, *, item: str):
    """Add an item to the grocery list as 'Not Bought'."""
    if item.lower() in grocery_list:
        await ctx.send(f"`{item}` is already on the list!", delete_after=5)
    else:
        grocery_list[item.lower()] = False  # Default to "Not Bought"
        await ctx.send(f"Added `{item}` to the grocery list!", delete_after=5)
    await ctx.message.delete()

# 🗑 Remove Item
@bot.command(name="remove")
async def remove_item(ctx, *, item: str):
    """Remove an item from the grocery list."""
    if item.lower() in grocery_list:
        del grocery_list[item.lower()]
        await ctx.send(f"Removed `{item}` from the grocery list.", delete_after=5)
    else:
        await ctx.send(f"`{item}` is not in the grocery list.", delete_after=5)
    await ctx.message.delete()

# ✅ Check/Uncheck Item
@bot.command(name="check")
async def check_item(ctx, item: str, status: str):
    """Mark an item as Bought (✅) or Not Bought (❌)."""
    item = item.lower()

    if item not in grocery_list:
        await ctx.send(f"`{item}` is not in the grocery list.", delete_after=5)
        return

    if status.lower() in ["bought", "check", "yes"]:
        grocery_list[item] = True
        await ctx.send(f"✅ Marked `{item}` as bought!", delete_after=5)
    elif status.lower() in ["not bought", "uncheck", "no"]:
        grocery_list[item] = False
        await ctx.send(f"❌ Marked `{item}` as not bought.", delete_after=5)
    else:
        await ctx.send("Use `bought` or `not bought`.", delete_after=5)

    await ctx.message.delete()

# 📜 Show Grocery List
@bot.command(name="list")
async def show_list(ctx):
    """Display the current grocery list with checkmarks."""
    if not grocery_list:
        await ctx.send("The grocery list is empty.")
        return

    list_content = "**🛒 Grocery List:**\n" + "\n".join(
        f"- {'✅' if bought else '❌'} {index + 1}. {item}" for index, (item, bought) in enumerate(grocery_list.items())
    )
    await ctx.send(list_content)

# 🧹 Clear Grocery List
@bot.command(name="clear")
async def clear_list(ctx):
    """Clear the entire grocery list."""
    grocery_list.clear()
    await ctx.send("🗑 The grocery list has been cleared.")

# Run both Flask & Discord bot
if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
    bot.run(TOKEN)
