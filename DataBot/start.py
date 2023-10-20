import discord, base64, requests
from discord.ext import commands
import os
from datetime import datetime
import asyncio


bot = commands.Bot(command_prefix='!')


# Global Variablen 
allowed_user_ids = []
owner_id = YOURUSERID # Initialisieren
    
log_channel_id = LOGCHANNELID  # Log Channel halt amk

def is_allowed_user(ctx):
    return ctx.author.id in allowed_user_ids

def is_owner(ctx):
    return ctx.author.id == owner_id

@bot.event
async def on_ready():
    print('Data loaded.')
    await bot.change_presence(activity=discord.Game(name="Killing victims with Bad OPSEC"))

@bot.command()
async def addvictim(ctx):
    if ctx.author.id != owner_id:
        await asyncio.sleep(5)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} you have no perms for that!")
        return

    await ctx.send("Type in the Name of the Person:")
    name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await ctx.send("Type in the Info you have about them:")
    infotext = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    filename = name.content + ".txt"
    with open(filename, 'w') as file:
        file.write(infotext.content)
        file.write("\n\nAdded at: " + datetime.now().strftime("%d.%m.%Y  %H:%M:%S "))

    await ctx.send(f"The info for {name.content} has been added.")
    await log_command_usage(ctx, "maskehinzufügen", name.content)

@bot.command()
async def removevictim(ctx):
    if ctx.author.id != owner_id:
        await asyncio.sleep(5)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} You have no Permission to do that!")
        return

    await ctx.send("Type in the Name of the victim you want to remove:")
    name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    filename = name.content + ".txt"

    if os.path.exists(filename):
        destination_folder = "deletedbackup"
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        new_location = os.path.join(destination_folder, filename)
        os.rename(filename, new_location)
        await ctx.send(f"The victim with the Name {name.content} was deleted.")
        await log_command_usage(ctx, "maskeentfernen", name.content)
    else:
        await ctx.send(f"The victim with the name {name.content} doesnt exist.")

@bot.command()
 
async def victiminfo(ctx):
    if ctx.author.id != owner_id:
        await asyncio.sleep(5)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} You have no Permission to do that!")
        return
    
    await ctx.send("Give in the Name of the victim you want Info about:")
    name_message = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    name = name_message.content
    filename = name + ".txt"
    
    loading_emoji_id = "" # put in here
    loading_message = await ctx.send(f"Loading...")
    
    await asyncio.sleep(1)  # Wait 1sec

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            infotext = file.read()

        info_message = f"🔓 **Information for {name}:**\n```{infotext} ```"
        await loading_message.edit(content=info_message)
        await log_command_usage(ctx, "victiminfo", name)
    else:
        await loading_message.edit(content=f"The victim called {name} doesnt exist.")


@bot.command()
 
async def victimlist(ctx):
    if ctx.author.id != owner_id:
        await asyncio.sleep(5)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} You have no Permission to do that!")
        return
        
    ignored_files = ["allowed_users.txt", "ownerid.txt"]
    files = [f[:-4] for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt') and f not in ignored_files]
    if files:
        masken_anzahl = len(files)
        file_list = '\n'.join(files)

        embed = discord.Embed(title="Data-Storage:", color=discord.Color.dark_gray())
        embed.add_field(name="victimlist", value=f"```\n{file_list}\n```")
        embed.set_footer(text=f"A total of ({masken_anzahl}) victims.")
        embed.add_field(name="Commanduser:", value=f"``  {ctx.author.name}  ``")

        await ctx.send(embed=embed)
        await log_command_usage(ctx, "victimlist")
    else:
        await ctx.send("There are no victims in here.")
        
        
@bot.command()
 
async def editvictim(ctx):
    if ctx.author.id != owner_id:
        await asyncio.sleep(5)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} You have no Permission to do that!")
        return
    await ctx.send("Type in the name of the victim you want to edit::")
    name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    filename = name.content + ".txt"

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            existing_text = file.read()

        await ctx.send("Type in the new Text:")
        new_text = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        with open(filename, 'w') as file:
            file.write(new_text.content)
            file.write("\n\nEdited at: " + datetime.now().strftime("%d.%m.%Y at %H:%M:%S"))

        await ctx.send(f"The info of the victim {name.content} was edited succesfully.")
        await log_command_usage(ctx, "maskebearbeiten", f"{name.content} - New Text: {new_text.content}")
    else:
        await ctx.send(f"The victim with the name {name.content} doesnt exist.")


@bot.command()
async def commands(ctx):
    message = """
    **Commands of the victimbank:**
   **!addvictim** - Wait till the Bot asks you for a Name and then give in Name and Info.
   **!victimlist** - Shows the current list of victims.
   **!removevictim** - Wait for Bot response then give in the name.
   **!editvictim** - Wait for Bot Response then edit the victim.
   **!victiminfo** - Wait for Bot Response then type in the name.
   **!done** - Do this when you are done.
    """
    await ctx.send(message)
    
    
    
@bot.command()
 
async def done(ctx):
    if ctx.author.id != owner_id:
        await asyncio.sleep(5)
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.mention} You have no Permission to do that!")
        return

    channel = ctx.channel
    await channel.purge()
    await log_command_usage(ctx, "done")

@victiminfo.error
@removevictim.error
@victimlist.error
@editvictim.error
@bot.event

async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} This Command doenst exist!")


async def log_command_usage(ctx, command_name, additional_info=""):
    log_channel = bot.get_channel(log_channel_id)
    timestamp = datetime.now().strftime("%d.%m.%Y at %H:%M:%S local Time of the Machine this runs on")
    user = ctx.author
    log_message = f"```ini\n[{timestamp}] {user} used this Command: '{command_name}'"
    if additional_info:
        log_message += f"\n{additional_info} was looked at."
    log_message += "```"
    await log_channel.send(log_message)


bot.run('YOURTOKEN')


