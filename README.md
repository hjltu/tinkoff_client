# tinkoff_client

* Get tinkoff API token:
<br>https://tinkoffcreditsystems.github.io/invest-openapi/

* Install:
<br>git clone https://github.com/hjltu/tinkoff_client.git
<br>cd tinkoff_client
<br>python3 -m venv venv
<br>source venv/bin/activate
<br>pip install --upgrade pip
<br>pip install requests


* Get tinkoff API token:
<br>https://tinkoffcreditsystems.github.io/invest-openapi/
<br>Add token to the file config.py

* Run:
<br>python test.py
<br>or run in docker:
<br>docker  build -f Dockerfile -t tbot .
<br>docker run -ti --rm tbot YOUR_TOKEN
