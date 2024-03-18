FROM quay.io/jupyterhub/configurable-http-proxy:4.6.1

ARG SSL_KEY_FILE
ARG SSL_CRT_FILE
ARG SSL_CA_FILE

USER 0

COPY ${SSL_KEY_FILE} /etc/ssl/private/jupyterhub_proxy.key
COPY ${SSL_CRT_FILE} /etc/ssl/certs/jupyterhub_proxy.crt
COPY ${SSL_CA_FILE} /etc/ssl/certs/jupyterhub_proxy_chain.crt

CMD [ \
        "--port=8000", \
        "--api-port=8001", \
        "--default-target=http://jupyterhub_hub:8081", \
        "--error-target=http://jupyterhub_hub:8081/hub/error", \
        "--ssl-key=/etc/ssl/private/jupyterhub_proxy.key", \
        "--ssl-cert=/etc/ssl/certs/jupyterhub_proxy.crt", \
        "--ssl-ca=/etc/ssl/certs/jupyterhub_proxy_chain.crt" \
    ]