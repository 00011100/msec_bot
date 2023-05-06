#!/usr/bin/python3

import discord
import orator
from discord.ext import commands, tasks, flags
from orator import DatabaseManager, Schema
from models.coffee import Coffee
from config import channel, check_user, db
import datetime
import asyncio
import textwrap
import logging
import sys
import pendulum


# Logging
logger = logging.getLogger('msecBot')
logger.debug(f"Logging enabled from: {__name__}")

# TODO Print caffeine table for each item in bev list
# TODO Print print today's caffeine
# TODO Print caffeine charts for highest
# TODO Print weekly and daily averages
# TODO Add cooldown timer / requires timestamp comparison
# TODO Send Rick Flair gif for new records over 200mg



# Image URLS for beverage thumbnails (will more than likely 404 with time)
bevimgs = {'coke':'https://cdn.shopify.com/s/files/1/1576/9979/products/CokeCan_1334x.png?v=1594893838',
        'coffee':'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Coffee_cup_icon.svg/1200px-Coffee_cup_icon.svg.png',
        'nitro':'https://i.pinimg.com/originals/e2/1b/3b/e21b3b384b6d0abe109232d3d93f14db.png',
        'tea':'https://assets.stickpng.com/images/580b57fcd9996e24bc43c54d.png',
        'dew':'https://assets.stickpng.com/images/587186d27b7f6103e35c6cc8.png',
        'energydrink':'http://pixelartmaker.com/art/2bc3984a24732f4.png'}

