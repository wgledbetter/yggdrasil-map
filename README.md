# Yggdrasil map

Forked from the code for http://www.fc00.org (http://h.fc00.org on Hyperboria).

## Sending your view of the network

This code reads a map of known nodes from `y.yakamo.org:3000/current` (reachable over yggdrasil). In order to display an accurate map of the network, we need your help. If you run a yggdrasil node, plase send your network view using the [send-view.py](https://github.com/yakamok/Niflheim-api/blob/master/send-view.py) script.

## Web server
```bash
git clone https://github.com/Arceliar/yggdrasil-map.git
sudo apt-get install python-flask python-flup python-mysqldb python-pygraphviz python-networkx

cd yggdrasil-map/web
cp web_config.example.cfg web_config.cfg
python web.py
```

You would need to edit web.py to adjust the address/port the server listens on, and may want to edit the web_config.cfg file. Note that most of the options in web_config.cfg are unused after forking from the fc00.org code, so this is mostly just a workaround until we have time to clean up this code.

Run `web/updateGraph.py` periodically to rerender nodes graph. You may want to customize reverse-proxy IP retrieval logic in web.py.
