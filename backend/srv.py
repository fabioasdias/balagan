import cherrypy
import sys
import os
from os.path import exists
import tempfile
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime
from psycopg2 import sql
import psycopg2.extras
from random import sample
from upload import processUploadFolder
import numpy as np
from scipy.spatial import Voronoi, Delaunay
from scipy.spatial.distance import pdist,squareform
from numpy.linalg import norm
import networkx as nx
from clustering import ComputeClustering
import json
from networkx.readwrite import json_graph
import traceback
import matplotlib.pylab as plt
from shapely.geometry import Point
from shapely.ops import cascaded_union
from shapely import wkb
WIGGLE=1e-5 #about half a street - used to close gaps (and densify the border)


def plotPol(g,style='o-'):
    for pol in _makeListPols(g):
        x=[]
        y=[]
        for p in pol.exterior.coords:                
            x.append(p[0])
            y.append(p[1])
        plt.plot(x,y,style)

def findBorder(points):
    P=[Point(points[i,0],points[i,1]).buffer(1750*WIGGLE).simplify(0.1) for i in range(points.shape[0])]
    B=cascaded_union(P).buffer(-750*WIGGLE)
    # plt.figure()
    # plt.plot(points[:,0],points[:,1],'.r')
    # plotPol(B)
    # plt.show()
    ret=[]
    for pol in _makeListPols(B):
        x,y=pol.exterior.coords.xy
        curBorder=fixDensity(np.array(list(zip(x,y))))
        ret.extend(curBorder)
    return(np.array(ret))


def fixDensity(border,nWiggles=500):
    step=nWiggles*WIGGLE
    new_border=[]
    N=border.shape[0]
    new_border.append(border[0,:])
    i=0
    j=i+1
    
    while True:
        if (i>=(N-1)):
            break

        p1=border[i,:]
        while True:
            p2=border[j,:]
            v=p2-p1
            totalD=norm(v)
            if totalD < step:
                if (j>=(N-1)):
                    break
                j+=1
            else:
                break
                
        if totalD>0:
            v=v/totalD #unitary vector
            cP=p1
            nSteps=int(np.floor(totalD/step))
            if (nSteps>0):
                actualStep=totalD/nSteps
                for _ in range(nSteps):
                    cP=cP+v*actualStep
                    new_border.append(cP)
        i=j
        j=i+1

    new_border=np.array(new_border)

    # border=np.concatenate((border,new_border),axis=0)
    return(new_border)



DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

def cors():
  if cherrypy.request.method == 'OPTIONS':
    # preflight request 
    # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
    cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
    cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
    cherrypy.response.headers['Access-Control-Allow-Origin']  = '*'
    # tell CherryPy To avoid normal handler
    return True
  else:
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)


def _getAvVG():
    ret={}
    ret['geometries']=[]
    ret['variables']=[]

    conn = connPool.getconn()
    cur = conn.cursor()
    cur.execute(sql.SQL("SELECT GeoID, name, description FROM AvGeo;"))
    for fields in cur:
        ret['geometries'].append({'GeoID':fields[0], 'name':fields[1], 'desc':fields[2]})

    cur.execute(sql.SQL("SELECT VarID, name, description FROM AvVars;"))
    for fields in cur:
        ret['variables'].append({'VarID':fields[0], 
                                    'name':fields[1], 
                                    'desc':fields[2], 
                                    'sample':_getSample(conn,'public','variables','val',where='VarId = '+str(fields[0]))})

    cur.close()
    conn.commit()
    connPool.putconn(conn)
    return(ret)
def _makeListPols(g):
    if g.type == 'Polygon':
        g=[g,]
    elif g.type == 'MultiPolygon':
        g=list(g)
    return(g)


