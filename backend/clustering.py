import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pylab as plt
import numpy as np
from scipy.spatial.distance import cdist,euclidean
from scipy.ndimage import gaussian_filter
from heapq import heappop, heappush,heapify
from random import sample
from matplotlib import cm
from pyemd import emd
import matplotlib.pylab as plt

NBINS=100
MD=np.eye(NBINS+4)
# plt.figure()
# plt.imshow(MD)
# plt.colorbar()
MD=gaussian_filter(MD,10)
MD=(MD[2:-2,2:-2]).copy(order='C')
# print(MD.shape,NBINS)
# plt.figure()
# plt.imshow(MD)
# plt.colorbar()
# plt.show()
#https://stackoverflow.com/questions/4211209/remove-all-the-elements-that-occur-in-one-list-from-another
def _filter_list(full_list, excludes):
    s = set(excludes)
    return (x for x in full_list if x not in s)

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

def _clusterDistance(G,C1,C2,layer,sampleSize):
    h1=C1['histogram']
    s1=np.sum(h1)
    if (s1>0):
        h1=h1/s1
    h2=C2['histogram']
    s2=np.sum(h2)
    if (s2>0):
        h2=h2/s2
    return(euclidean(h1,h2))
    # return(emd(h1,h2,MD))


def Union(x, y):
     xRoot = Find(x)
     yRoot = Find(y)
     if xRoot['rank'] > yRoot['rank']:
         xRoot['members'].extend(yRoot['members'])
         xRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         yRoot['members']=[]
         yRoot['parent'] = xRoot
     elif xRoot['rank'] < yRoot['rank']:
         yRoot['members'].extend(xRoot['members'])
         yRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         xRoot['members']=[]         
         xRoot['parent'] = yRoot
     elif xRoot['id'] != yRoot['id']: # Unless x and y are already in same set, merge them
         yRoot['parent'] = xRoot
         xRoot['members'].extend(yRoot['members'])
         xRoot['histogram']=xRoot['histogram']+yRoot['histogram']
         yRoot['members']=[]         
         xRoot['rank'] = xRoot['rank'] + 1

def Find(x):
     if x['parent']['id'] == x['id']:
        return x
     else:
        x['parent'] = Find(x['parent'])
        return x['parent']

def _updateHist(hist,minVal,maxVal,vals):
    th,_=np.histogram(vals,bins=NBINS,range=(minVal,maxVal))
    return(hist+th)

def ComputeClustering(H,layer,sampleSize=50,varname=''):
    print('start CC')
    G=H.copy()

    e2i={}
    i2e={}
    i=0
    for e in G.edges():
        e2i[e]=i
        e2i[(e[1],e[0])]=i
        i2e[i]=e
        i+=1

    S={}

    firstNode=list(G.nodes())[0]
    minVal=G.node[firstNode][layer]
    maxVal=G.node[firstNode][layer]
    allVals=[]
    nToVisit=[]
    for n in G.nodes():
        G.node[n]['parent']=G.node[n]
        G.node[n]['rank']=0
        G.node[n]['id']=n
        G.node[n]['members']=[n,]
        G.node[n]['histogram']=np.zeros((NBINS,))
        if (G.node[n][layer] is not None):
            allVals.append(G.node[n][layer])
            nToVisit.append(n)
            minVal=min((minVal,G.node[n][layer]))
            maxVal=max((minVal,G.node[n][layer]))

    for n in nToVisit:
        G.node[n]['histogram']=_updateHist(G.node[n]['histogram'],minVal,maxVal,G.node[n][layer])
        
    print('starting clustering')
    E={e2i[e]:True for e in G.edges()}
    NE=len(E.keys())
    # NG=len(G.nodes())

    level=0
    roots=set([Find(G.node[x])['id'] for x in G.nodes()])
    S[level]=[set(G.node[y]['members']) for y in roots]

    while (NE>0):
        print('-----------------\n\nlevel ',level)
        # nC=len(set([Find(G.node[n])['id'] for n in G.nodes()]))
        # print('#Clusters ',nC)


        level+=1

        H = []
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
                    cD=_clusterDistance(G, x, y, layer=layer,sampleSize=sampleSize)
                    heappush(H,(cD,K,(x,y)))
                    dv.append(cD)
        if (not dv):
            break


        qT=np.percentile(dv,10)
        TLH=0.005*len(H)


        print('Weights done',len(H))
        to_merge = []
        used = {}
        
        while len(H)>0:
            el=heappop(H)
            x,y=el[2]
            if ((el[0]>qT) and (len(to_merge)>(TLH))):
                print('broke with',el[0],qT)
                break
            if (x['id'] in used) or (y['id']  in used):
                continue
            used[x['id']]=True
            used[y['id']]=True
            to_merge.append((x,y))

        print('merge selection done: {0} to do, {1} used '.format(len(to_merge),len(used)))

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
        # print(level,roots,len(roots),sum([len(G.node[y]['members']) for y in roots]))
        S[level]=[set(G.node[y]['members']) for y in roots]

    # _plotGraph(G,layer)
    
    T=nx.DiGraph()
    T.add_node((-1,-1))
    T.node[(-1,-1)]['len']=len(G.nodes())
    
    for k in sorted(S.keys(),reverse=True):
        for i in range(len(S[k])):
            T.add_node((k,i))
            T.node[(k,i)]['len']=len(S[k][i])
            if (k+1) in S:
                for j in range(len(S[k+1])):
                    inter=(S[k][i]).intersection(S[k+1][j])
                    if len(inter)>0:
                        T.add_edge((k,i),(k+1,j))
                        T[(k,i)][(k+1,j)]['inter']=len(inter)
            else:
                T.add_edge((k,i),(-1,-1))
                T[(k,i)][(-1,-1)]['inter']=1

    pos=graphviz_layout(T, prog='dot')
    nx.draw(T,pos=pos,node_size=[T.node[n]['len']/10 for n in T.nodes()])#,width=[T[e[0]][e[1]]['inter']/10 for e in T.edges()])
    plt.savefig('im_{0}.png'.format(varname),dpi=600)
    plt.close()

    nx.write_gpickle(T,'gr_{0}.gp'.format(varname))

    #     plt.figure()
    #     plt.hist(S[k],20)
    # plt.show()
    return(G)

if __name__=="__main__":
    h=np.zeros((NBINS,))
    print(h)
    h=_updateHist(h,0,1,[0,1])
    print(h)
    print('\n')
    for i in range(NBINS):
        print('\n')
        print(h)
        v=i/NBINS
        h=_updateHist(h,0,1,v)
        print(v,h)