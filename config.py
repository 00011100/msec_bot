#!/usr/bin/python3
#
# Store your bot's token in a text file called BOT_TOKEN
#
# Get your token here https://discord.com/developers/applications
# Get your chat channel by right-clicking a channel, grabbing ID
import logging
import orator
import datetime
from orator import DatabaseManager, Schema
from models.user import User

# Logging
logger = logging.getLogger('msecBot')
logger.debug(f"Logging enabled from: {__name__}")

######################################
#   CONFIGURE BOT CHANNELS AND TOKEN
######################################

# Attempt to load bot token from a local file named BOT_TOKEN
try:
    botToken = open('BOT_TOKEN','r').read()

except FileNotFoundError as e:
    logger.error(f"[{__name__}] file BOT_TOKEN does not exist: {e}")
    exit(1)

# Set the channel integers here
channel = {'general':622800609564688389,'ctf':625823802592591872,
        'coffee':796450946157641829,'bots':798338301269639198,
        'debug':798310627851501570}

# Ensure each channel provided is a int
for chanid in channel.values():
    try:
        if type (chanid) != int:
            logger.warning("[{__name__}] Invalid BOT_CHANNEL: %s" % (chanid  or  "[-] No channel entered"))
            quit(1)
    except:
        logger.debug(f"[{__name__}] All channels are verified integers")



######################################
#   LOAD SQL MODEL CONFIGURATION
######################################

db = DatabaseManager({"default": {"driver":"sqlite", "database":"database/main.db"}})
orator.Model.set_connection_resolver(db)



######################################
#   CONFIGURE CONFIG SETTINGS HERE
######################################

birdIntervalLow = 2880 # 2 days
birdIntervalHigh = 20160 # 2 weeks
birdDelayLow = 7200
birdDelayHigh = 43200
claim_wait = -24
carrot_wait = -24



######################################
#      CONFIGURATION FUNCTIONS
######################################

def check_user(cid, name):

    logger.debug(f"[{__name__}][check_user] Verifying user {cid} exists")
    user = User.where( "client_id", cid ).get().first()

    if user:
        logger.info(f"[{__name__}][check_user] Verified that user {name} has a record")
        return
        
    try:
        date = datetime.datetime(1999, 1, 1, 11, 11, 11).strftime("%Y-%m-%d %H:%M:%S")

        if not user:

            date = datetime.datetime(1999, 1, 1, 11, 11, 11).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{__name__}][check_user] No record has been found for id: {cid}")
            user = User.create(client_id= cid, birds= 0, carrots= 0, slapped= 0,
            last_bird= date, currency= 0, last_curclaim= date, last_carrot= date,
            username= name)
            logger.info(f"[{__name__}][check_user] Record has been created for {name}")

        if not user.last_curclaim:

            date = datetime.datetime(1999, 1, 1, 11, 11, 11).strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{__name__}] Adding last_curclaim default date for {name}")
            user.last_curclaim= date
            user.save()

        else:
            logger.info(f"[{__name__}] Verified that user {name} has a record")

    except Exception as error:

        logger.error(repr(error))
        logger.error(repr(error.__class__))



# Function to verify / create db and table
def check_db():
    """ Checks to see if database exists, other wise
        a database in created in the specified location."""

    # Configuration to load or create database
    config = {
        'sqlite3': {
            'driver':'sqlite',
            'database':'database/main.db'}
            }

    # Establishing connection to DB
    db = DatabaseManager(config)
    # Establish Schema instance
    schema = Schema(db)

    # if tables does not exist, create it
    if not schema.has_table('users'):
        logger.warning("[{__name__}] 'users' table not found")
        logger.warning("[{__name__}] Creating user's table...")

        try:
            with schema.create('users') as table:
                table.increments('id')
                table.text('username')
                table.integer('client_id')
                table.datetime('created_at')
                table.datetime('updated_at')
                table.integer('birds')
                table.datetime('last_bird')
                table.integer('carrots')
                table.datetime('last_carrot')
                table.integer('currency')
                table.datetime('last_curclaim') 
                table.integer('slapped')

        except Exception as error:
            logger.error(repr(error))
            logger.error(repr(error.__class__))

    if not schema.has_table('caffeine'):
        logger.warning("[{__name__}]'caffeine' table not found")
        logger.warning("[{__name__}] Creating caffeine table...")

        try:
            with schema.create('caffeine') as table:
                table.increments('id')
                table.text('username')
                table.integer('client_id')
                table.datetime('created_at')
                table.datetime('updated_at')
                table.text('caff_type')
                table.integer('caff_amt')
                
        except Exception as error:
            logger.error(repr(error))
            logger.error(repr(error.__class__))
        

    else:
        logger.info("[{__name__}] Database has been found")

# Check for database        
check_db()
