"""
Permission checking utilities.
"""

from typing import Optional, Any
from django.db.models import QuerySet, Q
from users.models import User


class PermissionChecker:
    """Utility class for checking permissions."""
    
    # Level hierarchy (higher index = higher permission)
    LEVEL_HIERARCHY = ['read', 'create', 'edit', 'manage', 'admin']
    
    def __init__(self, user: User):
        self.user = user
    
    def get_highest_level(self, module_name: str, obj: Optional[Any] = None) -> Optional[str]:
        """
        Get the highest permission level for a module and optionally an object.
        
        Args:
            module_name: Name of the module
            obj: Optional object to check ownership for
        
        Returns:
            Highest permission level or None if no permissions
        """
        if self.user.is_superuser:
            return 'admin'
        
        user_roles = self.user.roles.filter(is_active=True)
        if not user_roles.exists():
            return None
        
        highest_level = None
        highest_level_index = -1
        
        for role in user_roles:
            permissions = role.permissions.filter(module_name=module_name, is_active=True)
            
            for perm in permissions:
                # Determine ownership type for this object
                ownership_type = self._determine_ownership_type(obj, perm.ownership_type)
                
                if ownership_type is None:
                    continue
                
                # Check if this permission applies
                if perm.ownership_type == 'all' or perm.ownership_type == ownership_type:
                    level_index = self._get_level_index(perm.level)
                    if level_index > highest_level_index:
                        highest_level_index = level_index
                        highest_level = perm.level
        
        return highest_level
    
    def has_permission(self, module_name: str, required_level: str, obj: Optional[Any] = None) -> bool:
        """
        Check if user has required permission level.
        
        Args:
            module_name: Name of the module
            required_level: Required permission level
            obj: Optional object to check ownership for
        
        Returns:
            True if user has required permission or higher
        """
        if self.user.is_superuser:
            return True
        
        highest_level = self.get_highest_level(module_name, obj)
        if highest_level is None:
            return False
        
        return self._level_satisfies(highest_level, required_level)
    
    def filter_queryset(self, queryset: QuerySet, module_name: str, required_level: str = 'read') -> QuerySet:
        """
        Filter queryset based on user permissions.
        
        Args:
            queryset: QuerySet to filter
            module_name: Name of the module
            required_level: Minimum required permission level
        
        Returns:
            Filtered QuerySet
        """
        if self.user.is_superuser:
            return queryset
        
        user_roles = self.user.roles.filter(is_active=True)
        if not user_roles.exists():
            return queryset.none()
        
        # Get all applicable permissions
        applicable_perms = []
        for role in user_roles:
            perms = role.permissions.filter(
                module_name=module_name,
                is_active=True
            )
            for perm in perms:
                if self._level_satisfies(perm.level, required_level):
                    applicable_perms.append(perm)
        
        if not applicable_perms:
            return queryset.none()
        
        # Build query based on permissions
        q_objects = Q()
        
        for perm in applicable_perms:
            if perm.ownership_type == 'all':
                # Can access all objects
                return queryset
            elif perm.ownership_type == 'self':
                # Can access objects assigned to user
                if queryset.model.__name__ == 'User':
                    # For User model, self means the user themselves
                    q_objects |= Q(id=self.user.id)
                elif hasattr(queryset.model, 'assigned_users'):
                    q_objects |= Q(assigned_users=self.user)
                elif hasattr(queryset.model, 'assigned_to'):
                    q_objects |= Q(assigned_to=self.user)
                    if hasattr(queryset.model, 'created_by'):
                        q_objects |= Q(created_by=self.user)
                elif hasattr(queryset.model, 'user'):
                    q_objects |= Q(user=self.user)
                elif hasattr(queryset.model, 'created_by'):
                    q_objects |= Q(created_by=self.user)
            elif perm.ownership_type == 'group':
                # Can access objects in user's groups
                user_groups = self.user.crm_groups.all()
                if user_groups.exists():
                    if hasattr(queryset.model, 'groups'):
                        q_objects |= Q(groups__in=user_groups)
                    # For models linked to client with groups (e.g. Task -> Client -> Groups)
                    elif hasattr(queryset.model, 'client') and hasattr(queryset.model.client.field.related_model, 'groups'):
                        q_objects |= Q(client__groups__in=user_groups)
                    # Also include self-assigned
                    if hasattr(queryset.model, 'assigned_users'):
                        q_objects |= Q(assigned_users=self.user)
                    elif hasattr(queryset.model, 'assigned_to'):
                        q_objects |= Q(assigned_to=self.user)
                    # For groups module itself, check if user is in the group
                    if queryset.model.__name__ == 'Group':
                        q_objects |= Q(id__in=user_groups.values_list('id', flat=True))
        
        return queryset.filter(q_objects).distinct()
    
    def _determine_ownership_type(self, obj: Optional[Any], perm_type: str) -> Optional[str]:
        """Determine ownership type for an object."""
        if obj is None:
            return perm_type  # For list views, return the permission type
        
        # Check if object is assigned to user (M2M or FK)
        if hasattr(obj, 'assigned_users') and obj.assigned_users.filter(id=self.user.id).exists():
            return 'self'
        if hasattr(obj, 'assigned_to') and obj.assigned_to_id == self.user.id:
            return 'self'
        
        # Check if object is in user's groups
        if hasattr(obj, 'groups'):
            user_groups = self.user.crm_groups.all()
            if obj.groups.filter(id__in=user_groups.values_list('id', flat=True)).exists():
                return 'group'
        
        # For Group model itself, check if user belongs to the group
        if obj.__class__.__name__ == 'Group':
            if obj.users.filter(id=self.user.id).exists():
                return 'self'
        
        # Check direct user assignment
        if hasattr(obj, 'user') and obj.user == self.user:
            return 'self'
        
        if hasattr(obj, 'created_by') and obj.created_by == self.user:
            return 'self'
        
        # If permission is 'all', it applies regardless
        if perm_type == 'all':
            return 'all'
        
        # Default to None if no match
        return None
    
    def _get_level_index(self, level: str) -> int:
        """Get index of permission level in hierarchy."""
        try:
            return self.LEVEL_HIERARCHY.index(level)
        except ValueError:
            return -1
    
    def _level_satisfies(self, user_level: str, required_level: str) -> bool:
        """Check if user level satisfies required level."""
        user_index = self._get_level_index(user_level)
        required_index = self._get_level_index(required_level)
        
        if user_index == -1 or required_index == -1:
            return False
        
        return user_index >= required_index


def get_permission_checker(user: User) -> PermissionChecker:
    """Get permission checker for a user."""
    return PermissionChecker(user)
