# Integrable Jupyterhub

This reference configuration provides a cloud-based Jupyterhub deployment for integrated usage, e.g., embedded within other applications.
It supports only short-lived sessions which are managed by the DockerSpawner.
A login is only possible by acquiring an authentication token via Jupyterhub API and passing the token either via URL or cookie in future requests.
Jupyterhub is also configured to run within the same Docker network the spawned session containers (single user servers) will also run on.
Thus, sufficient number of unbound local IP addresses should be reserved within your Docker network.

This project configuration sets up the following services:

| Service                 | Docker hostname    | External port    |
|-------------------------|--------------------|------------------|
| JupyterHub              | `jupyterhub_hub`   | 8081             |
| Configurable HTTP proxy | `jupyterhub_proxy` | 8000, 8001 (API) |
| PostgreSQL              | `jupyterhub_db`    | 5432             |


**WARNING**: All jupyterhub sessions/users are short-lived and will be culled upon expiration which also results in deleting all data created during a session.
Thus, the integrator might want to save all data by requesting it from the REST API server and moving the data to some external resource storage.


## Build and Run using docker-compose

1. Clone the integrable Jupyterhub and enter the base directory of the project.
2. Generate an `.env` file containing definitions of environment variables which are passed to the services we want to build.
    ```
    cat << EOF > .env
    POSTGRES_DB=jupyterhub
    POSTGRES_USER=jupyterhub
    POSTGRES_PASSWORD=$(openssl rand -hex 32)
    CONFIGPROXY_AUTH_TOKEN=$(openssl rand -hex 32)
    DOCKER_NETWORK_NAME=jupyterhub_network
    JPY_SERVICE_ADMINS=service-admin:$(openssl rand -hex 64)
    JPY_COOKIE_SECRET=$(openssl rand -hex 64)
    DOCKER_NOTEBOOK_IMAGE=integrable-jupyterhub-notebook:latest
    ACCESS_CONTROL_ORIGINS=
    SSL_DIR_PATH=./configurable-http-proxy/ssl
    EOF
    ```
   Note that the `openssl rand` commands will generate secrets such as service tokens and passwords.
   The following table describes some special fields from above:
   | Field                    | Description                                                                                               | Example                                     |
   |--------------------------|-----------------------------------------------------------------------------------------------------------|---------------------------------------------|
   | `CONFIGPROXY_AUTH_TOKEN` | Token used by jupyterhub to authenticate against the proxy server                                         |                                             |
   | `JPY_SERVICE_ADMINS`     | Admin service names and tokens, e.g. used in API calls or plugins _(separated list of tuples)_            | `admserv1:token1;admserv2:token2`           |
   | `DOCKER_NOTEBOOK_IMAGE`  | Default jupyter notebook image to be spawned in each session                                              |                                             |
   | `ACCESS_CONTROL_ORIGINS` | Origins that are allowed to integrate/embed the jupyterhub, e.g. via iframe _(separated list of strings)_ | `https://127.1.2.7/;https://example.domain` |

3. If you want to use the single user image provided by this project, build the image with
   ```
   docker build -t integrable-jupyterhub-notebook:latest notebook/
   ```
   and change the `DOCKER_NOTEBOOK_IMAGE` variable to `integrable-jupyterhub-notebook:latest` within the `.env` file.
   Note that you might also build your own user server images upon the proposed one, e.g. to install another kernels.

4. In case of __development__, generate self-signed SSL key pairs within `configurable-http-proxy/ssl` with: 
   ```
   openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
       -keyout configurable-http-proxy/ssl/jupyterhub_proxy.key \
       -out    configurable-http-proxy/ssl/jupyterhub_proxy.crt \
       -addext "subjectAltName=DNS:jupyterhub_proxy,IP:127.0.0.1" \
       -subj   "/CN=jupyterhub_proxy"
   ```
   In case of __production__, update the `SSL_DIR_PATH` (see `.env`) environment variable to the directory containing SSL related files and provide `SSL_KEY_FILE`,
   `SSL_CRT_FILE` and `SSL_CA_FILE` filename arguments to the build section of the `jupyterhub_proxy` service within `docker-compose.yml`.  
   Example:
   ```
   jupyterhub_proxy:
       build:
           context: configurable-http-proxy
           args:
               - SSL_KEY_FILE=jupyterhub.key
               - SSL_CRT_FILE=jupyterhub.crt
               - SSL_CA_FILE=jupyterhub_ca.crt
   ```
   
5. Build and start all services:
   ```
   docker compose up --build
   ```
   In production, you might start jupyterhub services via `docker compose up --detach` and spectate all service logs using `docker compose logs --follow`.

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

## Integrated usage

This configuration enables Jupyterhub to be used in an integrated manner, e.g., embedded via iframe, while other backend services are communicating with the Jupyterhub REST API and single user server endpoints.
Being embedded, Jupyter frontend needs to send requests to Jupyterhub URLs which might not match with the origin resulting in conflicts with the CORS policies.

Thus, the recommended way is to set `ACCESS_CONTROL_ORIGINS` to the origins which are allowed to embed Jupyter (see above).
As another solution, the webserver that embeds Jupyter must be configured with ProxyPass rules, which route requests to correct Jupyterhub URL.
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

## Firewall config (iptables)

In case that single user servers, i.e. jupyter users, should be isolated from the outbound network access, the firewall running on the same system as the Jupyterhub can be configured as follows.
Firstly, we need to assign a static IP address to each docker compose service.
Therefore, specify a subnet used by all docker containers created/spawned by this project within `docker-compose.yml`. E.g.,
```
# ...
networks:
    jupyterhub_network:
        name: jupyterhub_network
        ipam:
            config:
                - subnet: 172.27.0.0/16
```

Subsequently, assign an IP address from this subnet to each docker compose service by adding the `ipv4_address` value to the `jupyterhub_network` section of the respective service. E.g.,
```
networks:
    jupyterhub_network:
        ipv4_address: 172.27.0.2
```
Assuming that the static IP address `172.27.0.2` should be assigned to  `jupyterhub_hub`, `172.27.0.3` to `jupyterhub_db` and `172.27.0.4` to `jupyterhub_proxy`, configure your iptables chain `DOCKER-USER` as follows:
```
# Exceptions for Jupyterhub, Postgres and Proxy containers
iptables -A DOCKER-USER -s 172.27.0.2,172.27.0.3,172.27.0.4 -j ACCEPT

# Exceptions for user containers to connect to Jupyterhub and Proxy only!
iptables -A DOCKER-USER -s 172.27.0.0/16 -d 172.27.0.2,172.27.0.4 -j ACCEPT

# Reject all packets coming from the docker network/subnet
iptables -A DOCKER-USER -s 172.27.0.0/16 -j REJECT
```

## URL binding for production

Make sure to update the `c.JupyterHub.bind_url` property within `jupyterhub/jupyter_config.py` to the public facing URL of the proxy (i.e. the whole Jupyter application). E.g.,
```
# Binding
c.JupyterHub.hub_ip = ''
c.JupyterHub.base_url = ''
c.JupyterHub.bind_url = 'https://my.jupyterhub.tld:8000'
```


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