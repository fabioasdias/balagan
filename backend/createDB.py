from subprocess import run
import sys

if len(sys.argv)!=2:
    print('.py DBNAME')
    exit(-1)

DB=sys.argv[1]

def  _runDB(cmd):
    run(cmd.format(DB),shell=True)

try:
    run("psql -lqtA -U postgres | grep -q {0}".format(DB),shell=True,check=True)
except:
    _runDB("createdb -U postgres {0}")
    _runDB('psql -U postgres {0} -c "CREATE EXTENSION postgis;"')
    _runDB('psql -U postgres {0} -c "CREATE EXTENSION postgis_topology;"')
    _runDB('psql -U postgres {0} -c "CREATE EXTENSION postgis_sfcgal;"')


