CREATE USER ckan_default WITH PASSWORD 'pass';
CREATE USER datastore_default WITH PASSWORD 'pass';
DROP DATABASE IF EXISTS ckan_test;
DROP DATABASE IF EXISTS datastore_test;
CREATE DATABASE ckan_test OWNER ckan_default ENCODING 'utf-8';
CREATE DATABASE datastore_test OWNER ckan_default ENCODING 'utf-8';
