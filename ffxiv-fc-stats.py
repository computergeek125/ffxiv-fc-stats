#!/usr/bin/env python3

# Written by computergeek125
# Originally created 02 AUG 2019
# See attached LICENSE file

import aiohttp
import argparse
import asyncio
import json
import logging
import matplotlib
import matplotlib.pyplot as plt
from pprint import pprint
import ratelimit
import time
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
parser.add_argument("-o", "--out", help="filename to write to. If none, will attempt use GUI", default=None)
parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level", default='INFO')

args = parser.parse_args()

with open(args.config) as config_file:
    config = json.load(config_file)
matplotlib.style.use(config["mpl-style"])

@ratelimit.limits(config["rate-limit"], config["rate-limit-window"])
def api_call_int(call, *args, **kwargs):
    return call(*args, **kwargs)

def api_call(call, *args, **kwargs):
    while True:
        try:
            return api_call_int(call, *args, **kwargs)
        except ratelimit.RateLimitException:
            logging.warning("Rate limit exceeded. Sleeping for {t}s.".format(t=config["rate-limit-window"]))
            time.sleep(config["rate-limit-window"])

def char_max_level(character):
    levels = []
    cj = character["Character"]["ClassJobs"]
    for c in cj.keys():
        levels.append(cj[c]["Level"])
    return max(levels)

async def run(config, session, args):
    global fc
    global fcm
    global member_data
    global levels
    try:
        if config['api-key'] is None:
            client = xivapi.Client(session=session, api_key="")
        else:
            client = xivapi.Client(session=session, api_key=config['api-key'])
        fc = await api_call(client.freecompany_by_id, args.id, include_freecompany_members=True)
        logging.info("Loaded free company \"{name}\" ({gc}): {slogan}"
            .format( name=fc["FreeCompany"]["Name"],
                     gc=fc["FreeCompany"]["GrandCompany"],
                     slogan=fc["FreeCompany"]["Slogan"]
            )
        )
        fcm = fc["FreeCompanyMembers"]
        logging.warning("Loading character information from XIVAPI.  This may take up to 4s per member.")
        member_data = {}
        for m in fcm:
            logging.info("Processing character {name} ({id})".format(id=m["ID"], name=m["Name"]))
            member_data[m["ID"]] = await api_call(client.character_by_id, m["ID"])
        logging.info("Crunching numbers...")
        levels = {}
        for i in range(1,81):
            levels[i] = 0
        for m in member_data.keys():
            if member_data[m]["Info"]["Character"]["IsActive"]:
                logging.debug("Calculating max level for character {n} ({i})".format(n=member_data[m]["Character"]["Name"],i=m))
                levels[char_max_level(member_data[m])] += 1
            else:
                logging.debug("Skipping level calculation for inactive character {i}".format(i=m))
        plt.bar(levels.keys(), levels.values(), align="center", width=0.9)
        plt.ylabel("Number of members")
        plt.xlabel("Level")
        plt.title("{name} member levels".format(name=fc["FreeCompany"]["Name"]))
        plt.show()
    except:
        logging.exception("An exception occured during program execution")
    finally:
        await session.close()

if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, args.logLevel), format='%(message)s', datefmt='%H:%M')
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    loop.run_until_complete(run(config, session, args))