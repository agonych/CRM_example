"""
Management command to create an Admin role with admin permissions for all modules.
Usage: python manage.py create_admin_role
"""

from django.core.management.base import BaseCommand
from roles.models import Role, RolePermission
from permissions.base import get_permission_registry


class Command(BaseCommand):
    help = 'Create an Admin role with admin permissions for all modules'

    def handle(self, *args, **options):
        # Get permission registry
        registry = get_permission_registry()
        all_permissions = registry.get_all()
        
        if not all_permissions:
            self.stdout.write(
                self.style.WARNING('No modules with permissions found. Make sure modules have permissions.py files.')
            )
            return
        
        # Create or get Admin role
        role, created = Role.objects.get_or_create(
            name='Admin',
            defaults={
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created role: {role.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Role "{role.name}" already exists. Updating permissions...'))
            # Delete existing permissions for this role
            RolePermission.objects.filter(role=role).delete()
        
        # Create admin permissions for all modules
        permissions_created = 0
        for module_name, perm_def in all_permissions.items():
            # Check if 'all' ownership type is available
            if 'all' in perm_def.types:
                ownership_type = 'all'
            elif perm_def.types:
                # Use the first available ownership type if 'all' is not available
                ownership_type = perm_def.types[0]
                self.stdout.write(
                    self.style.WARNING(
                        f'Module "{module_name}" does not support "all" ownership type. '
                        f'Using "{ownership_type}" instead.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Module "{module_name}" has no ownership types defined. Skipping.')
                )
                continue
            
            # Check if 'admin' level is available
            if 'admin' in perm_def.levels:
                level = 'admin'
            elif perm_def.levels:
                # Use the highest available level
                level = perm_def.levels[-1]
                self.stdout.write(
                    self.style.WARNING(
                        f'Module "{module_name}" does not support "admin" level. '
                        f'Using "{level}" instead.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Module "{module_name}" has no permission levels defined. Skipping.')
                )
                continue
            
            # Create permission
            permission, perm_created = RolePermission.objects.get_or_create(
                role=role,
                module_name=module_name,
                ownership_type=ownership_type,
                level=level,
                defaults={'is_active': True}
            )
            
            if perm_created:
                permissions_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [+] Created permission: {module_name} - {ownership_type} {level}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  [-] Permission already exists: {module_name} - {ownership_type} {level}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[SUCCESS] Admin role setup complete! Created {permissions_created} permission(s) for {len(all_permissions)} module(s).'
            )
        )
