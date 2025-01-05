import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = 'MTMyNDU2OTgyNzc3OTY3NDE5NA.G5VHPs.Nred6og1FWg1MCpHLh1jmyvcD_1tjrtsj06mrM'
GUILD = 'Brandon\'s server'

intents = discord.Intents.all()
intents.members = True  # Required for member updates (voice state changes)
intents.voice_states = True  # Required to track voice state changes
intents.messages = True
# client = discord.Client()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

@client.command()
async def test(ctx):
    print("test")
    await ctx.send("test123")
client.run(TOKEN)