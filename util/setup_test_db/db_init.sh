docker run --name dms-postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 -d postgres
cat db_init.sql | docker exec -i dms-postgres psql -U postgres
ckan -c ../../ckan/test-core.ini datastore set-permissions | docker exec -i dms-postgres psql -U postgres