#!/usr/bin/env python3
import ckanapi
import logging
import argparse

log = logging.getLogger(__name__)

# This script removes all users that arn't signed up for notifications, or are in a specified list, or are sysadmins.

org_members = [
    "relia-nkhata",
    "ray-244",
    "lmtambo-9172"
    "christian-neumann"
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--ckan-url", required=True,
                        help="CKAN url, can be passed as env CKAN_URL, e.g. https://dev.adr.fjelltopp.org")
    parser.add_argument("-K", "--ckan-apikey", required=True,
                        help="CKAN sysadmin api key, can be passed as env CKAN_APIKEY")
    parser.add_argument("-p", "--param",
                        help="Placeholder param to be used by your script.")
    parser.add_argument("--log-level", default=logging.INFO, type=lambda x: getattr(logging, x),
                        help="Configure the logging level.")
    parsed_args = parser.parse_args()
    return parsed_args


def work(ckan_url, ckan_apikey, param):
    ckan = ckanapi.RemoteCKAN(ckan_url, apikey=ckan_apikey)
    users = ckan.action.user_list(all_fields=True, include_plugin_extras=True)
    users_to_keep = []
    for user in users:
        if (
            user['sysadmin'] or
            user['activity_streams_email_notifications'] or
            user['phonenumber'] or
            user['name'] in org_members
        ):
            users_to_keep.append(user['name'])
    log.info(f"{len(users_to_keep)} in total")
    counter = 0
    for user in users:
        if user not in users_to_keep:
            log.info(f"Deleting user: {user}")
            counter = counter + 1
            ckan.action.user_delete(id=user)
    log.info(f"{len(users)} in total")
    log.info(f"Deleted {counter} users")


if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    ckan_url = args.ckan_url
    ckan_apikey = args.ckan_apikey
    param = args.param
    work(ckan_url, ckan_apikey, param)
