#!/bin/sh
# build js components & allow editing
yarn --cwd /usr/lib/ckan/ckanext-dms/ckanext/dms/react/
yarn --cwd /usr/lib/ckan/ckanext-dms/ckanext/dms/react/ build
chown -R ckan /usr/lib/ckan/ckanext-dms/ckanext/dms/assets/build
