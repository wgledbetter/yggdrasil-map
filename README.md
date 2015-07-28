# fc00.org

Source code for http://fc00.atomshare.net (http://h.fc00.atomshare.net on Hyperboria).

## Sending your view of the network

```bash
wget https://raw.githubusercontent.com/zielmicha/fc00.org/master/scripts/sendGraph.py
nano sendGraph.py
chmod +x sendGraph.py

# Run this every 5-60 minutes
./sendGraph.py
```

## Web server
```bash
git clone git@github.com:zielmicha/fc00.org.git
git clone git@github.com:zielmicha/nodedb.git web/nodedb
sudo apt-get install python-flask python-flup python-mysqldb python-pygraphviz

cd fc00.org/web
python web.py
```

Run `web/updateGraph.py` periodically to rerender nodes graph. You may want to customize reverse-proxy IP retrieval logic in web.py.
