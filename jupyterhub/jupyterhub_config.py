import os
from jupyterhub.auth import Authenticator

c = get_config()


# ======================================================================================================================
# General config
#

# Binding
c.JupyterHub.hub_ip = ''
c.JupyterHub.base_url = '/jupyter'  # proxy route entry to jupyterhub

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# Proxy
c.ConfigurableHTTPProxy.api_url = 'https://jupyterhub_proxy:8001'
c.ConfigurableHTTPProxy.auth_token = os.environ.get('CONFIGPROXY_AUTH_TOKEN')
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.debug = True
c.ConfigurableHTTPProxy.log_level = 'DEBUG'

# Cleanups
c.JupyterHub.cleanup_servers = True

# Debugging
c.Application.log_level = 'DEBUG'
c.JupyterHub.log_level = 'DEBUG'


# ======================================================================================================================
# Database
#

c.JupyterHub.db_url = 'mysql+mysqlconnector://root:{}@jupyterhub_db:3306/{}'.format(
    os.environ['MYSQL_ROOT_PASSWORD'],
    os.environ['MYSQL_DATABASE']
)


# ======================================================================================================================
# Spawner config
#

c.DockerSpawner.image = os.environ.get('DOCKER_NOTEBOOK_IMAGE', c.DockerSpawner.image)
c.DockerSpawner.network_name = os.environ.get('DOCKER_NETWORK_NAME', c.DockerSpawner.network_name)

notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR', '/home/jovyan/work')
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {'jupyterhub-user-{username}': notebook_dir}

# Remove containers once they are stopped
c.DockerSpawner.remove = False

# Debugging. Single-user server debug logging.
c.DockerSpawner.debug = True
c.Spawner.debug = True

c.Spawner.default_url = '/lab'
c.Spawner.mem_limit = '4G'


# ======================================================================================================================
# Authenticator
#

class RejectAuthenticator(Authenticator):
    async def authenticate(self, handler, data):
        return data['username']  # TODO Disable non-token based authentication.


c.JupyterHub.authenticator_class = RejectAuthenticator


# ======================================================================================================================
# Services and roles
#

c.JupyterHub.services = [{'name': 'service-admin', 'admin': True}]

# Define additional tokens for existing services.
c.JupyterHub.service_tokens = {'secret-token': 'service-admin'}

c.JupyterHub.load_roles = [
    {
        'name': 'service-role',
        'scopes': [
            'access:servers',
            'admin:users',
            'admin:servers',
            'delete:users',
            'delete:servers',
            'servers',
            'tokens'
        ],
        'services': [
            'service-admin',
        ]
    }
]