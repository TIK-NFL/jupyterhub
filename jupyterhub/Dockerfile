FROM jupyterhub/jupyterhub:main


# ======================================================================================================================
# General packages and jupyterhub dependencies
#

RUN apt-get update && \
    apt-get -y install jupyter ssl-cert vim wget unzip jq

RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    mysql-connector-python \
    jupyterhub-idle-culler


# ======================================================================================================================
# Jupyter extensions
#

RUN jupyter nbextension enable --py widgetsnbextension


# ======================================================================================================================
# Config
#

COPY jupyterhub_config.py .
COPY proxy.py /usr/local/lib/python3.10/dist-packages/jupyterhub/proxy.py
