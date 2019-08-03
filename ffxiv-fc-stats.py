#!/usr/bin/env python3

# Written by computergeek125
# Originally created 02 AUG 2019
# See attached LICENSE file

import aiohttp
import argparse
import asyncio
import logging
from pprint import pprint
try:
    import xivapipy.xivapi as xivapi
except ImportError:
    import xivapi

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="Config to use", default="config.json")
#parser.add_argument("-w", "--world", help="World to search in", required=True)
#parser.add_argument("-f", "--free_company", help="Name of Free Company to find", required=True)
parser.add_argument("-i", "--id", help="ID of the Free Company to query", required=True)
#parser.add_argument("-s", "--since", help="Exclude members who haven't logged in in this many days", default=None)
parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level", default='INFO')

args = parser.parse_args()

config_file = args.config
config = {"api-key":None}

async def run(config, session, args):
    global fc
    global fcm
    global member_data
    try:
        if config['api-key'] is None:
            client = xivapi.Client(session=session, api_key="")
        else:
            client = xivapi.Client(session=session, api_key=config['api-key'])
        fc = await client.freecompany_by_id(args.id, include_freecompany_members=True)
        logging.info("Loaded free company \"{name}\" ({gc}): {slogan}"
            .format( name=fc["FreeCompany"]["Name"],
                     gc=fc["FreeCompany"]["GrandCompany"],
                     slogan=fc["FreeCompany"]["Slogan"]
            )
        )
        fcm = fc["FreeCompanyMembers"]
        member_data = {}
        for m in fcm:
            logging.info("Processing character id {id} with name {name}".format(id=m["ID"], name=m["Name"]))
            member_data[m["ID"]] = await client.character_by_id(m["ID"])
    except:
        logging.exception("An exception occured while contacting XIVAPI")
    finally:
        await session.close()

if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, args.logLevel), format='%(message)s', datefmt='%H:%M')

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    loop.run_until_complete(run(config, session, args))