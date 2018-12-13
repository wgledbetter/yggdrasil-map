#!/usr/bin/env python
from flask import Config
from database import NodeDB
import graphPlotter

import urllib, json
url = "current" #alternatively "http://y.yakamo.org:3000/current"

# nodes indexed by coords
class NodeInfo:
  def __init__(self, ip, coords):
    self.ip = str(ip)
    self.label = str(ip) # TODO readable labels
    self.coords = str(coords)
    self.version = "unknown"
  def getCoordList(self):
    return self.coords.strip("[]").split(" ")
  def getParent(self):
    p = self.getCoordList()
    if len(p) > 0: p = p[:-1]
    return "[" + " ".join(p).strip() + "]"
  def getLink(self):
    c = self.getCoordList()
    return int(self.getCoordList()[-1].strip() or "0")

class LinkInfo:
  def __init__(self, a, b):
    self.a = a # NodeInfo
    self.b = b # NodeInfo

def generate_graph(time_limit=60*60*3):
    response = urllib.urlopen(url)
    data = json.loads(response.read())["yggnodes"]

    toAdd = []
    for ip in data:
      info = NodeInfo(ip, data[ip][0])
      toAdd.append(info)

    nodes = dict()
    def addAncestors(info):
      parent = NodeInfo("?", info.getParent())
      parent.label = "{} {}".format(parent.ip, parent.coords)
      nodes[parent.coords] = parent
      if parent.coords != parent.getParent(): addAncestors(parent)

    for info in toAdd: addAncestors(info)
    for info in toAdd: nodes[info.coords] = info

    sortedNodes = sorted(nodes.values(), key=(lambda x: x.getLink()))
    #for node in sortedNodes: print node.ip, node.coords, node.getParent(), node.getLink()

    edges = []
    for node in sortedNodes:
      if node.coords == node.getParent: continue
      edges.append(LinkInfo(node, nodes[node.getParent()]))

    print '%d nodes, %d edges' % (len(nodes), len(edges))

    graph = graphPlotter.position_nodes(nodes, edges)
    js = graphPlotter.get_graph_json(graph)

    with open('static/graph.json', 'w') as f:
        f.write(js)


def load_graph_from_db(time_limit):
    config = Config('./')
    config.from_pyfile('web_config.cfg')

    with NodeDB(config) as db:
        nodes = db.get_nodes(time_limit)
        edges = db.get_edges(nodes, 60*60*24*7)
        return (nodes, edges)


if __name__ == '__main__':
    generate_graph()
