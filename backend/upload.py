from glob import glob
import magic
import zipfile
from os import remove
from os.path import isdir
from subprocess import run
from uuid import uuid4
import pandas as pd
from sqlalchemy import create_engine
from os.path import basename


engine = create_engine('postgresql+psycopg2://postgres:nothing@localhost/balagan')

def _tableName(id,n):
    return('{0}-{1}'.format(id,n))

def _extractErase(fname,tempDir):
    zip_ref = zipfile.ZipFile(fname, 'r')
    zip_ref.extractall(tempDir)
    zip_ref.close()
    remove(fname)

def processUploadFolder(tempDir):    
    shps=[]
    csvs=[]
    folders=[tempDir,]
    nzips=0
    while folders:
        cf=folders.pop(0)
        for fname in glob(cf+'/*'):
            if (isdir(fname)):
                folders.append(fname)
            else:
                kind=magic.from_file(fname,mime=True)
                if (kind=='application/zip'):
                    newdir=tempDir+'/{0}/'.format(nzips)
                    nzips+=1
                    _extractErase(fname,newdir)
                    folders.append(newdir)
                if ((kind=='application/octet-stream') and ('.shp' in fname)):
                    shps.append(fname)
                if ((kind=='text/plain') and (('.csv' in fname)or('.tsv' in fname))):
                    csvs.append(fname)
                if ((kind=='text/plain') and (('.gj' in fname)or('.json' in fname))):
                    shps.append(fname)

    nTables=0
    id=uuid4()
    ret={}
    ret['id']=str(id)
    ret['status']={}
    for shp in shps:
        ret['status'][basename(shp)]=-1
        if ('.shp' in shp):
            shp2=shp.replace('.shp','.2.shp')
        else:
            if ('.json' in shp):
                shp2=shp.replace('.json','.shp')
            elif  ('.gj' in shp):
                shp2=shp.replace('.gj','.shp')

        thisTable=_tableName(id,nTables)
        try:
            cmd='ogr2ogr -f "ESRI Shapefile" -t_srs EPSG:4326 {1} {0}'.format(shp,shp2) #-dialect sqlite -sql "select ST_MakeValid(geometry) as geometry, * from {2}" ,basename(shp)[:-4]
            # print(cmd)
            run(cmd,shell=True,check=True)
            run('shp2pgsql -s 4326 -I -g geom {0} tempdata.{1} | psql -q -U postgres -d balagan'.format(shp2,thisTable),shell=True,check=True)
            ret['status'][basename(shp)]=thisTable
        except:
            raise
            # pass
        nTables+=1

    for C in csvs:
        print(C)
        thisTable=_tableName(id,nTables)
        ret['status'][basename(C)]=-1
        try:
            df=pd.read_csv(C,low_memory=False)
            df.to_sql(thisTable, engine,schema='tempdata')
            ret['status'][basename(C)]=thisTable
        except:
            pass
        nTables+=1
    return(ret)

    