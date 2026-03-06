"""
Permission definition for Tasks module.
"""

MODULE_NAME = 'tasks'

# Permission types: self (tasks assigned to user), group (tasks for clients in user's groups), all (all tasks)
PERMISSION_TYPES = ['self', 'group', 'all']

# Permission levels
PERMISSION_LEVELS = ['read', 'create', 'edit', 'manage', 'admin']
