from discord.ext import commands,tasks
import discord
import os
from dotenv import load_dotenv
import discord
import platform

if platform.system() == "Linux":
    opus_path = '/usr/lib/libopus.so.***' 
    discord.opus.load_opus(opus_path)
intents = discord.Intents.all()
# uselavalink is set to True bot will try to connect to lavalink server
# if local is enabled bot will try to connect to local lavalink server
load_dotenv(".env")

class staffbot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            intents=intents,
            command_prefix=".",
            help_command=None,
            application_id=1266405128727035904,
        )

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):           
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        await self.tree.sync()

bot = staffbot()

@bot.event
async def on_ready():
    print("-------------------")
    print(f"{bot.user} is Ready")
    print("-------------------")

bot.run(os.getenv("DISCORD_TOKEN"))