# Permission System Refactoring Notes

## Changes Made

### 1. New Modules Created
- **permissions/** - Base permission system with registry and checker
- **groups/** - Groups module (moved from users)
- **roles/** - Roles module (moved from users)

### 2. Permission System
- Each module now defines its permissions in `permissions.py`:
  - `MODULE_NAME` - Module identifier
  - `PERMISSION_TYPES` - Available ownership types (e.g., ['self', 'group', 'all'])
  - `PERMISSION_LEVELS` - Available permission levels (e.g., ['read', 'create', 'edit', 'manage', 'admin'])

### 3. RolePermission Model
- Replaces JSON permissions field
- Supports multiple permission rows per module per role
- Each row has: module_name, ownership_type, level

### 4. Permission Checker
- `PermissionChecker` class for checking permissions
- `get_highest_level()` - Returns highest permission level (highest wins)
- `has_permission()` - Checks if user has required level
- `filter_queryset()` - Filters queryset based on permissions

## Migration Required

This refactoring requires database migrations:
1. Remove Group and Role from users app
2. Create groups and roles apps
3. Create RolePermission model
4. Migrate existing permission data

## Files That Need Updates

### Backend
- [ ] Update all imports (Group, Role from new locations)
- [ ] Update serializers (users, groups, roles)
- [ ] Update views (users, groups, roles, clients)
- [ ] Update admin (users, groups, roles)
- [ ] Update clients/views.py to use PermissionChecker
- [ ] Create migrations

### Frontend
- [ ] Update RoleModal to support multiple permission rows
- [ ] Add permission checking to menu items
- [ ] Update API calls for new permission structure
