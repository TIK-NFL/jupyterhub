FROM jupyterhub/jupyterhub:4.0.2

RUN apt-get update && \
    apt-get -y install jupyter ssl-cert vim wget unzip jq

RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    mysql-connector-python

COPY jupyterhub_config.py .
COPY proxy.py /usr/local/lib/python3.10/dist-packages/jupyterhub/proxy.py
