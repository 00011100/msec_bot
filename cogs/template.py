#!/usr/bin/python3

import discord
from discord.ext import commands, tasks

# All commands and loops fall under the class
class Template(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    # For looped events
    @tasks.loop()
    async def loop_name(self):
        pass
    
    # For new commands
    @commands.command()
    async def testy(self, ctx, member : discord.User):
        pass

# Load the cog
def setup(client):
    client.add_cog(Template(client))