# All commands and loops fall under the class
class Caff(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    # All of the command flags for ingest
    @flags.add_flag("--caffeine", type= int, default= 0)
    @flags.add_flag("--type", type= str, default= None)
    @flags.add_flag("--undo", action= "store_true")
    @flags.add_flag("--help", action= "store_true")
    @flags.command()

    async def ingest(self, ctx, **flags):
        """For recording your consumption of awesomeness - FlyPhish"""

        check_user(ctx.author.id, ctx.author)

        # Ensure this command can only be ran from the coffee channel
        if ctx.message.channel.id != channel['coffee']:
            xbed = discord.Embed(color= 0xFF0000)
            xbed.add_field(name= "Error Msg", value= "This caffeine command can only be ran from the coffee channel!")
            errormsg = await ctx.send(embed= xbed)
            await asyncio.sleep(3)
            await errormsg.delete()
            await ctx.message.delete()
            return

        # Presets for beverages with their respective avg caffeine content
        bev = {'coffee': 80,'nitro': 280,'tea': 30,'coke': 32,'dew': 54,'energydrink': 160}

        # Set variables based on passed args
        if flags['type']:
            amt = bev[flags['type']]
            bevtype = flags['type']

        if flags['caffeine']:
            amt = flags['caffeine']
        
        # For whatever reason this help bool flag needs an argument
        if flags['help']:
            
            help_str = """
            **--caffeine** - Change the caffeine ammount for the type\n \
            **--type** - Change the type of coffee\n \
            **--undo** - Erase your last entry \n \
            **--help** - Display this help screen\n \
            **.caffchart** - Show your caffeine chart""".lstrip()

            xbed = discord.Embed(color= 0x00FF00)
            xbed.set_author(name= "Caffeine Tracker", icon_url= "https:///content/images/2020/06/LogoPNG-small-1.png")
            xbed.add_field(name= "Summary", value= "There are several beverage type presets, each with their own preset caffeine content\
            which can be overwritten with the **'--caffeine'** option in case you would like to make adjustments for your particular \
            beverarge ", inline= False)
            xbed.add_field(name= "Cofee Types", value= "***coffee*** [80mg], ***nitro***[280mg], ***tea***[30mg],\
             ***coke***[32mg], ***dew***[54mg], ***energydrink***[160mg]", inline= False)
            xbed.add_field(name= "Examples", value= "**1)** *.ingest  --type coffee*\n**2)** *.ingest  --type coffee  --caffeine 90*", inline= False)
            xbed.add_field(name= "Commands", value= textwrap.dedent(help_str.strip()), inline= False)
            await ctx.send(embed= xbed)


        if flags['undo']:
            try:
                caff_obj = db.table('caffeine').select("*").where('username', ctx.author.name).order_by("created_at","DESC").get().first()
                caff_type = caff_obj['caff_type']
                caff_id = caff_obj["id"]
                caff_date = caff_obj['created_at']
                caff_amt = caff_obj['caff_amt']
                db.table('caffeine').where("id",caff_obj['id']).delete() 
                logger.warning(f"[{__name__}] {ctx.author.name} has deleted rec-id {caff_id}: {caff_type}|{caff_amt}|{caff_date}")
        
                xbed = discord.Embed(color= 0xFF0000)
                xbed.add_field(name= "Deleted Last Entry", value= f"Successfully deleted last record")
                xbed.add_field(name= "Type", value= f"**{caff_type}**", inline= False)
                xbed.add_field(name= "Caffeine Ammount", value= f"**{caff_amt}**", inline= False)
                xbed.add_field(name= "Entry Date", value= f"**{caff_date}**", inline= False)
                xbed.set_thumbnail(url= "https://upload.wikimedia.org/wikipedia/en/thumb/b/ba/Red_x.svg/120px-Red_x.svg.png")
                caff_msg = await ctx.send(embed= xbed)

                await asyncio.sleep(10)
                await caff_msg.delete()      
                await ctx.message.delete()
                return

            except Exception as e:

                xbed = discord.Embed(color= 0xFF0000)
                xbed.add_field(name= "Error Message", value= f"You currently do not have any records at this time.")
                caff_msg = await ctx.send(embed= xbed)
                await asyncio.sleep(5)
                await caff_msg.delete()      
                await ctx.message.delete()
        try:
            # Create a new caffeine record
            logger.info(f"[{__name__}]{ctx.author.id} entered a new caffeine record")
            Coffee.create(client_id= ctx.author.id, username= ctx.author.name, caff_type= bevtype, caff_amt= amt)

        except:
           return

        # Send the embedded msg for ingest command
        logger.info(f"[{__name__}] {ctx.author.name} ingested {bevtype} for {amt}mg of caffeine")
        xbed = discord.Embed(color= 0x00FF00)
        xbed.set_author(name= "Caffeine Ingested", icon_url= ctx.author.avatar_url)
        if amt > 200:
            xbed.set_thumbnail(url= "https://media.tenor.com/images/2604ac2d8be9df6934ad32b76e402ea0/tenor.gif")
            xbed.add_field(name="WOOOOO!", value= f"**{ctx.author.name}** just ingest a **{bevtype}** with **{amt}mg** of caffeine! ***WOO!***")
        else:  
            xbed.set_thumbnail(url= bevimgs[bevtype])
            xbed.add_field(name="Ingested", value= f"**{ctx.author.name}** just ingest a **{bevtype}** with **{amt}mg** of caffeine!")
        
        xbed.set_footer(text= "For Help Use:  .ingest --help")
        await ctx.send(embed= xbed)


        
    @commands.command()
    async def caffchart(self, ctx):
        """Display your caffeine chart"""
        
        # Ensure command can only be ran in coffee channel
        if ctx.message.channel.id != channel['coffee']:

            xbed = discord.Embed(color= 0xFF0000)
            xbed.add_field(name= "Error Msg", value= "This caffeine command can only be ran from the coffee channel!")
            errormsg = await ctx.send(embed= xbed)
            await asyncio.sleep(3)
            await errormsg.delete()
            await ctx.message.delete()
            return

        try:
            # Get the amount and count grouped by caff_type
            caff_type_counts = db.table('caffeine') \
              .select(db.raw("caff_type, count(*) as count, sum(caff_amt) as amount")) \
              .where('client_id', ctx.author.id) \
              .group_by("caff_type") \
              .order_by( db.raw( "count" ), "DESC" ).get()

            # Get the top weekly caffiene drinkers
            client_id_week_counts = db.table('caffeine') \
              .select(db.raw("username, client_id, count(*) as count, sum(caff_amt) as amount")) \
              .where(db.raw( "strftime('%W %Y', created_at)"), db.raw("strftime('%W %Y', datetime('now','localtime')) " ) ) \
              .group_by("client_id") \
              .order_by( db.raw( "amount" ), "DESC" ) \
              .limit(3).get()

            # Get the top daily caffiene drinkers
            client_id_day_counts = db.table('caffeine') \
              .select(db.raw("username, client_id, count(*) as count, sum(caff_amt) as amount") ) \
              .where(db.raw( "strftime('%j %Y', created_at)"), db.raw("strftime('%j %Y', datetime('now','localtime')) " ) ) \
              .group_by("client_id") \
              .order_by( db.raw( "amount" ), "DESC" ) \
              .limit(3).get()



        except Exception as e:
          exc_type, exc_obj, exc_tb = sys.exc_info()
          logger.warning(str(e))
          logger.warning(str(e.__class__))
          logger.warning(exc_tb.tb_lineno)
          logger.error(f"[{__name__}] [caffchart] Failed to get records "  + repr(e))

        # Average Caffeine
        try:
            rec_avg = db.table('caffeine').where('client_id', ctx.author.id).avg("caff_amt") or 0
            rec_avg_week = db.table('caffeine').where('client_id', ctx.author.id).where_raw( "created_at > ?", pendulum.now("utc").subtract(weeks=1)  ).avg("caff_amt") or 0
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(str(e))
            logger.warning(str(e.__class__))
            logger.warning(exc_tb.tb_lineno)
            logger.warning(f"[{__name__}] No average: {ctx.author.id}")

        try:
            # Send embedded values
            xbed = discord.Embed(color= 0x00FF00)
            xbed.set_author(name= "Caffeine Chart", icon_url= ctx.author.avatar_url)
            labels = { 1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}

            if len(caff_type_counts) > 0:
                xbed.add_field(name= "Lets have a look", value= f"Here is a brief summary for **{ctx.author.name}**")
                for idx, caff_type_count in enumerate( caff_type_counts ):
                    xbed.set_thumbnail(url= bevimgs[ caff_type_count["caff_type"] ])
                    xbed.add_field( name=labels[ idx+1 ], value=f"**{caff_type_count['caff_type'].capitalize()}** with a total of: **{caff_type_count['amount']}mg**", inline=False)

            ## Provide the average caffeine content from all records
            xbed.add_field(name= "Average Caffeine", 
            value= f"Your total average intake is: ***{int(rec_avg)}mg of caffeine!***", inline= False)
            xbed.add_field(name= "Average Caffeine", 
            value= f"Your weekly average intake is: ***{int(rec_avg_week)}mg of caffeine!***", inline= False)


            if len(client_id_week_counts) > 0:
                xbed.add_field(name= "Weekly", value= f"Top Weekly Caffiene Drinkers", inline=False)
                for idx, client_id_week_count in enumerate( client_id_week_counts ):
                    xbed.add_field( name=labels[ idx+1 ], value=f"**{client_id_week_count['username']}** with a total of: **{client_id_week_count['amount']}mg**", inline=True)

            if len(client_id_day_counts) > 0:
                xbed.add_field(name= "Daily", value= f"Today's Caffiene Drinkers", inline=False)
                for idx, client_id_day_count in enumerate( client_id_day_counts ):
                    xbed.add_field( name=labels[ idx+1 ], value=f"**{client_id_day_count['username']}** with a total of: **{client_id_day_count['amount']}mg**", inline=True)



            msg = await ctx.send(embed= xbed)
            await asyncio.sleep(120)
            await msg.delete()
            await ctx.message.delete()


            if len(caff_type_counts) == 0:
                xbed = discord.Embed(color= 0xFF0000)
                xbed.set_author(name= "What?!", 
                icon_url= ctx.author.avatar_url)
                xbed.add_field(name= "Error", 
                value="You haven't even ingested anything yet!")
                errormsg = await ctx.send(embed= xbed)
                await asyncio.sleep(3)
                await errormsg.delete()      
                await ctx.message.delete()

        except Exception as e:
          exc_type, exc_obj, exc_tb = sys.exc_info()
          logger.warning(str(e))
          logger.warning(str(e.__class__))
          logger.warning(exc_tb.tb_lineno)

          logger.warning(f"[{__name__}] Error: {ctx.author.id}")
          


# Load the cog
def setup(client):
    client.add_cog(Caff(client))
