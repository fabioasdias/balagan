import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pylab as plt
from glob import glob
from os.path import exists

for f in glob('gr_*.gp'):
    pngName=f.replace('gp','png')
    if exists(pngName):
        continue
    print(f)
    T=nx.read_gpickle(f)
    pos=graphviz_layout(T, prog='dot')
    nx.draw(T,pos=pos,node_size=[T.node[n]['len']/10 for n in T.nodes()])#,width=[T[e[0]][e[1]]['inter']/10 for e in T.edges()])
    plt.savefig(pngName,dpi=600)
    plt.close()
