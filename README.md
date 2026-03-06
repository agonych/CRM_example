# CRM System

A modular CRM system built with Django (backend) and React with Tailwind CSS (frontend).

## Features

- **User Management**: Custom user model with groups and roles, search, filters, and active/inactive tabs
- **Flexible Permission System**: Module-based permissions with multiple permission rows per role
- **Client Management**: Full CRUD with status tracking, group assignment, user assignment, and batch operations
- **Task Management**: Task tracking with types, assignments, due dates, durations, monetary values, and batch operations
- **Client Statuses**: Configurable client statuses with sort ordering
- **Batch Operations**: Select multiple clients or tasks and perform bulk actions (change status, assign groups/users, set type, complete/cancel)
- **Role-Based Access Control**: Granular permissions with ownership types (self/group/all) and access levels
- **Modern UI**: React frontend with Tailwind CSS and responsive design
- **Permission-Aware UI**: Menu items and actions hidden based on user permissions

## Project Structure

```
CRM_Example/
├── backend/          # Django backend
│   ├── crm_project/  # Main Django project
│   ├── users/        # Users app
│   ├── groups/       # Groups app
│   ├── roles/        # Roles app
│   ├── clients/      # Clients app
│   ├── tasks/        # Tasks app
│   ├── permissions/  # Permission system
│   └── requirements.txt
└── frontend/         # React frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── contexts/
    │   ├── hooks/
    │   └── services/
    └── package.json
```

## Permission System

The permission system is modular and flexible:

### Module Permission Definition

Each module defines its permissions in a `permissions.py` file:

```python
MODULE_NAME = 'module_name'
PERMISSION_TYPES = ['self', 'group', 'all']  # Ownership types
PERMISSION_LEVELS = ['read', 'create', 'edit', 'manage', 'admin']  # Permission levels
```

### Permission Features

- **Multiple Permission Rows**: A role can have multiple permission rows for the same module
  - Example: "self admin" + "group read" for the same module
- **Highest Level Wins**: When checking permissions, the highest level across all applicable rows is used
- **Ownership Types**:
  - `self` - Objects assigned directly to the user
  - `group` - Objects in user's groups
  - `all` - All objects in the module
- **Permission Levels**: `read` < `create` < `edit` < `manage` < `admin`
- **Dynamic Module Loading**: Permissions are automatically discovered from module `permissions.py` files

## Backend Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. (Optional) Create a `.env` file in the `backend` directory for custom settings:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Note**: The project uses SQLite by default, so no database setup is required!

6. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

8. Create an Admin role with full permissions:
```bash
python manage.py create_admin_role
```

9. Create a superuser:
```bash
python manage.py createsuperuser
```

10. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 16+ and npm

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

**Note**: The frontend uses Vite's proxy to forward `/api/*` requests to `http://localhost:8000`. 

**Troubleshooting Proxy Issues:**
- The browser will show requests as `http://localhost:3000/api/...` - this is normal! Vite proxies them to port 8000 server-side
- Make sure the Django backend is running: `python manage.py runserver` (should be on port 8000)
- Restart the Vite dev server after changing `vite.config.js`: Stop (Ctrl+C) and run `npm run dev` again
- Check the browser Network tab - failed requests will show the error details
- Check the Vite terminal for proxy errors
- Verify CORS is configured in Django settings (should allow `http://localhost:3000`)

