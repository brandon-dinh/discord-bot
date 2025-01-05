import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

intents = discord.Intents.all()
intents.members = True  # Required for member updates (voice state changes)
intents.voice_states = True  # Required to track voice state changes
intents.messages = True
# Initialize the bot with prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# File where user data will be saved
DATA_FILE = 'voice_time_data.json'
# Load the persistent data from the JSON file
def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save the data to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize user data from file
user_data = load_data()

# Keep track of when a user joined a voice channel
user_join_times = {}

# Track users in each voice channel to calculate time spent together
channel_members = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Handle user joining a voice channel
    if before.channel is None and after.channel is not None:
        user_join_times[member.id] = datetime.now()

        # Track which users are in the same channel
        if after.channel.id not in channel_members:
            channel_members[after.channel.id] = set()
        channel_members[after.channel.id].add(member.id)

    # Handle user leaving a voice channel
    if before.channel is not None and after.channel is None:
        if member.id in user_join_times:
            join_time = user_join_times[member.id]
            total_time = datetime.now() - join_time
            if member.id not in user_data:
                user_data[member.id] = {"total_time_spent": 0.0, "time_with_others": {}}
            user_data[member.id]["total_time_spent"] += total_time.total_seconds() / 60.0
            
            # Update time spent with other members in the same channel
            if before.channel.id in channel_members:
                for other_user_id in channel_members[before.channel.id]:
                    if other_user_id != member.id:
                        if other_user_id not in user_data[member.id]["time_with_others"]:
                            user_data[member.id]["time_with_others"][other_user_id] = 0.0
                        time_diff = datetime.now() - max(join_time, user_join_times[other_user_id])
                        user_data[member.id]["time_with_others"][other_user_id] += time_diff.total_seconds() / 60.0
                        user_data[other_user_id]["time_with_others"][member.id] += time_diff.total_seconds() / 60.0
                        
            # Remove member from channel tracking
            channel_members[before.channel.id].remove(member.id)
            if not channel_members[before.channel.id]:
                del channel_members[before.channel.id]

        del user_join_times[member.id]

    # Save data after each update
    save_data(user_data)

@bot.command()
async def stats(ctx, member: discord.Member = None):
    """Command to get a member's total time in voice and time spent with others."""
    member = member or ctx.author  # Default to the command caller if no member is specified
    
    if member.id not in user_data:
        await ctx.send(f"No data found for {member.display_name}.")
        return
    
    total_time_spent = round(user_data[member.id]["total_time_spent"], 2)
    time_with_others = user_data[member.id]["time_with_others"]

    # Format total time
    total_time_str = str(total_time_spent)
    if len(total_time_str) > 7:
        total_time_str = total_time_str[:7]

    embed = discord.Embed(title=f"Stats for {member.display_name}")
    embed.add_field(name="Total Time in Voice Call (mins)", value=total_time_str)
    
    if time_with_others:
        time_str = "\n".join([f"<@{other_member}>: {str(round(t, 2))}" for other_member, t in list(time_with_others.items()).sort(reverse=True)[:10]])
        embed.add_field(name="Time Spent with Other Members (mins)", value=time_str)
    
    await ctx.send(embed=embed)

@bot.command()
async def reset(ctx):
    """Command to reset the stats."""
    global user_data, user_join_times, channel_members
    user_data = {}
    user_join_times = {}
    channel_members = {}
    save_data(user_data)  # Save the reset data
    await ctx.send("Stats have been reset.")

# Run the bot with your token
bot.run(TOKEN)