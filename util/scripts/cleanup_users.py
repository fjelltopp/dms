#!/usr/bin/env python3
import ckanapi
import logging
import argparse

log = logging.getLogger(__name__)

# Script run at 14:07 on 3rd December 2024

sms_subscribers = [
    "stephen-chu", 
    "mike", 
    "mprslot", 
    "agus", 
    "wiseman-banda", 
    "masozi-lufingo-ngosi", 
    "haxson-twaibu", 
    "silvee", 
    "jimson-banda", 
    "dennis-kacheche", 
    "tiwonge-chimpandule", 
    "slotpulsa5000", 
    "situs138", 
    "gabriel-mwamlima"
]
org_members = [
    "relia-nkhata",
    "ray-244",
    "lmtambo-9172"
    "christian-neumann"
]
sysadmins = [
    "christian-neumann",
    "admin",
    "mful",
    "tomek",
    "francis",
    "michal-ful",
    "jberry"
]
email_subscribers = [
    'alonzoharvey',
    'amon-dembo',
    'andreas-jahn',
    'andrew-mussa',
    'andy', 
    'berlington-munkhondya',
    'beth-tippett-barr',
    'cameronrhoades',
    'charles-innocent-chinguwo',
    'cherylsingh',
    'ckhuwi',
    'francis',
    'cleowheeler',
    'dennismontano',
    'dennyhiggins',
    'dollar-merah',
    'dr-rabson-kachala',
    'dumisani-ndhlovu',
    'giay',
    'gift-magawa',
    'haywoodtatum',
    'isaiah_sikamba',
    'joe',
    'jberry',
    'kalibisajadi',
    'kassandrastovall',
    'kingsley-laija',
    'limbani-bandah',
    'lfrosario',
    'tymless',
    'maggie-phiri',
    'michal-ful',
    'nicodemus-chihana',
    'patience-bwanali',
    'pearldonovan',
    'phillip-mtambo',
    'pimpin4d-official',
    'precious-chigete',
    'ray-244',
    'semu-bangelo',
    'smith-vitumbiko-nthakomwa',
    'sterner-moses-msamila',
    'tmasina',
    'tomek',
    'wanangwa-mkandawire',
    'william-kayira',
    'mzumaraw',
    'wyattwray',
    'yamikani-matiya',
    'zernanise-xavier'
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
    users = ckan.action.user_list(all_fields=False)
    counter = 0
    USERS_TO_KEEP = email_subscribers + sms_subscribers + sysadmins + org_members
    for user in users:
        if user not in USERS_TO_KEEP:
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
