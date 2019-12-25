import json
import socket
import sys
import time

#gives the option to get data from an external server instead and send that
#if no options given it will default to localhost instead
if len(sys.argv) == 3:
  host_port = (sys.argv[1], int(sys.argv[2]))
else:
  host_port = ('localhost', 9001)

def getDHTPingRequest(key, coords, target=None):
  if target:
    return '{{"keepalive":true, "request":"dhtPing", "box_pub_key":"{}", "coords":"{}", "target":"{}"}}'.format(key, coords, target)
  else:
    return '{{"keepalive":true, "request":"dhtPing", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords)

def doRequest(req):
  try:
    ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ygg.connect(host_port)
    ygg.send(req)
    data = json.loads(ygg.recv(1024*15))
    return data
  except:
    return None

def getNodeInfo(key, coords):
  try:
    req = '{{"keepalive":true, "request":"getNodeInfo", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords)
    ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ygg.connect(host_port)
    ygg.send(req)
    data = json.loads(ygg.recv(1024*15))
    return data
  except:
    return None

visited = dict() # Add nodes after a successful lookup response
rumored = dict() # Add rumors about nodes to ping
timedout = dict()
def handleResponse(address, info, data):
  global visited
  global rumored
  global timedout
  timedout[str(address)] = {'box_pub_key':str(info['box_pub_key']), 'coords':str(info['coords'])}
  if not data: return
  if 'response' not in data: return
  if 'nodes' not in data['response']: return
  for addr,rumor in data['response']['nodes'].iteritems():
    if addr in visited: continue
    rumored[addr] = rumor
  if address not in visited:
    # TODO? remove this, it's debug output that happens to be in the same format as yakamo's "current" json file
    now = time.time()
    visited[str(address)] = {'box_pub_key':str(info['box_pub_key']), 'coords':str(info['coords']), 'time':now}
    if address in timedout: del timedout[address]
    nodeinfo = getNodeInfo(str(info['box_pub_key']), str(info['coords']))
    #print "\nDEBUG:", info, nodeinfo
    if len(visited) > 1: sys.stdout.write(",\n")
    nodename = None
    try:
      if nodeinfo and 'response' in nodeinfo and 'nodeinfo' in nodeinfo['response'] and 'name' in nodeinfo['response']['nodeinfo']:
        nodename = '"' + str(nodeinfo['response']['nodeinfo']['name']) + '"'
    except:
      pass
    if nodename:
      sys.stdout.write('"{}": ["{}", {}, {}]'.format(address, info['coords'], int(now), nodename))
    else:
      sys.stdout.write('"{}": ["{}", {}]'.format(address, info['coords'], int(now)))
    sys.stdout.flush()
# End handleResponse

# Get self info
selfInfo = doRequest('{"keepalive":true, "request":"getSelf"}')

# Initialize dicts of visited/rumored nodes
for k,v in selfInfo['response']['self'].iteritems(): rumored[k] = v

# Loop over rumored nodes and ping them, adding to visited if they respond
print '{"yggnodes": {'
while len(rumored) > 0:
  for k,v in rumored.iteritems():
    handleResponse(k, v, doRequest(getDHTPingRequest(v['box_pub_key'], v['coords'])))
    # These next two are imperfect workarounds to deal with old kad nodes
    #handleResponse(k, v, doRequest(getDHTPingRequest(v['box_pub_key'], v['coords'], '0'*128)))
    #handleResponse(k, v, doRequest(getDHTPingRequest(v['box_pub_key'], v['coords'], 'f'*128)))
    break
  del rumored[k]
print '\n}}'
#End

# TODO do something with the results

#print visited
#print timedout
