FROM quay.io/jupyterhub/configurable-http-proxy:4.6.2

ARG SSL_KEY_FILE=jupyterhub_proxy.key
ARG SSL_CRT_FILE=jupyterhub_proxy.crt
ARG SSL_CA_FILE=''

ENV SSL_KEY_FILE=${SSL_KEY_FILE:+/etc/ssl/jupyter-docker-ssl/${SSL_KEY_FILE}}
ENV SSL_CRT_FILE=${SSL_CRT_FILE:+/etc/ssl/jupyter-docker-ssl/${SSL_CRT_FILE}}
ENV SSL_CA_FILE=${SSL_CA_FILE:+/etc/ssl/jupyter-docker-ssl/${SSL_CA_FILE}}


USER 0

ENTRYPOINT /srv/configurable-http-proxy/chp-docker-entrypoint \
        --port=8000 \
        --api-port=8001 \
        --default-target=http://jupyterhub_hub:8081 \
        --error-target=http://jupyterhub_hub:8081/hub/error \
        --ssl-key=${SSL_KEY_FILE} \
        --ssl-cert=${SSL_CRT_FILE} \
        --ssl-ca=${SSL_CA_FILE}