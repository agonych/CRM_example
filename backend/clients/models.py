from django.db import models
from django.utils import timezone
from users.models import User, Group


class Client(models.Model):
    """Client model for CRM."""
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # Relationships
    groups = models.ManyToManyField(Group, related_name='clients', blank=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_clients', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_clients'
    )
    
    class Meta:
        db_table = 'clients'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def update_last_access(self):
        """Update last access timestamp."""
        self.last_access = timezone.now()
        self.save(update_fields=['last_access'])
