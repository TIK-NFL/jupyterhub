FROM jupyterhub/jupyterhub:main

RUN apt-get update && \
    apt-get -y install jupyter ssl-cert vim wget unzip jq

RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    mysql-connector-python \
    jupyterhub-idle-culler

COPY jupyterhub_config.py .
COPY proxy.py /usr/local/lib/python3.10/dist-packages/jupyterhub/proxy.py
