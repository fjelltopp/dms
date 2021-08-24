import json
import logging
import os
import re

import ckanapi

import csv

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

with open(CONFIG_PATH, 'r') as config_file:
    CONFIG = json.loads(config_file.read())['config']

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG['data_path'])
USERS_FILE = os.path.join(DATA_PATH, 'users.json')
ORGANIZATIONS_FILE = os.path.join(DATA_PATH, 'organizations.json')
DOCUMENTS_FILE = os.path.join(DATA_PATH, CONFIG['documents_file'])
GROUPS_FILE = os.path.join(DATA_PATH, CONFIG['groups_file'])
RESOURCE_FOLDER = os.path.join(DATA_PATH, CONFIG['resource_folder'])

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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
                'title': document['dataset'],
                'name': document['dataset_name'],
                'year': document['year'],
                'owner_org': document['owner_org'],
                'groups': [{'name': document['category']}],
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
        if len(document['file']) < 1:
            log.warning(f"Resource {resource_dict['name']} not created as it has no file attachment")
            continue

        resource_dict = {
            'title': document['title'],
            'name': document['name'],
            'year': document['year'],
            'url': 'upload',
            'package_id': document['dataset_name']
        }

        try:
            file_id = document['file'].split('.')[0]
            file_path = os.path.join(RESOURCE_FOLDER, file_id, document['file'])

            with open(file_path, 'rb') as res_file:
                ckan.call_action(
                    'resource_create',
                    resource_dict,
                    files={'upload': res_file}
                )
            log.info(f"Created resource {resource_dict['name']}")
            continue
        except ckanapi.errors.ValidationError as e:
            pass  # fallback to resource update
        try:
            log.warning(f"Resource {resource_dict['name']} might already exists. Will try to update.")
            id = ckan.action.resource_show(id=resource_dict['name'])['id']
            ckan.action.resource_update(id=id, **resource_dict)
            log.info(f"Updated resource {resource_dict['name']}")
        except ckanapi.errors.ValidationError as e:
            log.error(f"Can't create resource {resource_dict['name']}: {e.error_dict}")


def load_groups(ckan, documents):
    """
    Helper method to load groups from the GROUPS_FILE config file
    :param ckan: ckanapi instance
    :return: None
    """
    group_ids_dict = {}

    with open(GROUPS_FILE, 'r') as groups_file:
        groups = json.load(groups_file)['groups']

        for group in groups:
            group_name = group['name']
            try:
                org = ckan.action.group_create(**group)
                log.info(f"Created group {group_name}")
                group_ids_dict[group_name] = org["id"]
                continue
            except ckanapi.errors.ValidationError as e:
                pass  # fallback to group update
            try:
                log.warning(f"Group {group_name} might already exists. Will try to update.")
                group_id = ckan.action.group_show(id=group_name)['id']
                ckan.action.group_update(id=group_id, **group)
                group_ids_dict[group_name] = group_id
                log.info(f"Updated group {group_name}")
            except ckanapi.errors.ValidationError as e:
                log.error(f"Can't create group {group_name}: {e.error_dict}")

    return group_ids_dict


def load_data(ckan_url, ckan_api_key):
    ckan = ckanapi.RemoteCKAN(ckan_url, apikey=ckan_api_key)

    documents = _load_documents()

    load_users(ckan)
    orgs = load_organizations(ckan)
    load_groups(ckan, documents)
    load_datasets(ckan, documents)
    load_resources(ckan, documents)


def _create_name(title):
    name = re.sub('[^a-zA-Z0-9_ ]', '', title)
    name = re.sub('[_ ]', '-', name)
    name = name.lower()
    return name


def _load_documents():
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
                    'category': _create_name(row[6]),
                    'year': row[8],
                    'owner_org': _create_name(row[5]),
                    'dataset': row[10],
                    'dataset_name': _create_name(row[10])
                }
                documents.append(document)
            if row[1] == 'logi_id':
                start_table = True
        return documents


if __name__ == '__main__':
    load_data(ckan_url=CONFIG['ckan_url'], ckan_api_key=CONFIG['ckan_api_key'])
