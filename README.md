# Jupyterhub-Cloud

## Build and Deployment

## Integration

## Configuration

### Configurable-http-proxy (default arguments)
```
--ip=127.0.0.1 --port=8080 --api-ip=127.0.0.1 --api-port=8001 --default-target=http://jupyterhub_hub:8081 --error-target=http://jupyterhub_hub:8081/hub/error
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