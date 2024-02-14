FROM jupyterhub/configurable-http-proxy:4

USER 0

RUN apk update && apk add openssl

RUN openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
    -keyout /etc/ssl/private/jupyterhub_proxy.key \
    -out /etc/ssl/certs/jupyterhub_proxy.crt \
    -subj "/CN=jupyterhub_proxy" \
    -addext "subjectAltName=DNS:jupyterhub_proxy,IP:127.0.0.1"

CMD [ \
        "--ssl-key=/etc/ssl/private/jupyterhub_proxy.key", \
        "--ssl-cert=/etc/ssl/certs/jupyterhub_proxy.crt", \
        "--api-ssl-key=/etc/ssl/private/jupyterhub_proxy.key", \
        "--api-ssl-cert=/etc/ssl/certs/jupyterhub_proxy.crt" \
    ]