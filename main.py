import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
from flask import Flask
import threading

# Load bot token from environment variables
TOKEN = os.getenv("TOKEN")  # Make sure to set this in your hosting platform

# Intents setup
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # For slash commands

# Grocery list storage (Dictionary for status tracking)
grocery_list = {}  # Example: {1: ("Milk", False), 2: ("Eggs", True)}

# Global list message
list_message = None


# 🛠️ Function to format the grocery list
def format_grocery_list():
    if not grocery_list:
        return "📝 **Grocery List:**\n*The grocery list is empty.*"
    return "📝 **Grocery List:**\n" + "\n".join(
        f"{num}. {'✅' if bought else '❌'} {item}" for num, (item, bought) in grocery_list.items()
    )


# 🚀 Bot Ready Event
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🔄 Synced {len(await tree.sync())} commands.")
    await bot.change_presence(activity=discord.Game(name="Managing your groceries!"))


# ➕ Add an Item
@tree.command(name="add", description="Add an item to the grocery list")
async def add_item(interaction: discord.Interaction, item: str):
    """Add an item and update the message."""
    global list_message
    num = len(grocery_list) + 1
    grocery_list[num] = (item, False)

    # Update or send the message
    if list_message:
        await list_message.edit(content=format_grocery_list())
    else:
        list_message = await interaction.channel.send(format_grocery_list())

    await interaction.response.send_message(f"✅ Added `{item}` to the list!", ephemeral=True)


# ❌ Remove an Item
@tree.command(name="remove", description="Remove an item from the grocery list")
async def remove_item(interaction: discord.Interaction, number: int):
    """Remove an item by its number."""
    global list_message
    if number in grocery_list:
        del grocery_list[number]
        # Re-number the list
        grocery_list.update({i + 1: v for i, v in enumerate(grocery_list.values())})

        if list_message:
            await list_message.edit(content=format_grocery_list())
        await interaction.response.send_message(f"🗑 Removed item `{number}`.", ephemeral=True)
    else:
        await interaction.response.send_message(f"⚠️ Item `{number}` not found.", ephemeral=True)


# ✅ Toggle Bought/Not Bought
@tree.command(name="toggle", description="Mark an item as bought or not bought")
async def toggle_item(interaction: discord.Interaction, number: int):
    """Toggle the bought status."""
    global list_message
    if number in grocery_list:
        item, bought = grocery_list[number]
        grocery_list[number] = (item, not bought)  # Toggle status

        if list_message:
            await list_message.edit(content=format_grocery_list())

        await interaction.response.send_message(
            f"🔄 Toggled `{item}` to {'✅ Bought' if not bought else '❌ Not Bought'}.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(f"⚠️ Item `{number}` not found.", ephemeral=True)


# 📜 Show the Grocery List
@tree.command(name="list", description="Show the current grocery list")
async def show_list(interaction: discord.Interaction):
    """Display the current grocery list."""
    global list_message
    if list_message:
        await list_message.edit(content=format_grocery_list())
    else:
        list_message = await interaction.channel.send(format_grocery_list())

    await interaction.response.send_message("📋 List updated!", ephemeral=True)


# 🗑 Clear the Grocery List
@tree.command(name="clear", description="Clear the entire grocery list")
async def clear_list(interaction: discord.Interaction):
    """Clear all items from the list."""
    global list_message
    grocery_list.clear()

    if list_message:
        await list_message.edit(content="📝 **Grocery List:**\n*The grocery list is empty.*")

    await interaction.response.send_message("🗑 Grocery list cleared!", ephemeral=True)


# 🌍 Flask Web Server (For Hosting)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

# 🔄 Run Flask in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# 🎯 Run the bot
bot.run(TOKEN)
