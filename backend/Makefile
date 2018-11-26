all: 
	python3 srv.py

redodb: dropdb prepdb
	echo 'redone'
dropdb:
	dropdb -U postgres balagan

prepdb: createDB.py sql/create.sql
	python3 createDB.py balagan
	psql -U postgres balagan -f  sql/create.sql
