import discord 
import asyncio 
import subprocess 
import wavelink
from discord.ext import commands 
from discord import app_commands
import config
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    app.run(host='0.0.0.0', port=5001)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!" , intents=intents) 


@bot.event 
async def on_ready():
    print(f"Logged in as {bot.user}") 
    await bot.tree.sync()
    await wavelink.NodePool.create_node(bot=bot,
        host='localhost',  # or your Lavalink server
        port=2333,
        password='youshallnotpass',
        https=False
    )

@bot.event 
async def on_message(message: discord.Message):
    content =  message.content 

    print(content)
    
    if content.startswith("Hello"):
        await message.reply(f"Hi bro {message.author.mention}!")  
    

@bot.tree.command()
async def kill(interaction: discord.Interaction):
    await interaction.response.send_message(f"Killed {interaction.user.mention}")


@bot.tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command()
async def embed(interaction: discord.Interaction, message: str):
    embed = discord.Embed(title="MY LOVE ASHI💘", description="I LOVE YOU ASHI💗", color=discord.Color.red())
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1357703187569709218/1357703266196263075/Vm7MsSAHohTXZlzfjln1--1--o0s9e.jpg?ex=67f12b33&is=67efd9b3&hm=de9eb9fb0d8ae4422d5421d4cc9c03c944e0a93f596ad021469425a66e597a09&")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1357703187569709218/1357749363958349955/20250404_214019.gif?ex=67f15622&is=67f004a2&hm=f6711ab078fd3cfef065ae0f9f7686ec17cdd529327297a2b651e55eaabab5ce&")
    embed.set_footer(text="I LOVE YOU ASHI😘")
    embed.add_field(name="MY LOVE ASHI💗", value="I LOVE YOU ASHI", inline=True)
    embed.add_field(name="my love ashi", value="i love you ashi", inline=True)
    embed.add_field(name="MY LOVE ASHI", value="i love you ashi", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command()
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(thinking=True, ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Cleared {amount} messages!", ephemeral=True)


@clear.error
async def on_error(interaction: discord.Interaction, error: Exception):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("YOU DONT HAVE PERMISSION TO USE THIS COMMAND!", ephemeral=True)

    elif isinstance(error, commands.BotMissingPermissions):
        await interaction.response.send_message ("I DONT HAVE PERMISSIONS TO USE THIS COMMAND!", ephemeral=True)

Thread(target=run_flask).start()


@bot.tree.command()
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.mention}", ephemeral=True)
    await user.send(f"You have been kicked from {interaction.guild.name} for {reason}")

@bot.tree.command()
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user.mention}", ephemeral=True)
    await user.send(f"You have been banned from {interaction.guild.name} for {reason}")

@bot.tree.command()
@commands.has_permissions(ban_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    await interaction.response.send_message(f"Warned {user.mention}", ephemeral=True)
    await user.send(f"You have been warned in {interaction.guild.name} for {reason}")

@bot.event
async def on_ready():
    await wavelink.NodePool.create_node(
        bot=bot,
        host='localhost',  # Replace with your Lavalink host
        port=2333,
        password='youshallnotpass',
        https=False
    )
    print(f'Logged in as {bot.user}')

@bot.tree.command(name="play")
@app_commands.describe(query="Song to play")
async def play(interaction: discord.Interaction, query: str):
    vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)

    track = await wavelink.YouTubeTrack.search(query, return_first=True)
    await vc.play(track)
    await interaction.response.send_message(f"Now playing: {track.title}")


@bot.tree.command(name="stop", description="Stop the music and clear the queue.")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if not vc:
        await interaction.response.send_message("I'm not connected to a voice channel.")
        return

    if isinstance(vc, wavelink.Player):
        await vc.stop()
        vc.queue.clear()
        await interaction.response.send_message("Stopped playback and cleared the queue.")
    else:
        await interaction.response.send_message("Not a valid Lavalink player.")
        
@bot.tree.command()
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"Info: {member.name}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command()
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration)
    await interaction.response.send_message(f"Muted {member.mention} for {minutes} minutes.")
    
@bot.tree.command()
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"Unmuted {member.mention}.")

@bot.tree.command()
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color.green())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=guild.owner)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command()
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    await interaction.response.send_message(member.avatar.url)
    
@bot.tree.command()
async def say(interaction: discord.Interaction, *, message: str):
    await interaction.response.send_message(message)
    
@bot.tree.command()
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Info", color=discord.Color.blurple())
    embed.add_field(name="Name", value=bot.user.name)
    embed.add_field(name="ID", value=bot.user.id)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms")
    await interaction.response.send_message(embed=embed)
    
@bot.tree.command()
async def emojify(interaction: discord.Interaction, text: str):
    emoji_text = ""
    for char in text.lower():
        if char.isalpha():
            emoji_text += f":regional_indicator_{char}: "
        elif char.isdigit():
            emoji_text += f":{char}: "
        else:
            emoji_text += char
    await interaction.response.send_message(emoji_text)
    
    last_deleted = {}

@bot.event
async def on_message_delete(message):
    last_deleted[message.channel.id] = message

@bot.tree.command()
async def snipe(interaction: discord.Interaction):
    msg = last_deleted.get(interaction.channel.id)
    if msg:
        await interaction.response.send_message(f"Last deleted: {msg.author}: {msg.content}")
    else:
        await interaction.response.send_message("No message to snipe!")
    
bot.run(config.DISCORD_TOKEN)
