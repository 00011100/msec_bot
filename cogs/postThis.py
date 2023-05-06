#!/usr/bin/python3

import discord
from discord.ext import commands, tasks
import logging

logger = logging.getLogger('msecBot')
logger.debug(f"Logging enabled from: {__name__}")

# All commands and loops fall under the class
class postThis(commands.Cog):

    def __init__(self, client):
        self.client = client

    @flags.add_flag("--messageId", type= int)
    @flags.add_flag("--title", type= str)
    @flags.add_flag("--help", action= "store_true")
    @flags.command()


    
    @commands.command()
    async def postThis(self, ctx, **flags):
        if flags['help']:
            help_str = """
            **--messageId** - Get one from righht-clicking oon the message yuo want to post\n \
            **--title** - Titlle of the post""".lstrip()

            xbed = discord.Embed(color= 0x00FF00)
            xbed.set_author(name= "Forum helper")
            xbed.add_field(name= "Summary", value= "Helps get our form active by combining forum and discord ", inline= False)
            xbed.add_field(name= "Commands", value= textwrap.dedent(help_str.strip()), inline= False)
            await ctx.send(embed= xbed)

        # Required fields
        if not flags['messageId'] or not flags['title']:
            return
        
        msg_body_raw = await ctx.fetch_message(flags['messageId'])
        post_title = flags['title']
        logger.debug(f"Posting with title {post_title}")

        import requests
        import json

        url = "https:///posts.json"

        payload = json.dumps({
          "title": post_title,
          "raw": msg_body_raw
        })

        headers = {
          'Content-Type': 'application/json',
          'Api-Key': '',
          'Api-Username': ''
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        logger.debug(f"{response.text} -- Forum helper")



# Load the cog
def setup(client):
    client.add_cog(postThis(client))
