#!/usr/bin/python3

# Imports
import json
import socket
import sys
import time
import copy

################################################################################
# Globals
visited = dict()
rumored = dict()
timedout = dict()


################################################################################
# Functions
# Generate DHT ping request string
def getDHTPingRequest(key, coords, target=None):
    if target:
        return '{{"keepalive":true, "request":"dhtPing", "box_pub_key":"{}", "coords":"{}", "target":"{}"}}'.format(key, coords, target)
    else:
        return '{{"keepalive":true, "request":"dhtPing", "box_pub_key":"{}", "coords":"{}"}}'.format(key, coords)


################################################################################
# Run
def run():
    # Handle command-line args
    if len(sys.argv) == 3:
        LOCAL_ADMIN = False
        host_port = (sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) == 1:
        LOCAL_ADMIN = True
        usockaddr = '/var/run/yggdrasil.sock'
    else:
        raise Exception("Bad command line args")

    # Execute request on admin socket
    def doRequest(reqstr):
        try:
            if LOCAL_ADMIN:
                ygg = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                ygg.connect(usockaddr)
            else:
                ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ygg.connect(host_port)
            ygg.send(str.encode(reqstr))
            rcv = ygg.recv(1024*15)
            data = json.loads(rcv.decode())
            return data
        except:
            return None

    # Get node info
    def getNodeInfo(key, coords):
        try:
            req = '{{"keepalive":true, "request":"getNodeInfo", "box_pub_key":"{}", "coords":"{}"}}'.format(
                key, coords)
            if LOCAL_ADMIN:
                ygg = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                ygg.connect(usockaddr)
            else:
                ygg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ygg.connect(host_port)
            ygg.send(str.encode(req))
            rcv = ygg.recv(1024*15)
            data = json.loads(rcv.decode())
            return data
        except:
            return None

    # Get Info about first node
    selfInfo = doRequest('{"keepalive":true, "request":"getSelf"}')

    for k, v in selfInfo['response']['self'].items():
        rumored[k] = v

    # Sort response nodes into dicts
    def handleResponse(address, info, data):
        # Assume time-out. Otherwise this will be deleted
        timedout[str(address)] = {'box_pub_key': str(info['box_pub_key']),
                                  'coords': str(info['coords'])
                                  }

        # If it actually did time-out, or the response is broken/empty, return
        if not data:
            return
        if 'response' not in data:
            return
        if 'nodes' not in data['response']:
            return

        # Identify unvisited nodes
        for addr, rumor in data['response']['nodes'].items():
            # Ignore already visited connected nodes
            if addr in visited:
                continue

            rumored[addr] = rumor

        # Store info from responding node if it is unvisited
        if address not in visited:
            now = time.time()
            visited[str(address)] = {'box_pub_key': str(info['box_pub_key']),
                                     'coords': str(info['coords']),
                                     'time': now
                                     }

            # Undo time-out assumption
            if address in timedout:
                del timedout[address]

            # Print info
            nodeinfo = getNodeInfo(
                str(info['box_pub_key']), str(info['coords']))

            nodename = None
            try:
                if nodeinfo and 'response' in nodeinfo and 'nodeinfo' in nodeinfo['response'] and 'name' in nodeinfo['response']['nodeinfo']:
                    nodename = '"' + \
                        str(nodeinfo['response']['nodeinfo']['name']) + '"'
            except:
                pass
            if nodename:
                print('"{}": ["{}", {}, {}],'.format(
                    address, info['coords'], int(now), nodename))
            else:
                print('"{}": ["{}", {}],'.format(
                    address, info['coords'], int(now)))

    print('{"yggnodes": {')
    while len(rumored) > 0:
        rmr = copy.copy(rumored)
        for k, v in rmr.items():
            handleResponse(k, v, doRequest(
                getDHTPingRequest(v['box_pub_key'], v['coords'])))
            # Old kad node workaround
            handleResponse(k, v, doRequest(getDHTPingRequest(
                v['box_pub_key'], v['coords'], '0'*128)))
            handleResponse(k, v, doRequest(getDHTPingRequest(
                v['box_pub_key'], v['coords'], 'f'*128)))

        del rumored[k]
    print('\n}}')

    # Save visited nodes as json
    visited_json = json.dumps(visited)
    f = open("visited.json", "w")
    f.write(visited_json)
    f.close()

    # Save timedout nodes as json
    timedout_json = json.dumps(timedout)
    f = open("timedout.json", "w")
    f.write(timedout_json)
    f.close()


################################################################################
# Main
if __name__ == "__main__":
    run()
