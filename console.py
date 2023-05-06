#!/usr/bin/python3
import orator
import yaml
import logging
import sys
import pdb
from models.user import User

#setup logging
logger = logging.getLogger('orator.connection.queries')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

#setup orator
config = yaml.load( open("database/orator.yml"), Loader=yaml.FullLoader )
db = orator.DatabaseManager( config["databases"] )
db.enable_query_log()
orator.Model.set_connection_resolver(db)

# break
pdb.set_trace()
