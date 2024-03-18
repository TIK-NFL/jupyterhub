# Integrable Jupyterhub

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


## Build and Run using docker-compose

1. Clone Integrable Jupyterhub and enter the base directory of the project.
2. Generate an `.env` file containing definitions of environment variables which are passed to the services we want to build.
    ```
    cat << EOF > .env
    MYSQL_DATABASE=jupyterhub
    MYSQL_ROOT_PASSWORD=$(openssl rand -hex 32)
    DOCKER_NETWORK_NAME=jupyterhub_network
    DOCKER_NOTEBOOK_IMAGE=quay.io/jupyter/base-notebook:hub-4.0.2
    CONFIGPROXY_AUTH_TOKEN=$(openssl rand -hex 32)
    JPY_COOKIE_SECRET=$(openssl rand -hex 64)
    JPY_SERVICE_ADMINS=service-admin:$(openssl rand -hex 64)
    ACCESS_CONTROL_ORIGINS= # <origins that are allowed integrate jupyter as a frame>
    EOF
    ```
   Note that the `openssl rand` commands will generate some secrets such as service tokens and passwords.
3. If you want to use the single user image provided by this project, build the image using
   ```
   docker build -t integrable-jupyterhub-notebook:main notebook/
   ```
   and change the `DOCKER_NOTEBOOK_IMAGE` variable to `integrable-jupyterhub-notebook:main` within the `.env` file.  Note that you might also use another single user server images which deviate from these two options.
4. Build and start all services:
   ```
   docker compose up --build
   ```

## Development

### Debugging

To enable debug logging for all Jupyterhub related services, add the following lines to `jupyterhub/jupyterhub_config.py`:
```
c.ConfigurableHTTPProxy.debug = True
c.ConfigurableHTTPProxy.log_level = 'DEBUG'
c.JupyterHub.log_level = 'DEBUG'
c.Spawner.debug = True
c.DockerSpawner.debug = True
c.Application.log_level = 'DEBUG'
```

### Attaching to the Jupyterhub network

If you are using other docker compose services which integrate this Jupyterhub in another network, you might attach them to the jupyterhub docker network defined in this project.
In this case, define the network used by integrating services as external (see below). Then you will be able to resolve names and contact Jupyter services like `jupyterhub_proxy`.

```
networks:
    another_network:
        name: jupyterhub_network
        # allows using an existing network stack not defined by this docker-compose file.
        external: true
```

### SSL certificate validation

SSL is enabled at the public facing interface of the Jupyterhub proxy.
On each docker build a new private key and certificate is generated at the configurable HTTP proxy.
Since the certificate is self-signed, Jupyterhub's requests to the proxy will fail by default.
To circumvent this for development reasons, the generated SSL certificate from the configurable-http-proxy image is copied to the Jupyterhub image.

Alternatively, you can use the original configurable-http-proxy image , which by default does not use SSL.
To this end, specify `image: jupyterhub/configurable-http-proxy` instead of `build: configurable-http-proxy` and change
the protocol of `c.ConfigurableHTTPProxy.api_url` from `https` to `http` within `jupyterhub/jupyterhub_config.py`.
If you are using ProxyPass rules to the jupyterhub, you will also need to update the protocol of the target to `http`/`ws`. 

## Integrated usage

This configuration enables the Jupyterhub to be used in an integrated manner, e.g., embedded via iframe, while other backend services are communicating with the Jupyterhub REST API and single user server endpoints.
Being embedded, Jupyter frontend needs to send requests to Jupyterhub URLs which might not match with the origin resulting in conflicts with the CORS policies.
As a solution, the webserver that embeds Jupyter must be configured with ProxyPass rules, which route requests to correct Jupyterhub URL.

The following reference configuration of an Apache webserver contains reverse proxy rules, which affect HTTPS as well as secure websocket connections (WSS).

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

All requests sent to `/jupyter` will be rerouted to `jupyterhub_proxy:8000/jupyter`.


## Single User Server

The single user server image configured by Integrable Jupyterhub ships with the following kernels:

| Language | Lang. version            | Jupyter kernel            | Reference                                                                                                           |
|----------|--------------------------|---------------------------|---------------------------------------------------------------------------------------------------------------------|
| Python   | 3                        | `ipykernel`               | [Repository](https://github.com/ipython/ipykernel) / [Homepage](https://ipython.org)                                |
| BASH     | GNU bash, version 5.1.16 | `bash_kernel`             | [Repository](https://github.com/takluyver/bash_kernel)                                                              |
| C        | C11                      | `jupyter-c-kernel`        | [Repository](https://github.com/brendan-rius/jupyter-c-kernel)                                                      |
| C++      | 17                       | `xeus-cling` / `xcpp17`   | [Repository](https://github.com/jupyter-xeus/xeus-cling) / [Homepage](https://xeus-cling.readthedocs.io/en/latest/) |
| Java     | OpenJDK 18               | `ijava`                   | [Repository](https://github.com/SpencerPark/IJava)                                                                  |
| Octave   | GNU Octave 6.4.0         | `octave_kernel`           | [Repository](https://github.com/Calysto/octave_kernel)                                                              |
| R        | 4.1.2                    | `IRkernel`                | [Repository](https://github.com/IRkernel/IRkernel) / [Homepage](https://irkernel.github.io)                         |


## Resources
- https://jupyterhub.readthedocs.io/en/stable/howto/separate-proxy.html
- https://github.com/jupyterhub/configurable-http-proxy