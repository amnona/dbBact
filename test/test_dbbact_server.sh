#!/bin/bash
# Parameters:
# $1 name of the directory where postgres binaries are located (including trailing /)
# $2 address for the test dbbact server (i.e. 127.0.0.1:5002)
DEFAULT_POSTGRES_DIR=""
POSTGRES_DIR=${1:-$DEFAULT_POSTGRES_DIR}
DEFAULT_SERVER_ADDR="127.0.0.1:5002"
SERVER_ADDR=${2:-$DEFAULT_SERVER_ADDR}

# delete the test database and user and create new
${POSTGRES_DIR}psql postgres -U postgres < create_test_db.commands.txt

# set the password env, variable
PGPASSWORD="dbbact_test"
echo $PGPASSWORD

# get the full database scheme
PGPASSWORD="dbbact_test" ${POSTGRES_DIR}pg_restore -U dbbact_test -d dbbact_test --schema-only --no-owner ../database/dbbact-export.psql

# add the  users private table
PGPASSWORD="dbbact_test" ${POSTGRES_DIR}pg_restore -U dbbact_test -d dbbact_test --schema-only --no-owner ../database/users-private-table-scheme.psql

# add anonymous user
PGPASSWORD="dbbact_test"  ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO UsersTable (id,username) VALUES(0,'na');"
 # password hash is for empty string ""
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO UsersPrivateTable (id,username,passwordhash, attemptscounter) VALUES(0,'na','"'$2a$06$KNMw2Tjs8MF2RKL2O9UeGuyy9/lJBaouVN5byaLo/Sm33OMf7Uk3K'"',0);"

 # add annotationtypes
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationTypesTable (id,description) VALUES(1,'diffexp');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationTypesTable (id,description) VALUES(2,'isa');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationTypesTable (id,description) VALUES(3,'contamination');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationTypesTable (id,description) VALUES(4,'common');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationTypesTable (id,description) VALUES(5,'highfreq');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationTypesTable (id,description) VALUES(6,'other');"

# add details types
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationDetailsTypesTable (id,description) VALUES(1,'high');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationDetailsTypesTable (id,description) VALUES(2,'low');"
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AnnotationDetailsTypesTable (id,description) VALUES(3,'all');"

# add agents type
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO AgentTypesTable (id,description) VALUES(0,'na');"
# add methods type
  PGPASSWORD="dbbact_test" ${POSTGRES_DIR}psql -d dbbact_test -U dbbact_test -c "INSERT INTO MethodTypesTable (id,description) VALUES(0,'na');"

 # and run the test
 ./test_server.py --server-addr $SERVER_ADDR
 