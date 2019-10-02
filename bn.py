#%%
import networkx as nx
import pandas as pd
import re

#%%
# class representing a node
class Node:
  def __init__(self, nodeName, parents, cpt):
    self.nodeName = nodeName
    self.parents = parents
    self.cpt = cpt # conditional probability table
    
    # todo deal with these variables when we need to
    # isQueryVariable = None
    # isEvidenceVariable = None
  
#%% 
# get a list of the nodes from the file name
def getNodes(fileName):
  inputFile = open(fileName)
  nodes = []

  for line in inputFile:
    parsed = re.findall(r'\[([^]]*)\]', line) # split by []
    nodeName = line[0 : line.find(':')]
    parents = [] # parents of this node
    if(parsed[0] != ''): # skip nodes with no parents
      parents = parsed[0].split(' ') # this needs to be empty array
    probabilities = parsed[1].split(' ') # get our probabilities
    
    data = {}

    # split our probability data into two columns
    fData, tData = seperateData(probabilities)
    data['p(' + nodeName + '=F)'] = fData
    data['p(' + nodeName + '=T)'] = tData

    # process parents
    if(len(parents) == 1 and parents[0] != ''):
      data['parent1'] = ['parent=F', 'parent=T']
    elif(len(parents) == 2):
      data['parent1'] = ['parent1=F', 'parent1=F', 'parent1=T', 'parent1=T']
      data['parent2'] = ['parent2=F', 'parent2=T', 'parent2=F', 'parent2=T']

    # now we can create our node
    cpt = pd.DataFrame(data=data)
    nodes.append(Node(nodeName, parents, cpt))
  return nodes

#%%
# helper function to seperate the data into two columns, true and false
def seperateData(probabilities):
    fData = []
    tData = []
    for i, probability in enumerate(probabilities):
      # even
      if(i % 2 == 0):
        fData.append(float(probability))
      # odd
      if(i % 2 == 1):
        tData.append(float(probability))
    return fData, tData

#%%
# generate a bayseian network from the given file name
def generateNetwork(fileName):
  network = nx.nx.DiGraph(directed=True)
  nodes = getNodes(fileName)

  for node in nodes:
    for parent in node.parents:
      network.add_edge(parent, node.nodeName)

  return network
#%%
# gnerate our network and draw it
network = generateNetwork('inputs/network_option_a.txt')
nx.draw(network, arrows=True, with_labels=True)
