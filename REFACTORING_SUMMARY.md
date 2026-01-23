# Permission System Refactoring - Summary

## ✅ Completed

### Backend Changes

1. **Created Permissions Module** (`permissions/`)
   - `base.py` - Permission registry that loads permissions from module `permissions.py` files
   - `checker.py` - PermissionChecker class with highest-level-wins logic
   - `views.py` - API endpoint to get available permissions
   - `urls.py` - URL routing for permissions API

2. **Created Groups Module** (`groups/`)
   - Moved Group model from `users` app
   - Created serializers, views, admin, URLs
   - Added `permissions.py` with module definition

3. **Created Roles Module** (`roles/`)
   - Moved Role model from `users` app
   - Created `RolePermission` model for multiple permission rows
   - Created serializers, views, admin, URLs
   - Added `permissions.py` with module definition

4. **Updated Clients Module**
   - Added `permissions.py` with module definition
   - Updated views to use `PermissionChecker`
   - Simplified permission checking logic

5. **Updated Users Module**
   - Removed Group and Role models
   - Added `permissions.py` with module definition
   - Updated imports

### Frontend Changes

1. **Created Permission Hook** (`hooks/usePermissions.js`)
   - Fetches user roles and calculates permissions
   - Provides `hasPermission(module, level)` function

2. **Updated Layout Component**
   - Checks read permissions for menu items
   - Hides menu items user can't access

3. **Updated All Pages**
   - Clients, Users, Groups, Roles pages check permissions
   - Hide create/edit/delete buttons based on permissions

4. **Rewrote RoleModal**
   - Supports multiple permission rows per module
   - Fetches available permissions from API
   - Add/remove permission rows dynamically

## 🔄 Migration Required

This refactoring requires database migrations:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

**Important**: The old JSON permissions field in Role model will be replaced with RolePermission rows. You may need to write a data migration to convert existing permissions.

## 📝 Module Permission Definition

Each module now defines permissions in `permissions.py`:

```python
MODULE_NAME = 'module_name'
PERMISSION_TYPES = ['self', 'group', 'all']  # Ownership types
PERMISSION_LEVELS = ['read', 'create', 'edit', 'manage', 'admin']  # Permission levels
```

## 🎯 Permission System Features

1. **Multiple Permission Rows**: A role can have multiple permission rows for the same module (e.g., "self admin" and "group read")

2. **Highest Level Wins**: When checking permissions, the highest level across all applicable rows is used

3. **Ownership Types**:
   - `self` - Objects assigned to the user
   - `group` - Objects in user's groups
   - `all` - All objects in the module

4. **Permission Levels**: read < create < edit < manage < admin

5. **Dynamic Module Loading**: Permissions are loaded automatically from module `permissions.py` files

## 🔗 API Endpoints

- `GET /api/permissions/available/` - Get all available module permissions
- `GET /api/groups/` - List groups (replaces `/api/auth/groups/`)
- `GET /api/roles/` - List roles (replaces `/api/auth/roles/`)
- `GET /api/roles/permissions/` - List role permissions
- `POST /api/roles/permissions/` - Create role permission
- `PATCH /api/roles/permissions/{id}/` - Update role permission
- `DELETE /api/roles/permissions/{id}/` - Delete role permission

## ⚠️ Breaking Changes

1. **API Endpoints Changed**:
   - `/api/auth/groups/` → `/api/groups/`
   - `/api/auth/roles/` → `/api/roles/`

2. **Permission Structure Changed**:
   - Old: JSON field in Role model
   - New: RolePermission model with multiple rows

3. **Imports Changed**:
   - `from users.models import Group, Role` → `from groups.models import Group` and `from roles.models import Role`
