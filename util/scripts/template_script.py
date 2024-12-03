#!/usr/bin/env python3
import ckanapi
import logging

import argparse
from dotenv import load_dotenv

from helpers import EnvDefault

load_dotenv()
log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--ckan-url", action=EnvDefault, envvar="CKAN_URL", required=True,
                        help="CKAN url, can be passed as env CKAN_URL, e.g. https://dev.adr.fjelltopp.org")
    parser.add_argument("-K", "--ckan-apikey", action=EnvDefault, envvar="CKAN_APIKEY", required=True,
                        help="CKAN sysadmin api key, can be passed as env CKAN_APIKEY")
    parser.add_argument("-p", "--param",
                        help="Placeholder param to be used by your script.")
    parser.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x),
                        help="Configure the logging level.")
    parsed_args = parser.parse_args()
    return parsed_args


def work(ckan_url, ckan_apikey, param):
    ckan = ckanapi.RemoteCKAN(ckan_url, apikey=ckan_apikey)
    ### Your CKAN manipulation goes here. E.g:
    users = ckan.action.user_list()
    for user in users:
        log.info(f"User {user['name']}")




if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    ckan_url = args.ckan_url
    ckan_apikey = args.ckan_apikey
    param = args.param
    work(ckan_url, ckan_apikey, param)