def _createHier(VarID):
    print('Create Hier VARID',VarID)
    conn = connPool.getconn()
    cur = conn.cursor()

    cur.execute(sql.SQL("SELECT GeoID,name from AvVars WHERE VarID=%s"),[VarID,])
    res=cur.fetchone()
    GeoID=res[0]
    varname=res[1]
    print('GeoID',GeoID,varname)
    cacheName='geoid_{0}.gp'.format(GeoID)

    if not exists(cacheName):
        print('doing the graph')
        cur.execute(sql.SQL("SELECT F.FormID, ST_X(F.centr), ST_Y(F.centr), F.geom FROM Forms as F WHERE (F.GeoID=%s)"),[GeoID,])
        points=[]#np.zeros((cur.rowcount,2))
        ind2ID={}
        G=nx.Graph()
        ind=0
        # plt.figure()
        for row in cur:
            n=row[0]
            G.add_node(n)
            G.node[n]['x']=row[1]
            G.node[n]['y']=row[2]
            geom=wkb.loads(row[3], hex=True)
            for pol in _makeListPols(geom):            
                # plotPol(pol)
                p=pol.representative_point()
                points.append([p.x,p.y])
                ind2ID[ind]=n
                ind+=1

                # x,y=pol.exterior.coords.xy
                # curPoints=fixDensity(np.array(list(zip(x,y))))
                # points.extend(curPoints)
                # for _ in range(curPoints.shape[0]):
                #     ind2ID[ind]=n        
                #     ind=ind+1
        points=np.array(points)

        border=findBorder(points)
        maxValid=points.shape[0]
        points=np.concatenate((points,border),axis=0)

        print('start Voronoi', points.shape)
        D=Voronoi(points,qhull_options="E0")
        print('done Voronoi')
        for e in D.ridge_points:
            if (e[0]<maxValid) and (e[1]<maxValid):
                n0=ind2ID[e[0]]
                n1=ind2ID[e[1]]
                if (n0!=n1):
                    G.add_edge(n0,n1)
        print('number of connected components ',nx.number_connected_components(G))
        nx.write_gpickle(G,cacheName)
    else:
        print('assigning values',cacheName)
        G=nx.read_gpickle(cacheName)

    # pos={}
    # for n in G:
    #     pos[n]=[G.node[n]['x'],G.node[n]['y']]
    # for H in nx.connected_component_subgraphs(G):
    #     if (len(list(H.nodes()))>10):
    #         nx.draw(H,pos=pos,node_size=2,node_color='green')
    #     else:
    #         nx.draw(H,pos=pos,node_size=10,node_color='red')
    # plt.show()
    # exit()


    cur.execute(sql.SQL("SELECT normVal, FormID FROM Variables WHERE (VarID=%s);"),[VarID,])
    print('assigning values nodes:{0}, vals:{1}'.format(len(G.nodes),cur.rowcount))
    for row in cur:
        G.node[row[1]]['val']=row[0]


    print('Nodes {0}, edges {1}'.format(len(G.nodes()),len(G.edges())))
    H=ComputeClustering(G, layer='val',varname=varname)
    print('clustering done')
    status=False
    levelMax=0
    for e in H.edges():
        if ('level' in H[e[0]][e[1]]):
            levelMax=max((levelMax,H[e[0]][e[1]]['level']))


    #fluxland
    if (True):
        print('saving', VarID, varname)
        NG=nx.Graph()
        
        cur.execute(sql.SQL("SELECT F.FormID, F.OriginalID FROM Forms as F WHERE (F.GeoID=%s);"),[GeoID])
        conversion={row[0]:row[1] for row in cur.fetchall()}

        NG.add_nodes_from([conversion[n] for n in H.nodes()])
        NG.add_edges_from([(conversion[n1],conversion[n2]) for (n1,n2) in H.edges()])
        for e in H.edges():
            NG[conversion[e[0]]][conversion[e[1]]]['level']=H[e[0]][e[1]]['level']/levelMax

        with open('g{0}.json'.format(VarID),'w') as fout:
            json.dump(json_graph.node_link_data(NG),fout)



    try:
        cur.execute(sql.SQL("INSERT INTO AvHier(VarID,maxLevel) VALUES (%s,%s) RETURNING HierID;"),[VarID,levelMax])
        HierID=cur.fetchone()[0]
        for e in H.edges():
            if ('level' in H[e[0]][e[1]]):
                cur.execute(sql.SQL("INSERT INTO Edges(HierID,Node1,Node2,level,scale) VALUES (%s,%s,%s,%s,0);"),[HierID,e[0],e[1],H[e[0]][e[1]]['level']])
        conn.commit()
        status=True
    except:
        conn.rollback()
        print("Unexpected error:", sys.exc_info()[0])
        raise        

    cur.close()
    conn.commit()
    connPool.putconn(conn)
    
    ret={'status':status}
    return(ret)

    
