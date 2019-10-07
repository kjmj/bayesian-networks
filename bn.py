import networkx as nx
import pandas as pd
import re
import random
import sys

# class representing a node
class Node:
  status = None

  def __init__(self, nodeName, parents, cpt):
    self.nodeName = nodeName
    self.parents = parents
    self.cpt = cpt  # conditional probability table

  # when we print this node, print the node name
  def __repr__(self):
    return self.nodeName


# sets the status of each node
def setStatus(fileName, nodes):
  inputFile = open(fileName)
  line = inputFile.readline().rstrip()  # read line and strip \n
  parsed = line.split(',')  # split by commas
  for i, char in enumerate(parsed):  # go through nodes and assign them their status character
    nodes[i].status = char


# get a list of the nodes from the file name
def getNodes(networkFileName, queryFileName):
  inputFile = open(networkFileName)
  nodes = []

  # create a list of nodes
  for line in inputFile:
    parsed = re.findall(r'\[([^]]*)\]', line)  # split by []
    nodeName = line[0: line.find(':')]
    parents = []  # parents of this node
    if(parsed[0] != ''):  # skip nodes with no parents
      parents = parsed[0].split(' ')  # this needs to be empty array
    probabilities = parsed[1].split(' ')  # get our probabilities
    cpt = createCPT(probabilities, parents, nodeName)  # create our cpt

    nodes.append(Node(nodeName, parents, cpt))  # create a node and append it to the list

  # set the status of our nodes
  setStatus(queryFileName, nodes)

  # now we need to convert the strings of parents to their actual node objects
  parentsToNodes(nodes)

  return nodes

# create a conditional probability table
def createCPT(probabilities, parents, nodeName):
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
  return cpt

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


# generate a bayseian network from the given file name
def generateNetwork(networkFileName, queryFileName):
  network = nx.nx.DiGraph(directed=True)
  nodes = getNodes(networkFileName, queryFileName)

  for node in nodes:
    for parent in node.parents:
      network.add_edge(parent, node)

  return network

# get the sample value from the node
def findSampleVal(node, values):
  if len(node.parents) is 0:
    for col in node.cpt:
      if 'F' in col:
        cptValue = node.cpt[col][0]
    return cptValue
  for parent in node.parents:
    values[parent] = weightedProbabilities(parent, values)
  i = 0
  for parent in node.parents:
    if(values[parent]):
      i += (2 ** node.parents.index(parent))
  for col in node.cpt:
    if 'F' in col:
      cptValue = node.cpt[col][i]
    return cptValue

# samples a bayesian network
def priorSampling(network):
  values = {}
  for node in network:
    rand = random.uniform(0,1)
    val = findSampleVal(node, values)
    values[node.nodeName] = True if rand < val else False 
  return values

# query for evidence on the network
def queryEvidence(network):
  a = {}
  e = {}
  for n in network:
    if n.status == 't':
      e[n.nodeName] = True
    elif n.status == 'f':
      e[n.nodeName] = False
    elif n.status == '?':
      a['X'] = n.nodeName
    a['e'] = e
  return a

# determine if x is consistent with e
def isConsistent(x, e):
  flag = True
  for n in x:
    if n in e and x[n] != e[n]:
      flag = False
  return flag

# run rejection sampling as outlined in the book
def rejectionSampling(X, e, bn, N):
  n = {True: 0, False: 0}
  for j in range(1, N):
    x = priorSampling(bn)
    if isConsistent(x, e):
      b = x[X]
      n[b] += 1
  return normalize(n)

# normalize our data
def normalize(n):
  if sum(n.values()) > 0:
    normalized = {}
    for k, v in n.items():
      normalized[k] = float(v) / sum(n.values())
    return normalized
  else:
    return None

# calculate weighted probabilites
def weightedProbabilities(node, values):
  if len(node.parents) is 0:
    for col in node.cpt:
      if 'F' in col:
        cptValue = node.cpt[col][0]
    return cptValue
  for parent in node.parents:
    values[parent] = weightedProbabilities(parent, values)
  i = 0
  for parent in node.parents:
    if(values[parent]):
      i += (2 ** node.parents.index(parent))
  for col in node.cpt:
    if 'F' in col:
      cptValue = node.cpt[col][i]
    return cptValue

# get weighted sample for the network and e
def weightedSample(network, e):
  val = {}
  i = 0
  w = 1
  v = None
  for node in network:
    r = random.uniform(0, 1)
    probabilities = r
    # node has paprents
    if len(node.parents) > 0:
      # get probabilities
      probabilities = weightedProbabilities(node, val)
    # no parents for this node
    else:
      for col in node.cpt:
        if 'F' in col:
          probabilities = node.cpt[col][0]
    # evidence node
    if node.nodeName in e:
      if not e[node.nodeName]:
        w *= (1 - probabilities)
      else:
        w *= probabilities
    else:
      if r < probabilities:
        val[node.nodeName] = True
      else:
        val[node.nodeName] = False
    i += 1
  return val, w

# calculate out likelihood weighting as in the book
def likelihoodWeighting(X, e, bn, N):
  W = {True: 0, False: 0}
  for j in range(1, N):
    x, w = weightedSample(bn, e)
    b = x[X]
    W[b] += w
  return normalize(W)

def main():
    numSamples = int(sys.argv[3])
    # generate our network
    network = generateNetwork(sys.argv[1], sys.argv[2])
    evidence = queryEvidence(network)

    # run rejection sampling
    rs = rejectionSampling(evidence['X'], evidence['e'], network, numSamples)
    print('Rejection Sampling', rs)

    # run likelihood weighting
    lw = likelihoodWeighting(evidence['X'], evidence['e'], network, numSamples)
    print('Likelihood Weighting', lw)

main()