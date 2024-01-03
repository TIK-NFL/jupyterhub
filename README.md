# Jupyterhub-Cloud

This reference configuration provides a cloud-based Jupyterhub deployment for integrated usage (e.g., within plugins or frames).
It supports only short-lived sessions which are managed by the DockerSpawner.
A login is only possible by acquiring an authentication token via Jupyterhub API and passing the token either via URL or cookie in future requests.
Jupyterhub is also configured to run within the same Docker network the spawned sessions containers (single user servers) will also run on.
Thus, sufficient number of unbound local IP addresses should be reserved within your Docker network.

This project configuration sets up the following services:

| Service                 | Docker hostname    | External port    |
|-------------------------|--------------------|------------------|
| JupyterHub              | `jupyterhub_hub`   | 8081             |
| Configurable HTTP proxy | `jupyterhub_proxy` | 8000, 8001 (API) |
| MySQL                   | `jupyterhub_db`    | 3306, 33060      |


**WARNING**: All jupyterhub sessions/users are short-lived and will be culled upon expiration which also results in deleting all data created during a session.
Thus, the integrator might want to save all data by requesting it from the REST API server and moving the data to some external resource storage.

## Build and Deployment

1. Clone Jupyterhub-Cloud and enter the base directory of the project.
2. Generate an `.env` file containing definitions of environment variables which are passed to the services we want to build.
    ```
    cat << EOF > .env
    MYSQL_DATABASE=jupyterhub
    MYSQL_ROOT_PASSWORD=$(openssl rand -hex 32)
    DOCKER_NETWORK_NAME=jupyterhub_network
    DOCKER_NOTEBOOK_IMAGE=quay.io/jupyterhub/singleuser:main
    CONFIGPROXY_AUTH_TOKEN=$(openssl rand -hex 32)
    JPY_COOKIE_SECRET=$(openssl rand -hex 64)
    EOF
    ```
   Note that the `openssl rand` commands will generate some secrets such as service tokens and passwords.
3. If you want to use the single user image provided by this project, build the image using
   ```
   docker build -t jupyterhub-cloud-singleuser:main singleuser/
   ```
   and change the `DOCKER_NOTEBOOK_IMAGE` variable to `jupyterhub-cloud-singleuser:main` within the `.env` file.  Note that you might also use another single user server images which deviate from these two options.
4. Build and start all services:
   ```
   docker compose up --build
   ```


## Development

- Debugging
- Cert validation
- Attaching to the jupyterhub_network

## Plugin

- Proxying to jupyterhub / Avoiding CROSS-origin problems 

## Single user server

## Configuration


### Configurable-http-proxy (default arguments)
```
--ip=127.0.0.1 --port=8000 --api-ip=127.0.0.1 --api-port=8001 --default-target=http://jupyterhub_hub:8081 --error-target=http://jupyterhub_hub:8081/hub/error
```

### Apache (minimal config)

```
<VirtualHost _default_:443>
    DocumentRoot /var/www/html

    #
    # SSL config
    #

    SSLEngine on
    SSLCertificateFile	/etc/ssl/certs/server.crt
    SSLCertificateKeyFile /etc/ssl/private/server.key

    #
    # SSL reverse proxy
    #

    SSLProxyEngine On

    # TODO: Disabled for development. Be sure to remove/enable in production environments.
    SSLProxyVerify none
    SSLProxyCheckPeerName off

    # Rewrite rules to proxy websocket connections
    RewriteEngine on
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule /jupyter/(.*) "wss://jupyterhub_proxy:8000/jupyter/$1" [P,L]

    <Location "/jupyter">
        # preserve host header to avoid cross-origin problems
        ProxyPreserveHost on
        ProxyPass         https://jupyterhub_proxy:8000/jupyter
        ProxyPassReverse  https://jupyterhub_proxy:8000/jupyter
        RequestHeader     set "X-Forwarded-Proto" expr=%{REQUEST_SCHEME}
    </Location>

</VirtualHost>
```

#### Resources
- https://jupyterhub.readthedocs.io/en/stable/howto/separate-proxy.html
- https://github.com/jupyterhub/configurable-http-proxy