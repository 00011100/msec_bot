import discord
from discord.ext import commands
import logging
import sys
import orator
import yaml
from models.user import User


def setup(client):
  # Setup logging for sql queries
  logger = logging.getLogger('orator.connection.queries')
  logger.setLevel(logging.DEBUG)
  logger.addHandler(logging.StreamHandler(sys.stdout))

  
  # Initialize the orator config
  #db = orator.DatabaseManager( config["databases"] )
  #db.enable_query_log()
  #orator.Model.set_connection_resolver(db)
