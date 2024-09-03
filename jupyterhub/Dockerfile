FROM quay.io/jupyterhub/jupyterhub:5.1.0


# ======================================================================================================================
# General packages and jupyterhub dependencies
#

RUN apt-get update && \
    apt-get -y install jupyter ssl-cert patch vim wget unzip jq python3-psycopg2 git

RUN python3 -m pip install --no-cache-dir  \
    dockerspawner  \
    jupyterhub-idle-culler \
    git+https://github.com/TIK-NFL/jupyterhub-ltiauthenticator.git@multiauth_support \
    git+https://github.com/TIK-NFL/jupyterhub-multiauthenticator.git@lti_support


# ======================================================================================================================
# Jupyter extensions
#

RUN jupyter nbextension enable --py widgetsnbextension


# ======================================================================================================================
# Config
#

COPY jupyterhub_config.py .