import json
import logging
import os
import re

import ckanapi

import csv

CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), './config.json')

with open(CONFIG, 'r') as config_file:
    config = json.loads(config_file)['config']

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), config['data_path'])
USERS_FILE = os.path.join(DATA_PATH, 'users.json')
ORGANIZATIONS_FILE = os.path.join(DATA_PATH, 'organizations.json')
DOCUMENTS_FILE = os.path.join(DATA_PATH, 'Malawi legacy repository document metadata - Document metadata.csv')

log = logging.getLogger(__name__)


def load_organizations(ckan):
    """
    Helper method to load organizations from the ORGANIZATIONS_FILE config file
    :param ckan: ckanapi instance
    :return: a dictionary map of created organization names to their ids
    """
    organization_ids_dict = {}
    with open(ORGANIZATIONS_FILE, 'r') as organizations_file:
        organizations = json.load(organizations_file)['organizations']
        for organization in organizations:
            org_name = organization['name']
            try:
                org = ckan.action.organization_create(**organization)
                log.info(f"Created organization {org_name}")
                organization_ids_dict[org_name] = org["id"]
                continue
            except ckanapi.errors.ValidationError as e:
                pass  # fallback to organization update
            try:
                log.warning(f"Organization {org_name} might already exists. Will try to update.")
                org_id = ckan.action.organization_show(id=org_name)['id']
                ckan.action.organization_update(id=org_id, **organization)
                organization_ids_dict[org_name] = org_id
                log.info(f"Updated organization {org_name}")
            except ckanapi.errors.ValidationError as e:
                log.error(f"Can't create organization {org_name}: {e.error_dict}")
    return organization_ids_dict


def load_users(ckan):
    """
    Helper method to load users from USERS_FILE config json file
    :param ckan: ckanapi instance
    :return: None
    """
    with open(USERS_FILE, 'r') as users_file:
        users = json.load(users_file)['users']
        for user in users:
            try:
                ckan.action.user_create(**user)
                log.info(f"Created user {user['name']}")
                continue
            except ckanapi.errors.ValidationError as e:
                pass  # fallback to user update
            try:
                log.warning(f"User {user['name']} might already exists. Will try to update.")
                id = ckan.action.user_show(id=user['name'])['id']
                ckan.action.user_update(id=id, **user)
                log.info(f"Updated user {user['name']}")
            except ckanapi.errors.ValidationError as e:
                log.error(f"Can't create user {user['name']}: {e.error_dict}")


def load_datasets(ckan, documents):
    """
    Helper method to load datasets from the DOCUMENTS_FILE config file
    :param ckan: ckanapi instance
    :param documents: a list of documents built from the metadata import file
    :return: None
    """

    for document in documents:
        try:
            dataset = {
                'title': document['title'],
                'name': document['name'],
                'year': document['year'],
                'owner_org': document['owner_org'],
                'notes': 'Demo dataset'
            }
            ckan.action.package_create(**dataset)
            log.info(f"Created dataset {dataset['name']}")
            continue
        except ckanapi.errors.ValidationError as e:
            pass  # fallback to dataset update
        try:
            log.warning(f"Dataset {dataset['name']} might already exists. Will try to update.")
            id = ckan.action.package_show(id=dataset['name'])['id']
            ckan.action.package_update(id=id, **dataset)
            log.info(f"Updated dataset {dataset['name']}")
        except ckanapi.errors.ValidationError as e:
            log.error(f"Can't create dataset {dataset['name']}: {e.error_dict}")


def load_resources(ckan, documents):
    """
    Helper method to load resources from the DOCUMENTS_FILE config file
    :param ckan: ckanapi instance
    :param documents: a list of documents built from the metadata import file
    :return: None
    """
    for document in documents:
        resource_dict = {'title': document['title'], 'name': document['name'], 'year': document['year'],
                         'url': 'upload', 'notes': 'Demo resource', 'package_id': document['name']}
        with open(os.path.join(DATA_PATH, document['file']), 'rb') as res_file:
            ckan.call_action(
                'resource_create',
                resource_dict,
                files={'upload': res_file}
            )


def load_data(ckan_url, apikey):
    ckan = ckanapi.RemoteCKAN(ckan_url, apikey=apikey)

    with open(DOCUMENTS_FILE) as csvfile:
        metadata_reader = csv.reader(csvfile)
        start_table = False
        documents = []
        for row in metadata_reader:
            if start_table:
                document = {
                    'title': row[2],
                    'name': _create_name(row[2]),
                    'file': row[3],
                    'program': row[5],
                    'category': row[6],
                    'year': row[8],
                    'owner_org': _create_name(row[5]),
                }
                documents.append(document)
            if row[1] == 'logi_id':
                start_table = True

    load_users(ckan)
    orgs = load_organizations(ckan)
    load_datasets(ckan, documents)
    load_resources(ckan, documents)


def _create_name(title):
    name = re.sub('[^a-zA-Z0-9_ ]', '', title)
    name = re.sub('[_ ]', '-', name)
    name = name.lower()
    return name


if __name__ == '__main__':
    load_data(ckan_url=config['ckan_url'], apikey=config['api_key'])
