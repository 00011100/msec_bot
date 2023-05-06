#!/usr/bin/python3
#
# MSEC Official Bot 
# Version: 0.8
# Authors: MSEC Community
# Last version update: 3/23/2021
############################################################

import discord
import asyncio
from random import randint
from discord.ext import commands, tasks
from itertools import cycle
from os import listdir
import sqlite3
import config
import logging
import logging.handlers

# Logging 
logger = logging.getLogger('msecBot')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/msecBot_all.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter(f'%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
rotator = logging.handlers.RotatingFileHandler('logs/msecBot_all.log', maxBytes=1000000, backupCount=5)
logger.addHandler(rotator)
logger.addHandler(ch)
logger.addHandler(fh)

logger.debug(f"Logging enabled from: {__name__}")


# Global Variables
ver = 'v0.8'
status = cycle(['with fire', 'Hack the Gibson 3000', 'dead'])

logging.info('Log Started')

# Bot client
client = commands.Bot(command_prefix= ".")

# Load all cogs during startup
for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
    else:
        print(f'Unable to load {filename[:-3]}')



# When connected to server
@client.event
async def on_ready():
    """ When bot comes online, change status. Send online message."""

    # Start the bot status messages
    change_status.start()
    # Select channel ID from config dict 
    general_channel = client.get_channel(config.channel['bots'])
    
    # Create msecBot online message
    xbed = discord.Embed(color= 0x00FF00)
    xbed.set_author(name=f'msecBot Online {ver}',
    icon_url = "https:///content/images/2020/06/LogoPNG-small-1.png")
    xbed.add_field(name= "Change Log", value="\nCoffee ingest entries are no longer deleted\nDeleted Github cog\nCaffchart formatting")
    xbed.set_footer(text= f'Last Update: 3/23/2021')
    await general_channel.send(embed= xbed)



# Command that loads a cog specified by admins
@client.command()
async def load(ctx, extension):
    """ Load bot cog extension """
    
    # Capture all the roles the user is apart of
    role_names = [role.name for role in ctx.author.roles]

    if 'Admin' in role_names:
        client.load_extension(f'cogs.{extension}')
        logging.warning(f'[+] Loading cog extension: {extension}')
        xbed = discord.Embed(color= 0x00FF00)
        xbed.add_field(name= "Loading Cog", value= f'[+] Loading Cog extension: {extension}')
        xbed.set_footer(text= f'Command ran by: {ctx.author.name}')
        xbed.set_footer(text= ctx.author.name)
        await ctx.send(embed= xbed)

    else:
        xbed = discord.Embed(color= 0xFF0000)
        xbed.add_field(name= "Admin Function", value= f'[-] You cannot manipulate cog extensions at this time.')
        errmsg = await ctx.send(embed= xbed)
        await asyncio.sleep(3)
        await errmsg.delete()



# Command to unload a cog specified by admins
@client.command()
async def unload(ctx, extension):
    """ Unload bot cog extension"""

    role_names = [role.name for role in ctx.author.roles]

    if 'Admin' in role_names:
        client.unload_extension(f'cogs.{extension}')
        logging.warning(f'[-] Unloading cog extension: {extension}')
        xbed = discord.Embed(color= 0xFF0000)
        xbed.add_field(name= "Unloading Cog", value= f'[-] Unloading Cog extension: {extension}')
        xbed.set_footer(text= f'Command ran by: {ctx.author.name}')
        await ctx.send(embed= xbed)
     
    else:
        xbed = discord.Embed(color= 0xFF0000)
        xbed.add_field(name= "Admin Function", value= f'[-] You cannot manipulate cog extensions at this time.')
        errmsg = await ctx.send(embed= xbed)
        await asyncio.sleep(3)
        await errmsg.delete()


# Commands to reload a cog specfied by admins
@client.command()
async def reload(ctx, extension):
    """ Reload bot cog extension"""

    role_names = [role.name for role in ctx.author.roles]

    if 'Admin' in role_names:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        xbed = discord.Embed(color= 0x00FF00)
        xbed.add_field(name= "Reloading Cog", value= f'[+] Reloading Cog extension: {extension}')
        xbed.set_footer(text= f'Command ran by: {ctx.author.name}')
        xbed.set_footer(text= ctx.author.name)
        await ctx.send(embed= xbed)

    else:
        xbed = discord.Embed(color= 0xFF0000)
        xbed.add_field(name= "Admin Function", value= f'[-] You cannot manipulate cog extensions at this time.')
        errmsg = await ctx.send(embed= xbed)
        await asyncio.sleep(3)
        await errmsg.delete()



# Send message anytime a user does not provide a required arg.
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        xbed = discord.Embed(color= 0xFF0000) 
        xbed.add_field(name= "Error - Missing Argument", value= "[-] Please provide an argument for this command.")
        errormsg = await ctx.send(embed= xbed)
        await asyncio.sleep(3)
        await errormsg.delete()      
        await ctx.message.delete()


# Print the version number of msecBot
@client.command(name= 'version')
async def version(context):
    """ This is a command to check the current running version of the MSEC bot """

    await context.message.channel.send(ver)

# Change the status ever 4 hours
@tasks.loop(hours= 4)
async def change_status():
    await client.change_presence(activity= discord.Game(next(status)))

# Run the bot    
client.run(config.botToken)
