FROM quay.io/jupyterhub/jupyterhub:4.0.2


# ======================================================================================================================
# General packages and jupyterhub dependencies
#

RUN apt-get update && \
    apt-get -y install jupyter ssl-cert patch vim wget unzip jq python3-psycopg2

RUN python3 -m pip install --no-cache-dir \
    dockerspawner \
    jupyterhub-idle-culler


# ======================================================================================================================
# Jupyter extensions
#

RUN jupyter nbextension enable --py widgetsnbextension


# ======================================================================================================================
# Patches
#

COPY patches/cookies.py.patch /tmp/cookies.py.patch
RUN patch /usr/lib/python3.10/http/cookies.py < /tmp/cookies.py.patch

# ======================================================================================================================
# Config
#

COPY jupyterhub_config.py .