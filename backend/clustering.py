import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pylab as plt
import numpy as np
from scipy.spatial.distance import cdist,euclidean
from scipy.ndimage import gaussian_filter
from scipy.stats import wasserstein_distance
from heapq import heappop, heappush,heapify
from random import sample, random
from matplotlib import cm
import matplotlib.pylab as plt

NBINS=100

def _otherPlot(G,layer,edges):
    nodes=sorted(G.nodes())

    clusters=set([Find(G.node[n])['id'] for n in nodes])
    if (len(clusters)>20):
        return()

    colours={id:i/len(clusters) for i,id in enumerate(clusters)}
    cmap=cm.get_cmap('Vega20')


    pos={}
    node_sizes=[]
    NC=[]
    for n in nodes:
        pos[n]=[G.node[n]['x'],G.node[n]['y']]
        node_sizes.append(G.node[n][layer]/1000)
        NC.append(cmap(colours[Find(G.node[n])['id']]))


    E=[(min(ee),max(ee)) for ee in G.edges()]
    EC=list(set(E)-set(edges))
    nx.draw_networkx_nodes(G,pos=pos,node_size=node_sizes,node_color=NC)
    nx.draw_networkx_edges(G,pos=pos,edgelist=edges,edge_color='red',width=5)
    nx.draw_networkx_edges(G,pos=pos,edgelist=EC,edge_color='blue',width=1)
    plt.show()

def _plotGraph(G,layer):
    pos={}
    node_sizes=[]
    cmap=cm.get_cmap('viridis')
    emin=np.inf
    emax=-np.inf

    for e in G.edges():
        emin=np.min([emin,G[e[0]][e[1]]['level']])
        emax=np.max([emax,G[e[0]][e[1]]['level']])

    # print(emax,emin)

    ec=[]
    eW=[]
    for e in G.edges():
        X=G[e[0]][e[1]]['level']
        ec.append(cmap((X-emin)/(emax-emin)))
        eW.append(X)

    for n in G.nodes():
        pos[n]=[G.node[n]['x'],G.node[n]['y']]
        node_sizes.append(G.node[n][layer]/20)
    nx.draw(G,pos,node_size=node_sizes,edges=G.edges(),edge_color=ec,width=5)#eW)
    plt.figure()
    plt.hist(eW,500)
    plt.show()

def _clusterDistance(G,C1,C2,layer):
    h1=C1['histogram']
    s1=np.sum(h1)
    if (s1>0):
        h1=h1/s1

    C1=np.cumsum(h1)
    h2=C2['histogram']
    s2=np.sum(h2)
    if (s2>0):
        h2=h2/s2
    C2=np.cumsum(h2)

    D=np.sum(np.abs(C1-C2))/NBINS
    return(D)


def Union(x, y):
     xRoot = Find(x)
     yRoot = Find(y)
     if xRoot['rank'] > yRoot['rank']:
         xRoot['members'].extend(yRoot['members'])
         xRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         del(yRoot['histogram'])
         del(yRoot['members'])
         yRoot['parent'] = xRoot
     elif xRoot['rank'] < yRoot['rank']:
         yRoot['members'].extend(xRoot['members'])
         yRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         del(xRoot['histogram'])
         del(xRoot['members'])
         xRoot['parent'] = yRoot
     elif xRoot['id'] != yRoot['id']: # Unless x and y are already in same set, merge them
         yRoot['parent'] = xRoot
         xRoot['members'].extend(yRoot['members'])
         xRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         del(yRoot['histogram'])
         del(yRoot['members'])
         xRoot['rank'] = xRoot['rank'] + 1

def Find(x):
     if x['parent']['id'] == x['id']:
        return x
     else:
        x['parent'] = Find(x['parent'])
        return x['parent']

def _createHist(vals,minVal,maxVal):
    th,_=np.histogram(vals,bins=NBINS,range=(minVal,maxVal))
    return(th)

