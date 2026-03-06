import random
import factory
from django.utils import timezone
from datetime import timedelta
from faker import Faker
from .models import Task, TaskType
from clients.models import Client
from users.models import User

fake = Faker()

TASK_TYPE_NAMES = [
    'Phone Call',
    'Email',
    'Meeting',
    'Follow-up',
    'Proposal',
    'Invoice',
    'Support',
    'Consultation',
    'Review',
    'Onboarding',
]


class TaskTypeFactory(factory.django.DjangoModelFactory):
    """Factory for TaskType model."""

    class Meta:
        model = TaskType
        django_get_or_create = ('name',)

    name = factory.Iterator(TASK_TYPE_NAMES)
    is_active = True
    created_at = factory.LazyFunction(timezone.now)


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory for Task model."""

    class Meta:
        model = Task

    name = factory.LazyAttribute(lambda obj: fake.sentence(nb_words=4).rstrip('.'))
    description = factory.Faker('paragraph', nb_sentences=2)
    client = factory.LazyFunction(lambda: random.choice(list(Client.objects.all())))
    task_type = factory.LazyFunction(lambda: random.choice(list(TaskType.objects.all())))
    assigned_to = factory.LazyFunction(
        lambda: random.choice(list(User.objects.filter(is_active=True)))
    )
    due_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=random.randint(-30, 60))
    )
    duration = factory.LazyFunction(lambda: random.choice([15, 30, 45, 60, 90, 120]))
    monetary_value = factory.LazyFunction(
        lambda: round(random.uniform(0, 5000), 2) if random.random() > 0.3 else 0.0
    )
    status = factory.LazyFunction(
        lambda: random.choices(['active', 'completed', 'cancelled'], weights=[60, 30, 10])[0]
    )
    created_at = factory.LazyFunction(timezone.now)
    created_by = factory.LazyAttribute(lambda obj: obj.assigned_to)
