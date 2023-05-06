#!/usr/bin/python3

from discord.ext import commands, tasks
from models.user import User
from config import check_user
import discord
import asyncio
import datetime
import orator
import config
import logging

# Logging
logger = logging.getLogger('msecBot')
logger.debug(f"Logging enabled from: {__name__}")

async def reward(ctx, coins, title, msg):  
    user = User.where('client_id', ctx.author.id).get().first()
    user.update(currency= (user.currency+coins))
    xbed = discord.Embed(color= 0x00ff00)

    xbed.set_author(name= title, icon_url=ctx.author.avatar_url)
    xbed.set_thumbnail(url= "https://www.shareicon.net/data/2015/05/17/39779_safe_400x400.png")
    xbed.add_field(name= f"{coins} Coins Deposited", value= f"**Reason:** {msg}")
    msg = await ctx.send(embed= xbed)
    await asyncio.sleep(60)
    await msg.delete()
    await ctx.message.delete()


# All commands and loops fall under the class
class Coins(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def claim(self, ctx):
        try:
            # Check if user has record else create
            check_user(ctx.author.id, ctx.author.name)
            logger.info(f'[{__name__}] {ctx.author.name} is attempting to claim.')
            user = User.where('client_id', ctx.author.id).get().first()

            # Compare time stamps to to last claim and current claim attempt
            last_curclaim = datetime.datetime.strptime(user.last_curclaim, '%Y-%m-%d %H:%M:%S')
            claim_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            claim = datetime.datetime.now().strptime(claim_str,"%Y-%m-%d %H:%M:%S")
            next_buy = last_curclaim - datetime.timedelta(hours= config.claim_wait)

            # If claim is available 
            if claim >= next_buy:
               
                logger.info(f"[{__name__}] User {ctx.author.name} successfuly claimed their money")

                # update currency
                user.update(currency= (user.currency+100))
                user.update(last_curclaim= (claim))

                # Build embedded message
                xbed = discord.Embed(color= 0x00ff00)
                xbed.set_author(name="Daily Deposit", icon_url=ctx.author.avatar_url)
                xbed.set_thumbnail(url= "https://www.shareicon.net/data/2015/05/17/39779_safe_400x400.png")
                xbed.add_field(name= f"100 Coins Deposited", value= f"Here you go {ctx.author.name}! Come back tomorrow!")

                # Send message then delete after 60 seconds
                claimmsg = await ctx.send(embed= xbed)
                await asyncio.sleep(60)
                await claimmsg.delete()      
                await ctx.message.delete()

            else:
                # Display the remaining time until user can buy
                remaining_time = next_buy - claim
                xbed = discord.Embed(color= 0xff0000)
                xbed.add_field(name= f"{ctx.author.name}", value= f"You have to wait: **{remaining_time}** before you can claim again!")

                # Send and delete error message
                errormsg = await ctx.send(embed= xbed)
                await asyncio.sleep(5)
                await errormsg.delete()      
                await ctx.message.delete()

                logger.info(f"[{__name__}] User {ctx.author.name} has to wait: {remaining_time}")

        except Exception as error:
            logger.error(repr(error))
            logger.error(repr(error.__class__))



    @commands.command()
    async def balance(self, ctx):

        check_user(ctx.author.id, ctx.author.name)

        try:
            logger.info(f"[{__name__}] Checking balance for user {ctx.author.name}")

            # Get user object from SQL DB
            user = User.where('client_id', ctx.author.id).get().first()

            # If user has coins
            if user.currency > 0:
                xbed = discord.Embed(color= 0x00ff00)
                xbed.set_author(name="Currency Balance", icon_url= ctx.author.avatar_url)
                xbed.add_field(name= f"{ctx.author.name}", value= f"You currently have **{str(user.currency)}** coins!")
                xbed.set_thumbnail(url= "http://clipartmag.com/images/cartoon-coins-14.png")
                balancemsg = await ctx.send(embed= xbed)
                await asyncio.sleep(10)
                await balancemsg.delete()      
                await ctx.message.delete()

            # If user has no coins
            else:
                xbed = discord.Embed(color= 0xff0000)
                xbed.set_author(name="Currency Balance", icon_url= ctx.author.avatar_url)
                xbed.set_thumbnail(url= "http://www.getcadrplus.com/images/1180/images/Broken-Piggy-Bank.png")
                xbed.add_field(name= f"{ctx.author.name}", value= f"oh no!... You're broke!")
                xbed.set_footer(text= "Use the command .claim to get your daily coins or shoot a bird!")
                balancemsg = await ctx.send(embed= xbed)
                await asyncio.sleep(10)
                await balancemsg.delete()      
                await ctx.message.delete()


        except Exception as error:
            logger.error(repr(error))
            logger.error(repr(error.__class__))


# Load the cog
def setup(client):
    client.add_cog(Coins(client))
