docker-compose up -d
cat db_init.sql | docker exec -i db psql -U ckan
ckan -c ../../ckan/test-core.ini datastore set-permissions | docker exec -i db psql -U ckan