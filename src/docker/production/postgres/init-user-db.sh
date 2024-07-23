#!/bin/bash
set -e

# 220724, Tuesday, 04.00 pm  
# this script is being used to create a custom user and db name using the default superuser postgres and custom db postgres
# the below script has some conditions, the data should be empty to run the script. 
# see more on this link at: [Initialization scripts] section. Link: https://hub.docker.com/_/postgres?tab=description

# A new user with the POSTGRES_USER will be created with the POSTGRES_PASSWORD as password for POSTGRES_DB 
psql -v ON_ERROR_STOP=1 --username postgres --dbname postgres <<-EOSQL
    CREATE USER "$POSTGRES_USER" WITH PASSWORD "$POSTGRES_PASSWORD";
    CREATE DATABASE "$POSTGRES_DB";
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
EOSQL