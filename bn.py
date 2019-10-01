#%%
import networkx as nx
import pandas as pd
import re

#%%
G = nx.Graph()
G.add_edge('A', 'B', weight=4)
G.add_edge('B', 'D', weight=2)
G.add_edge('A', 'C', weight=3)
G.add_edge('C', 'D', weight=4)
nx.shortest_path(G, 'A', 'D', weight='weight')

#%%

class Node:
  isQueryVariable = None
  isEvidenceVariable = None


#%% data frame stuff
inputFile = open('inputs/network_option_a.txt')
data = {'parent1': [], 'parent2': []}

for line in inputFile:
  nodeName = line[0 : line.find(':')]

  parsed = re.findall(r'\[([^]]*)\]', line)
  parents = parsed[0]
  table = parsed[1]

  split = parents.split(' ')
  if(len(split) == 1):
    parent1 = split[0]
    # 1 parent
    data['parent1'].append([parent1 + ' F', parent1 + ' T'])
    data['parent2'].append([None, None])
  elif(len(split) == 2):
    # 2 parents
    data['parent1'] = [split[0] + ' F', split[0] + ' F', split[0] + ' T', split[0] + ' T']
    data['parent2'] = [split[1] + ' F', split[1] + ' T', split[1] + ' F', split[1] + ' T']

# print(data)



  #, 'node1 F': [.35, .23], 'node1 T': [.65, .77]
df = pd.DataFrame(data=data)
print(df)

#%%