def _getSample(conn,schema,tablename,field, where='', N=1):
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
    percentage=1
    while True:
        if (where==''):
            csql=sql.SQL('SELECT {} FROM {}.{} TABLESAMPLE SYSTEM(%s);').format(sql.Identifier(field),sql.Identifier(schema),sql.Identifier(tablename))
        else:
            csql=sql.SQL('SELECT {} FROM {}.{} TABLESAMPLE SYSTEM(%s) WHERE '+where+';').format(sql.Identifier(field),sql.Identifier(schema),sql.Identifier(tablename))
        cur.execute(csql, [percentage,])

        ret=cur.fetchall()
        if ((cur.rowcount>=N) or (percentage>100)):
            break
        else:
            percentage*=1.1
    
    cur.close()
    if (len(ret)>N):
        ret=sample(ret,N)
    return([X[0] for X in ret])


@cherrypy.expose
class server(object):
    @cherrypy.expose
    def index(self):
        return("It works!")

    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.config(**{'tools.cors.on': True})        
    def SimplifiedGeojson(self):
        input_json = cherrypy.request.json
        print(input_json)

        conn = connPool.getconn()
        cur = conn.cursor()

        bbox=input_json['viewbox']
        cur.execute(sql.SQL('SELECT geoid from AvGeo WHERE ST_Intersects(geom,ST_MakeEnvelope(%s, %s, %s, %s, 4326));'),[bbox['_sw']['lng'],bbox['_sw']['lat'],bbox['_ne']['lng'],bbox['_ne']['lat']])
        if (cur.rowcount >0):
            print(cur.fetchall())
        cur.close()
        conn.commit()        
        return({})

    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.config(**{'tools.cors.on': True})        
    def moveTemp(self):
        input_json = cherrypy.request.json
        # print(input_json)
        files=input_json['newFiles']
        # uuid=input_json['id']

        conn = connPool.getconn()
        cur = conn.cursor()

        # FormsToEdges=[]
        ret={}

        for F in files:
            ret[F]=True     
            if not files[F]['enabled']:
                continue
            ret[F]=False

            geoms=files[F]['geometries']
            vars=files[F]['variables']
            curGeoIDs={}

            if True:
                for g in geoms:
                    if (not g['enabled']):
                        continue
                    try:
                        if (g['mergeWith']==''):
                            cur.execute(sql.SQL('INSERT INTO AvGeo(Name,Description) VALUES (%s,%s) RETURNING GeoID;'),[g['name'],g['description']])
                            GeoID=cur.fetchone()[0]                            
                            conn.commit()
                        else:
                            GeoID=int(g['mergeWith'])
                        curGeoIDs[g['name']]=GeoID

                        print(GeoID)
                        cur.execute(
                            sql.SQL(
                                'INSERT INTO Forms(GeoID,OriginalID,geom,centr) SELECT %s,{0},ST_MakeValid({1}),ST_Centroid({1}) FROM tempdata.{2} RETURNING FormID;')
                                .format(sql.Identifier(g['indexField']),
                                        sql.Identifier(g['field']),
                                        sql.Identifier(g['table'])),[GeoID,])
                        cur.execute(
                            sql.SQL(
                                'INSERT INTO SimpForm(GeoID,OriginalID,geom,centr) SELECT %s,{0},ST_Multi(ST_SimplifyPreserveTopology(ST_Buffer(ST_SimplifyPreserveTopology(ST_MakeValid({1}), 0.5),0.0001),0.75)),ST_Centroid({1}) FROM tempdata.{2} RETURNING FormID;')
                                .format(sql.Identifier(g['indexField']),
                                        sql.Identifier(g['field']),
                                        sql.Identifier(g['table'])),[GeoID,])
                        conn.commit()
                        cur.execute(sql.SQL('UPDATE AvGeo SET geom=t.geom FROM (SELECT ST_Multi(ST_SetSRID(ST_Extent(F.geom),4326)) as geom from public.SimpForm as F where F.GeoID=%s) as t where GeoID=%s'),[GeoID,GeoID])                        
                        conn.commit()
                    except:
                        conn.rollback()
                        raise

                for v in vars:
                    if (not v['enabled']):
                        continue
                    if (v['useGeom']['GeoID']!=''):
                        GeoID=int(v['useGeom']['GeoID'])
                    else:
                        GeoID=curGeoIDs[v['useGeom']['name']]

                    try:  #TODO mergeWith not tested
                        if (v['mergeWith']==''):
                            if (v['normalizedBy']==''):                        
                                cur.execute(sql.SQL('INSERT INTO AvVars(Name,Description,GeoID) VALUES (%s,%s,%s) RETURNING VarID;'),[v['name'],v['description'],GeoID])
                            else:
                                cur.execute(sql.SQL('INSERT INTO AvVars(Name,Description,NormalizedBy,GeoID) VALUES (%s,%s,%s,%s) RETURNING VarID;'),[v['name'],v['description'],v['normalizedBy'],GeoID])
                            VarID=cur.fetchone()[0]
                            conn.commit()
                        else:
                            VarID=int(v['mergeWith'])

                        if (v['normalizedBy']==''):                        
                            cSQL=sql.SQL("""INSERT INTO 
                                                Variables(VarID,FormID,val,normVal) 
                                                SELECT 
                                                    %s,
                                                    F.FormID,
                                                    T.{1}::numeric,
                                                    T.{1}::numeric
                                                FROM 
                                                    tempdata.{2} as T, 
                                                    Forms as F 
                                                WHERE 
                                                    (T.{0}::text = F.OriginalID) AND 
                                                    (F.GeoID = %s);""").format(sql.Identifier(v['indexField']),sql.Identifier(v['field']),sql.Identifier(v['table']))
                            cur.execute(cSQL,[VarID,GeoID])
                        else:
                            cSQL=sql.SQL("""INSERT INTO 
                                                Variables(VarID,FormID,val,normVal) 
                                                SELECT 
                                                    %s,
                                                    F.FormID,
                                                    T.{1}::numeric,
                                                    case 
                                                        when V.val = 0 
                                                        then 0 
                                                    else
                                                        T.{1}::numeric/V.val
                                                    end
                                                FROM 
                                                    tempdata.{2} as T, 
                                                    Forms as F,
                                                    Variables as V 
                                                WHERE 
                                                    (V.VarID = %s) AND (V.FormID = F.FormID) AND
                                                    (T.{0}::text = F.OriginalID) AND 
                                                    (F.GeoID = %s);""").format(sql.Identifier(v['indexField']),sql.Identifier(v['field']),sql.Identifier(v['table']))
                            cur.execute(cSQL,[VarID,v['normalizedBy'],GeoID])

                        conn.commit()
                        try:
                            _createHier(VarID)
                        except Exception as exc:
                            print(traceback.format_exc())
                            print(exc)
                            pass
                    except:
                        print(cur.query)
                        conn.rollback()
                        raise

                ret[F]=True 

        cur.close()
        conn.commit()

        return(ret)

    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def getAvailableVG(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret=_getAvVG()
        return(ret)


    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def getAvailableHiers(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret=[]


        conn = connPool.getconn()
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT H.HierID, V.name, H.description, V.description FROM AvHier as H, AvVars as V WHERE V.VarID = H.VarID;"))
        for fields in cur:
            ret.append({'HierID':fields[0], 'name':fields[1], 'descH':fields[2], 'descV':fields[3], 'w':1/cur.rowcount, 'auto': True})

        cur.close()
        conn.commit()
        connPool.putconn(conn)

        return(ret)


    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.config(**{'tools.cors.on': True})        
    def createHierarchy(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        print(input_json)
        VarID=input_json['VarID']
        return(_createHier(VarID))


    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.config(**{'tools.cors.on': True})        
    def mixHierarchies(self):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        input_json = cherrypy.request.json
        print(input_json)
        detailThres=input_json['detailLevel']
        hiers = input_json['hiers']
        viewbox = input_json['viewbox']


        conn = connPool.getconn()
        cur = conn.cursor()
        
        if (not hiers):
            cur.execute(sql.SQL('SELECT HierID FROM AvHier;'))
            hiers=[{'HierID':x[0],'w':1/cur.rowcount} for x in cur.fetchall()]
            conn.commit()
        if (not hiers):
            print('breaking - no AvHiers')
            return({})

        

        G=nx.Graph()

        ret={}
        ret['type']="FeatureCollection"
        ret['features']=[]

        ids=[]
        feats=dict()
        for h in hiers:
            if (h['w']==0):
                continue
            cHID=h['HierID']
            ids.append(cHID)
            cur.execute(sql.SQL('SELECT maxLevel FROM AvHier WHERE HierID=%s;'),[cHID,])
            h['max']=cur.fetchone()[0]
            conn.commit()            
            cur.execute(sql.SQL("""SELECT 
                                        E.Node1, 
                                        E.Node2, 
                                        E.level,
                                        F.FormID,
                                        ST_AsGeoJson(ST_ForceRHR(F.geom))
                                    FROM 
                                        Edges as E, 
                                        Forms as F 
                                    WHERE 
                                        (E.HierID=%s) AND
                                        ((F.FormID=E.Node1) OR (F.FormID=E.Node2)) AND
                                        (F.Geom && ST_MakeEnvelope(%s,%s,%s,%s,4326));
                                        """), [cHID,viewbox['_sw']['lng'],viewbox['_sw']['lat'],viewbox['_ne']['lng'],viewbox['_ne']['lat']])
            for row in cur.fetchall():
                G.add_edge(row[0],row[1])
                G[row[0]][row[1]][cHID]=(row[2]/h['max'])*h['w']
                if (row[3] not in feats):
                    feats[row[3]]=json.loads(row[4])

                

            conn.commit()                   
            
        


        allD=[]
        to_remove=[]
        print(hiers)
        for e in G.edges():
            S=0
            # S=max([G[e[0]][e[1]][h] for h in G[e[0]][e[1]]])            
            for h in ids:
                if (h in G[e[0]][e[1]]):
                    S+=G[e[0]][e[1]][h]
            allD.append(S)
            if S > detailThres:
                to_remove.append((e[0],e[1]))


        # print(sorted(allD))
        # plt.hist(allD,100)
        # plt.show()
        G.remove_edges_from(to_remove)

        geom2ind=dict()
        for f in feats:
            geom2ind[f]=len(ret['features'])
            ret['features'].append({"type": "Feature","geometry": feats[f],"properties": {"colour":'black'} })        

        C=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928']
        curInd=0
        for H in sorted(nx.connected_components(G), key = len, reverse=True):
            for n in H:
                if (n in geom2ind):
                    ret['features'][geom2ind[n]]['properties']["colour"]=C[curInd%len(C)]

            curInd+=1

        print('\n\nUsed {0} clusters\n\n'.format(curInd))
        # for h in hiers:
        #     cur.execute(sql.SQL('SELECT V.GeoID FROM AvVars as V, AvHier as H WHERE (H.HierID=%s) AND (H.VarID=V.VarID);'), [cHID,])
        #     GeoID=cur.fetchone()[0]



        conn.commit()                    
        cur.close()
        connPool.putconn(conn)
        return(ret)


    @cherrypy.expose
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def getTemporaryTables(self, uuid=None):
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        ret={}
        ret['uuid']=uuid
        ret['new']={}
        ret['old']={}
        ret['old']=_getAvVG()
        
        print('uuid',uuid)
        conn = connPool.getconn()
        cur = conn.cursor()
        if (uuid is not None):
            cur.execute(sql.SQL("SELECT * FROM uploadlog WHERE uuid=%s;"),[uuid,])
        else:
            cur.execute(sql.SQL("SELECT * FROM uploadlog;"))

        cur2 = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        
        for table in cur:                    
            cur2.execute(sql.SQL("SELECT * FROM information_schema.columns WHERE table_schema = %s AND table_name   = %s;"),['tempdata',table[0]])            
            ret['new'][table[3]]={}
            ret['new'][table[3]]['enabled']=True
            ret['new'][table[3]]['variables']=[]
            ret['new'][table[3]]['geometries']=[]
            for fields in cur2:
                if (fields['udt_name']=='geometry'):
                    ret['new'][table[3]]['geometries'].append({'enabled':True,
                                                     'name':table[3].replace('.shp','').replace('.gj','').replace('.json',''),
                                                     'indexField':'', 
                                                     'mergeWith':'',
                                                     'description':table[3]+': '+fields['column_name'],
                                                     'table':table[0],                                                     
                                                     'field':fields['column_name'],
                                                     'fname':table[3],                                                     
                                                     })
                else:
                    ret['new'][table[3]]['variables'].append({'enabled': True,
                                                    'name': fields['column_name'],
                                                    'type':fields['udt_name'],                         
                                                    'indexField':'', 
                                                    'mergeWith':'', 
                                                    'normalizedBy':'',
                                                    'useGeom':'',                                                                                       
                                                    'description':table[3]+': '+fields['column_name'],                                                                    
                                                    'table':table[0],
                                                    'field':fields['column_name'],
                                                    'fname':table[3], 
                                                    'sample':_getSample(conn,'tempdata',table[0],fields['column_name'])
                                                    })
                    
        conn.commit()                    
        cur.close()
        cur2.close()                
        connPool.putconn(conn)
        return(ret)

    @cherrypy.expose
    @cherrypy.config(**{'tools.cors.on': True})    
    @cherrypy.tools.gzip()
    @cherrypy.tools.json_out()
    def upload(self, file):
        myFile=file
        cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
        with tempfile.TemporaryDirectory() as tempDir:
            fname=tempDir+'/'+myFile.filename
            with open(fname,'wb') as outFile:        
                while True:
                    data = myFile.file.read(8192)
                    if not data:
                        break
                    outFile.write(data)            
            out=processUploadFolder(tempDir)            
        conn = connPool.getconn()
        cur = conn.cursor()
        for k in out['status']:
            if (out['status'][k]!=-1):
                cur.execute(sql.SQL("INSERT INTO uploadlog (tableName,uuid,created,fname,ip,done) VALUES (%s,%s,%s,%s,%s,False)"),
                    [out['status'][k],
                    out['id'],
                    str(datetime.now()),
                    k,
                    str(cherrypy.request.remote.ip)])
        cur.close()
        conn.commit()
        connPool.putconn(conn)
        return(out)



if __name__ == '__main__':
    # if ((len(sys.argv)) != 2) and ((len(sys.argv)) != 3):
    #     print(".py conf.json (genCache? - optional = Y/N)")
    #     exit(-1)

    webapp = server()
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*','application/*']
        },
        '/public': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }



    connPool = ThreadedConnectionPool(1, 10, "dbname=balagan user=postgres password=nothing" )
    # _createHier(1)
    # exit()

    cherrypy.server.max_request_body_size = 0
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 8000
    cherrypy.quickstart(webapp, '/', conf)
    connPool.closeall()

