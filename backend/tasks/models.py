from django.db import models
from django.utils import timezone
from users.models import User
from clients.models import Client


class TaskType(models.Model):
    """Task type model for categorizing tasks."""
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_task_types'
    )

    class Meta:
        db_table = 'task_types'
        verbose_name = 'Task Type'
        verbose_name_plural = 'Task Types'
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task model for tracking work on clients."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.PROTECT,
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    due_date = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    monetary_value = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    last_access = models.DateTimeField(null=True, blank=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_tasks'
    )

    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def update_last_access(self):
        """Update last access timestamp."""
        self.last_access = timezone.now()
        self.save(update_fields=['last_access'])