def ComputeClustering(GH,layer,varname=''):
    print('start CC')
    G=GH.copy()

    e2i={}
    i2e={}
    i=0
    for e in G.edges():
        e2i[e]=i
        e2i[(e[1],e[0])]=i
        i2e[i]=e
        i+=1

    # S={}

    firstNode=list(G.nodes())[0]
    minVal=G.node[firstNode][layer]
    maxVal=G.node[firstNode][layer]
    allVals=[]
    nToVisit=[]

    pos={}
    for n in G.nodes():
        pos[n]=[G.node[n]['x'],G.node[n]['y']]
    for e in G.edges():
        G[e[0]][e[1]]['level']=-1

    for n in G.nodes():
        G.node[n]['parent']=G.node[n]
        G.node[n]['rank']=0
        G.node[n]['id']=n
        G.node[n]['members']=[n,]
        # G.node[n]['histogram']=np.zeros((NBINS,))

        if (G.node[n][layer] is not None):
            allVals.append(G.node[n][layer])
            nToVisit.append(n)
            minVal=min((minVal,G.node[n][layer]))
            maxVal=max((maxVal,G.node[n][layer]))

    print('Value range: {0}-{1}'.format(minVal,maxVal))

    for n in nToVisit:
        G.node[n]['histogram']=_createHist(G.node[n][layer],minVal,maxVal,)
        
    print('starting clustering')
    E={e2i[e]:True for e in G.edges()}
    NE=len(E.keys())
    # NG=len(G.nodes())

    level=0
    # roots=set([Find(G.node[x])['id'] for x in G.nodes()])
    # S[level]=[set(G.node[y]['members']) for y in roots]

    while (NE>0):
        print('-----------------\n\nlevel ',level)
        # nC=len(set([Find(G.node[n])['id'] for n in G.nodes()]))
        # print('#Clusters ',nC)

        level+=1

        H = {}
        queued = dict()
        dv=[]
        for ee in E:
            if (E[ee]==False):
                continue

            e=i2e[ee]
            x=Find(G.node[e[0]])
            xid=x['id']
            y=Find(G.node[e[1]])
            yid=y['id']
            if (xid!=yid):
                K=(min((xid,yid)),max((xid,yid)))
                if K not in queued:
                    queued[K]=True
                    numel=min((len(x['members']),len(y['members'])))
                    cD=_clusterDistance(G, x, y, layer=layer)
                    if (numel not in H):
                        H[numel]=[]
                    heappush(H[numel],(cD,K,(x,y)))
                    dv.append(cD)
        if (not dv):
            break

        quantileThreshold=np.percentile(dv,25)
        # MergeAtLeast=np.max([10,0.05*len(H)])
        print('QT {0:2.3f} (min:{1:2.3f}, max:{2:2.3f}, median:{3:2.3f}'.format(quantileThreshold,np.min(dv),np.max(dv),np.median(dv)))


        print('Weights done',len(H))
        to_merge = []
        used = {}
        el=[]
        for numel in sorted(H.keys()):
            while len(H[numel])>0:
                el=heappop(H[numel])
                x,y=el[2]
                if (el[0]>quantileThreshold):# and (len(to_merge)>(MergeAtLeast))):
                    # print('{0} broke with {1:3.2f}'.format(numel,el[0]))
                    break
                if (x['id'] in used) or (y['id']  in used):
                    continue
                used[x['id']]=True
                used[y['id']]=True
                to_merge.append((x,y))
            # print('{0} - edges {1}'.format(numel,len(to_merge)))

        print('merge selection done: {0} clusters to merge '.format(len(used)))

        removedEdges=0
        for (x,y) in to_merge:
            x=Find(x)
            y=Find(y)
            XE=set([e2i[e] for e in list(G.edges(x['members']))])
            YE=set([e2i[e] for e in list(G.edges(y['members']))])
            rE=list(XE.intersection(YE))
            removedEdges+=len(rE)
            for ee in list(rE):
                e=i2e[ee]
                G[e[0]][e[1]]['level']=level
                E[ee]=False
                NE-=1
                    
            Union(x,y)
        print('merging done', removedEdges)


        roots=set([Find(G.node[x])['id'] for x in G.nodes()])
        print('level {0} #clusters {1}'.format(level,len(roots)))#,sum([len(G.node[y]['members']) for y in roots]))
        # plt.figure()
        # plt.hist([len(G.node[y]['members']) for y in roots])
        # plt.show()
    return(G)