**Alternative (if proxy doesn't work):**
Create a `.env` file in the `frontend` directory:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```
This bypasses the proxy and calls the backend directly.

## API Endpoints

### Authentication
- `POST /api/auth/users/login/` - Login
- `POST /api/auth/users/register/` - Register new user
- `GET /api/auth/users/me/` - Get current user
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Users
- `GET /api/auth/users/` - List users
- `POST /api/auth/users/` - Create user
- `GET /api/auth/users/{id}/` - Get user
- `PATCH /api/auth/users/{id}/` - Update user
- `DELETE /api/auth/users/{id}/` - Delete user

### Groups
- `GET /api/groups/` - List groups
- `POST /api/groups/` - Create group
- `GET /api/groups/{id}/` - Get group
- `PATCH /api/groups/{id}/` - Update group
- `DELETE /api/groups/{id}/` - Delete group

### Roles
- `GET /api/roles/` - List roles
- `POST /api/roles/` - Create role
- `GET /api/roles/{id}/` - Get role
- `PATCH /api/roles/{id}/` - Update role
- `DELETE /api/roles/{id}/` - Delete role

### Role Permissions
- `GET /api/roles/permissions/` - List role permissions
- `POST /api/roles/permissions/` - Create role permission
- `GET /api/roles/permissions/{id}/` - Get role permission
- `PATCH /api/roles/permissions/{id}/` - Update role permission
- `DELETE /api/roles/permissions/{id}/` - Delete role permission

### Clients
- `GET /api/clients/` - List clients (filters: `status`, `group`, `assigned_user`)
- `POST /api/clients/` - Create client
- `GET /api/clients/{id}/` - Get client
- `PATCH /api/clients/{id}/` - Update client
- `DELETE /api/clients/{id}/` - Delete client
- `POST /api/clients/batch/` - Batch operations (actions: `change_status`, `add_to_group`, `remove_from_group`, `assign_users`)

### Client Statuses
- `GET /api/clients/statuses/` - List client statuses
- `POST /api/clients/statuses/` - Create client status
- `PATCH /api/clients/statuses/{id}/` - Update client status
- `DELETE /api/clients/statuses/{id}/` - Delete client status (unlinks from clients)

### Tasks
- `GET /api/tasks/` - List tasks (filters: `status`, `task_type`, `group`, `assigned_to`, `client`)
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Get task
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `POST /api/tasks/batch/` - Batch operations (actions: `complete`, `cancel`, `set_type`)

### Task Types
- `GET /api/tasks/types/` - List task types
- `POST /api/tasks/types/` - Create task type
- `PATCH /api/tasks/types/{id}/` - Update task type
- `DELETE /api/tasks/types/{id}/` - Delete task type

### Permissions
- `GET /api/permissions/available/` - Get all available module permissions (for role configuration)

## Permission System Usage

### Backend - Checking Permissions

```python
from permissions.checker import get_permission_checker

# Get permission checker for a user
checker = get_permission_checker(user)

# Check if user has permission
if checker.has_permission('clients', 'edit', client_obj):
    # User can edit this client
    pass

# Get highest permission level
level = checker.get_highest_level('clients', client_obj)

# Filter queryset based on permissions
clients = checker.filter_queryset(Client.objects.all(), 'clients', 'read')
```

### Frontend - Checking Permissions

```javascript
import { usePermissions } from '../hooks/usePermissions'

function MyComponent() {
  const { hasPermission } = usePermissions()
  
  if (!hasPermission('clients', 'read')) {
    return <div>No access</div>
  }
  
  return (
    <div>
      {hasPermission('clients', 'create') && (
        <button>Create Client</button>
      )}
    </div>
  )
}
```

## Management Commands

### Create Admin Role

Create an Admin role with admin permissions for all modules:

```bash
python manage.py create_admin_role
```

This command:
- Creates or updates an "Admin" role
- Automatically discovers all modules with permissions
- Creates admin-level permissions for all objects in each module
- Can be run multiple times to update permissions when new modules are added

### Seed Database

Seed the database with sample data:

```bash
python manage.py seed_data
```

This command:
- Creates 3 groups by default
- Creates 3 client statuses (New Lead, Active, Inactive)
- Creates 3 task types (Call, Meeting, Follow-up)
- Creates 5 users with roles and group assignments
- Creates 100 clients with random group and user assignments
- Creates 200 tasks linked to clients with random types and assignments

You can customize the counts:

```bash
python manage.py seed_data --groups 5 --clients 200 --users 10 --tasks 500
```

### Reset Database

Delete the SQLite database and recreate it (useful for development):

```bash
python reset_database.py
python manage.py migrate
python manage.py create_admin_role
```

Or manually delete `backend/db.sqlite3` and run migrations.

## Adding a New Module

To add a new module with permissions:

1. Create the module app:
```bash
python manage.py startapp mymodule
```

2. Add to `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    # ... other apps
    'mymodule',
]
```

3. Create `mymodule/permissions.py`:
```python
MODULE_NAME = 'mymodule'
PERMISSION_TYPES = ['self', 'group', 'all']  # Adjust as needed
PERMISSION_LEVELS = ['read', 'create', 'edit', 'manage', 'admin']  # Adjust as needed
```

4. The permission system will automatically discover and register your module!

## Development

### Backend Development
- Admin panel: `http://localhost:8000/admin/`
- API root: `http://localhost:8000/api/`

### Frontend Development
- The frontend proxies API requests to `http://localhost:8000/api` via Vite proxy configuration
- Menu items are automatically hidden based on read permissions
- Action buttons (create/edit/delete) are conditionally shown based on permissions

## Notes

- All models include timestamps: `created_at`, `last_access`, `last_edit`, `last_edited_by`
- JWT tokens are used for authentication
- CORS is configured to allow requests from `http://localhost:3000`
- The permission system is extensible - new modules automatically integrate by adding a `permissions.py` file
- Superusers (`is_superuser=True`) bypass all permission checks and have full access
- The permission checker uses "highest level wins" logic when multiple permission rows apply

