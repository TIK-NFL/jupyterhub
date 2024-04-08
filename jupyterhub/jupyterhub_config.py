import os
import sys
from jupyterhub.auth import Authenticator

c = get_config()

# ======================================================================================================================
# General config
#

# Binding
c.JupyterHub.hub_ip = ''
# proxy route entry to jupyterhub
c.JupyterHub.base_url = '/jupyter'
#c.JupyterHub.bind_url = 'https://jupyterhub_proxy:8000/jupyter'

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# Proxy
c.ConfigurableHTTPProxy.api_url = 'http://jupyterhub_proxy:8001'
c.ConfigurableHTTPProxy.auth_token = os.environ.get('CONFIGPROXY_AUTH_TOKEN')
c.ConfigurableHTTPProxy.should_start = False
# c.ConfigurableHTTPProxy.debug = True
# c.ConfigurableHTTPProxy.log_level = 'DEBUG'

# Cleanups
# do not stop/remove any running servers when jupyterhub shuts down or restarts
c.JupyterHub.cleanup_servers = False

# Debugging
# c.Application.log_level = 'DEBUG'
# c.JupyterHub.log_level = 'DEBUG'


# ======================================================================================================================
# Database
#

c.JupyterHub.db_url = 'postgresql://{}:{}@jupyterhub_db:5432/{}'.format(
    os.environ['POSTGRES_USER'],
    os.environ['POSTGRES_PASSWORD'],
    os.environ['POSTGRES_DB']
)

# ======================================================================================================================
# Spawner config
#

c.DockerSpawner.image = os.environ.get('DOCKER_NOTEBOOK_IMAGE', c.DockerSpawner.image)
c.DockerSpawner.network_name = os.environ.get('DOCKER_NETWORK_NAME', c.DockerSpawner.network_name)

notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR', '/home/jovyan/work')
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {'jupyterhub-user-{username}': notebook_dir}

c.DockerSpawner.name_template = 'jupyter_{raw_username}'

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# Debugging. Single-user server debug logging.
# c.DockerSpawner.debug = True
# c.Spawner.debug = True

c.Spawner.default_url = '/lab'  # '/notebooks' for classic view or '/lab' for JupyterLab view
c.Spawner.mem_limit = '4G'

# ======================================================================================================================
# Access control origins
#

access_control_origins = ''
for origin in os.environ.get('ACCESS_CONTROL_ORIGINS').split(';'):
    access_control_origins += origin + ' '

c.JupyterHub.tornado_settings = {
    'headers': {
        'Access-Control-Allow-Origin': access_control_origins,
    },
    'cookie_options': {
        'SameSite': 'None',
        'Secure': True,
        'Partitioned': True
    },
}

serverapp_tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' " + access_control_origins
    },
    'xsrf_cookie_kwargs': {
        'Partitioned': True
    }
}

c.Spawner.args = ["--ServerApp.tornado_settings={}".format(str(serverapp_tornado_settings))]

# ======================================================================================================================
# Authenticator
#

c.Authenticator.admin_users = {'admin'}

class RejectAuthenticator(Authenticator):
    async def authenticate(self, handler, data):
        # Disable non-token based authentication.
        return None


c.JupyterHub.authenticator_class = RejectAuthenticator

# ======================================================================================================================
# Services and roles
#

c.JupyterHub.services = [
    {
        'name': 'service-admin'
    },
    {
        "name": "jupyterhub-idle-culler-service",
        "command": [
            sys.executable, "-m", "jupyterhub_idle_culler", "--timeout=360", "--cull-users"
        ]
    }
]

# Get service admin users and tokens from env variable.
service_admins_env = os.environ.get('JPY_SERVICE_ADMINS')
service_admins = [(sa.split(':')[0], sa.split(':')[1]) for sa in service_admins_env.split(';')]

# Define additional tokens for existing services.
c.JupyterHub.service_tokens = {}

for service_admin in service_admins:
    c.JupyterHub.service_tokens[service_admin[1]] = service_admin[0]

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
        'services': [service_admin[0] for service_admin in service_admins]
    },
    {
        "name": "jupyterhub-idle-culler-role",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:servers",
            "delete:servers",
            "delete:users"
        ],
        # assignment of role's permissions to:
        "services": [
            "jupyterhub-idle-culler-service"
        ]
    }
]