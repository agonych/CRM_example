"""
Permission definition for Clients module.
"""

MODULE_NAME = 'clients'

# Permission types: self (clients assigned to user), group (clients in user's groups), all (all clients)
PERMISSION_TYPES = ['self', 'group', 'all']

# Permission levels
PERMISSION_LEVELS = ['read', 'create', 'edit', 'manage', 'admin']
