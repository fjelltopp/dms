#!/bin/sh
curl -sL https://deb.nodesource.com/setup_14.x | bash - && apt-get install nodejs && npm version
npm install --global yarn

# build js components & allow editing
yarn --cwd /usr/lib/ckan/ckanext-dms/ckanext/dms/react/
yarn --cwd /usr/lib/ckan/ckanext-dms/ckanext/dms/react/ build
chown -R ckan /usr/lib/ckan/ckanext-dms/ckanext/dms/assets/build

