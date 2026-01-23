from django.db import models
from users.models import User


class Group(models.Model):
    """Group model for organizing users."""
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='crm_groups', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_groups'
    )
    
    class Meta:
        db_table = 'groups'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
    
    def __str__(self):
        return self.name
