#%%
import networkx as nx
import pandas as pd
import re

#%%
# class representing a node
class Node:
  status = None
  def __init__(self, nodeName, parents, cpt):
    self.nodeName = nodeName
    self.parents = parents
    self.cpt = cpt # conditional probability table
  
  # when we print this node, print the node name
  def __repr__(self):
    return self.nodeName

#%%
# sets the status of each node
def setStatus(fileName, nodes):
  inputFile = open(fileName)
  line = inputFile.readline().rstrip() # read line and strip \n
  parsed = line.split(',') # split by commas
  for i,char in enumerate(parsed): # go through nodes and assign them their status character
    nodes[i].status = char
    
  
#%% 
# get a list of the nodes from the file name
def getNodes(networkFileName, queryFileName):
  inputFile = open(networkFileName)
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
  
  setStatus(queryFileName, nodes)

  # now we need to convert the strings of parents to their actual node objects
  parentsToNodes(nodes)
  return nodes

# given our nodes with parents encoded as strings, convert each parent to a Node object
def parentsToNodes(nodes):
  for node in nodes:
    actualParents = []
    for parent in node.parents:
      for n in nodes:
        if(parent == n.nodeName):
            actualParents.append(n)
    node.parents = actualParents

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
def generateNetwork(networkFileName, queryFileName):
  network = nx.nx.DiGraph(directed=True)
  nodes = getNodes(networkFileName, queryFileName)
  
  for node in nodes:
    for parent in node.parents:
      network.add_edge(parent, node)

  return network
#%%
# generate our network and draw it
network = generateNetwork('inputs/network_option_a.txt', 'inputs/query1.txt')
#nx.draw(network, arrows=True, with_labels=True)
