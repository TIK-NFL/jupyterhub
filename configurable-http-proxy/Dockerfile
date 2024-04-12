FROM quay.io/jupyterhub/configurable-http-proxy:4.6.1

ARG SSL_KEY_FILE=/etc/ssl/jupyter-docker-ssl/jupyterhub_proxy.key
ARG SSL_CRT_FILE=/etc/ssl/jupyter-docker-ssl/jupyterhub_proxy.crt
#ARG SSL_CA_FILE=/etc/ssl/jupyter-docker-certs/jupyterhub_proxy_chain.crt

ENTRYPOINT /srv/configurable-http-proxy/chp-docker-entrypoint \
        --port=8000 \
        --api-port=8001 \
        --default-target=http://jupyterhub_hub:8081 \
        --error-target=http://jupyterhub_hub:8081/hub/error \
        --ssl-key=${SSL_KEY_FILE} \
        --ssl-cert=${SSL_CRT_FILE}
#        --ssl-ca=${SSL_CA_FILE}