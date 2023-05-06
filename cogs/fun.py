#!/usr/bin/python3

import discord
import logging
from discord.ext import commands, tasks
from random import randint, choice
from models.user import User
from cogs.currency import reward
from config import check_user
import config
import asyncio
import datetime
import sqlite3
import orator

# Logging
logger = logging.getLogger('msecBot')
logger.debug(f"Logging enabled from: {__name__}")

# Global
birdsGIF = ['https://media1.tenor.com/images/1a4df7245244fbde2c3d3568ac7ba8ec/tenor.gif',
            'https://media1.tenor.com/images/155d1e366cddc08311318859be93d76a/tenor.gif',
            'https://media1.tenor.com/images/b12ca193cb9136587f555d60a87634d8/tenor.gif',
            'https://media1.tenor.com/images/d5501fc60b0c75650a73d31848230fb3/tenor.gif',
            'https://media1.tenor.com/images/a84ac84c30b9196015d2cba9721c362c/tenor.gif']


class Fun(commands.Cog):
    """ This is where you can put all the goofy commands for gifs
        or other things that add a spark of personality. ;)    """

    def __init__(self, client):
        self.client = client
        self.flying = False
        self.random_bird.start()
        self.first_run = True

    @commands.command()
    async def profile(self, ctx):
        """ Print your profile stats"""

        user = User.where('client_id', ctx.author.id).get().first()
        xbed = discord.Embed(color= 0x800080)
        xbed.set_author(name= f"{ctx.author.name}'s profile",
                        icon_url= ctx.author.avatar_url)
        xbed.add_field(name= "Birds", value= user.birds, inline= True)
        xbed.add_field(name= "Carrots", value= user.carrots, inline= True)
        xbed.add_field(name= "Slapped", value= user.slapped, inline= True)
        xbed.add_field(name= "Currency", value= user.currency, inline= True)
        await ctx.send(embed= xbed)

    # Award a user a carrot

    @commands.command()
    async def carrot(self, ctx, member: discord.User):
        """ You can award someone a carrot every 24 hours! """

        # Prevent user from awarding themselves a carrot
        if ctx.author.id == member.id:

            xbed = discord.Embed(color= 0xFF0000)
            xbed.add_field(name= "Failed Carrot Award",
                           value= "You can't award yourself a carrot...")
            errormsg = await ctx.send(embed= xbed)
            await asyncio.sleep(3)
            await errormsg.delete()
            await ctx.message.delete()
            return

        try:
            # Check that user and receving users have database records
            check_user(ctx.author.id, ctx.author.name)
            check_user(member.id, member.name)

            # Create the user database objects for user and receving user
            user = User.where('client_id', ctx.author.id).get().first()
            rec_user = User.where('client_id', member.id).get().first()

            # calculate the timestamps for last_carrot award given,
            # The time of the current claim and the time for the next avaiable carrot
            last_carrot = datetime.datetime.strptime(
                user.last_carrot, '%Y-%m-%d %H:%M:%S')
            claim_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            claim = datetime.datetime.now().strptime(claim_str, "%Y-%m-%d %H:%M:%S")
            next_carrot = last_carrot - \
                datetime.timedelta(hours= config.carrot_wait)

            # If users has met the requirements for the wait time
            if claim >= next_carrot:

                # Print to console for logging
                logger.info(f"[{__name__}] {ctx.author.name} has given {member.name} a carrot!")

                # Update the timestamp for last carrot given and award user a carrot
                user.update(last_carrot= (claim))
                rec_user.update(carrots= (rec_user.carrots+1))

                # Build and send a message to channel
                xbed = discord.Embed(color= 0x00FF00)
                xbed.set_author(name= "Carrot Award",
                                icon_url= ctx.author.avatar_url)
                xbed.add_field(name= f":carrot:{ctx.author.name} awarded {member.name} a carrot!:carrot:",
                               value= f"\n\nTotal number of carrots {member.name} has been awarded: {rec_user.carrots}")
                xbed.set_footer(
                    text= "You can only award a carrot once every 24 hours.")
                await ctx.send(embed= xbed)

            else:
                # Calculate remaining time until user can award carrot
                remaining_time = next_carrot - claim

                # Print to console for logging
                logger.info(f"[{__name__}] {ctx.author.name} has to wait: {remaining_time} before giving another carrot!")

                # Build and send message to channel
                xbed = discord.Embed(color= 0xFF0000)
                xbed.add_field(name= "Failed Carrot Award", value= f"You must wait {remaining_time} before \
                you can give another carrot!")
                errormsg = await ctx.send(embed= xbed)
                await asyncio.sleep(5)
                await errormsg.delete()
                await ctx.message.delete()
                return

        # Print the SQL error to console
        except Exception as error:
            logger.error(repr(error))
            logger.error(repr(error.__class__))

    # Slap user with a large trout

    @commands.command()
    async def slap(self, ctx, member: discord.User):
        """ Bringing back some good memories from IRC. 
        Go on, slap someone silly with a wet trout. 
        Live a little. """

        check_user(ctx.author.id, ctx.author.name)
        check_user(member.id, member.name)
        try:
            user = User.where("client_id", member.id).get().first()
            if not user:
                user = User.create(client_id= member.id,
                                   username= member.name, slapped= 1)
                logger.info(f'[{__name__}] First time user {member.id} has been slapped!')

            # If record already exist, add 1 to slapped
            else:
                logger.info(f'[{__name__}] Adding slap to {member.name}')
                user.update(slapped= (user.slapped+1))
                # Print to console
                logger.info(f'[{__name__}] {member.name} has a total slap count of {user.slapped}')

        except Exception as er:
            logger.error(repr(er))
            logger.error(repr(er.__class__))

        # Send embed message
        xbed = discord.Embed(color= 0x800080)
        xbed.set_author(name= 'Slapped',
                        icon_url= "https://upload.wikimedia.org/wikipedia/commons/1/16/Rainbow_trout_transparent.png")
        xbed.add_field(name= f"Slapped with a large trout", value= f'{ctx.author.name} \
        slapped {member.mention} around a little bit with a large trout.')
        xbed.set_footer(
            text= f'Number of times {member.name} has been slapped: {user.slapped}')

        # Send embed and delete original cmd message
        await ctx.send(embed= xbed)
        await ctx.message.delete()

    # Random bird that randomly occurs within 2 to 12 hours
    @tasks.loop(minutes= randint(config.birdIntervalLow, config.birdIntervalHigh))
    async def random_bird(self):
        """Changes flying status to True, randomly selects a gif
           Creates and sends a embed with the gif. The user then
           has a certain amount of time to shoot the bird."""

        # Get time, format and store in timestamp
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")

        # Prevents random bird on startup
        if self.first_run:
            await asyncio.sleep(randint(config.birdDelayLow, config.birdDelayHigh))
            self.first_run = False

        logger.info(f"[{__name__}] Releasing a random bird: {timestamp}")
        general = self.client.get_channel(
            config.channel['general'])  # Channel ID for TEST
        self.flying = True
        # Bird GIF is selected from random choice
        bird = choice(birdsGIF)

        # Send embedded message to channel
        xbed = discord.Embed(color= 0xFF0000)
        xbed.add_field(name= 'A wild bird appears!',
                       value= "It looks like it's carrying something...")
        xbed.set_footer(text= 'Use ".bang" within 60 seconds.')
        xbed.set_image(url= bird)
        birdmsg = await general.send(embed= xbed)

        # 60 seconds to shoot or bird is deleted
        await asyncio.sleep(60)
        self.flying = False
        await birdmsg.delete()
        # self.random_bird.change_interval(minutes = randint(config.birdIntervalLow,config.birdIntervalHigh)) # launch again within 2 hours

    # The before_loop is a special command to ensure the loop doesn't run early
    @random_bird.before_loop
    async def before_random_bird(self):
        await self.client.wait_until_ready()

    # Command to shoot random flying bird
    @commands.command()
    async def bang(self, ctx):
        """If a user sends the command bang, add the score
           or make a key, then send the embed with the score
           and turn off flying so no one else can shoot."""
        check_user(ctx.author.id, ctx.author.name)
        # Capture and format timestamp from datetime
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")

        if self.flying:

            # Toggle flying boolean
            self.flying = False
            # Retrieve username and username id.
            # Capture and format timestamp from datetime
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M")
            # Prints to console, eventually logs
            logger.info(f'[{__name__}] User: {ctx.author.name} shot the bird - {timestamp}')

            try:

                user = User.where("client_id", ctx.author.id).get().first()

                if user.birds < 1:
                    user.update(birds= (user.birds+1),
                                last_bird= datetime.datetime.now())
                    print(
                        f'[+] User {ctx.author.name} has shot their first bird')
                    # await ctx.send(embed = xbed)
                    await reward(ctx, 500, "First Bird", 'You claimed your first bird!')

                else:
                    # If record already exist, increment bird count by one
                    user.update(birds= (user.birds+1),
                                last_bird= datetime.datetime.now())

            # debug
            # Sqlite error tracing debug block for console
            # except sqlite3.Error as er:
            #    print('SQLite error: %s' % (' '.join(er.args)))
            #    print("Exception class is: ", er.__class__)
            #    print('SQLite traceback: ')
            #    exc_type, exc_value, exc_tb = sys.exc_info()
            #    print(traceback.format_exception(exc_type, exc_value, exc_tb))

            except Exception as er:
                logger.error(repr(er))

            # Create embed message, send to channel, and turn off flying boolean.
            coins = randint(1, 500)
            logger.info(f'[{__name__}] {ctx.author.name} has shot a bird and looted {coins} coins')
            xbed = discord.Embed(color= 0x00ff00)
            xbed.add_field(
                name= f'{ctx.author.name} has dropped the bird!', value= f'Bird Count: {user.birds}')
            xbed.set_thumbnail(
                url= "https://cdn.iconscout.com/icon/premium/png-256-thumb/crosshair-57-408204.png")
            xbed.add_field(name= f"The bird was carrying...",
                           value= f"**{coins}** coins!", inline= False)
            xbed.set_footer(text= f'Last Bird: {user.last_bird} ')
            msg = await ctx.send(embed= xbed)
            await reward(ctx, coins, "Bird Loot", "Coins are falling from the sky!")
            await msg.delete()
            await ctx.message.delete()

            logger.debug(f'[{__name__}] flying is set to {self.flying}')

        # If bird is not flying, send you missed message
        else:
            xbed = discord.Embed(color= 0xff0000)
            xbed.add_field(name= f'{ctx.author.name}',
                           value= f'You missed and shot the air...')
            bangmsg = await ctx.send(embed= xbed)
            # 5 seconds before deleteing message from chat
            await asyncio.sleep(5)
            await bangmsg.delete()
            await ctx.message.delete()


# Loads the cog
def setup(client):
    client.add_cog(Fun(client))
