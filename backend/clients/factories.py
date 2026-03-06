import factory
import random
from django.utils import timezone
from faker import Faker
from .models import Client, ClientStatus
from groups.models import Group
from users.models import User

fake = Faker()

CLIENT_STATUS_NAMES = [
    'Active',
    'Inactive',
    'On Hold',
    'VIP',
    'Churned',
]


class ClientStatusFactory(factory.django.DjangoModelFactory):
    """Factory for ClientStatus model."""

    class Meta:
        model = ClientStatus
        django_get_or_create = ('name',)

    name = factory.Iterator(CLIENT_STATUS_NAMES)
    is_active = True


class ClientFactory(factory.django.DjangoModelFactory):
    """Factory for Client model."""

    class Meta:
        model = Client

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.LazyAttribute(lambda obj: fake.phone_number()[:20])
    email = factory.Faker('email')
    address = factory.Faker('address')
    created_at = factory.LazyFunction(timezone.now)

    @factory.lazy_attribute
    def status(self):
        """Randomly assign a status (70% chance) or leave as Prospect/null (30%)."""
        all_statuses = ClientStatus.objects.filter(is_active=True)
        if all_statuses.exists() and random.random() < 0.7:
            return random.choice(list(all_statuses))
        return None
    
    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        """Add groups to the client if provided."""
        if not create:
            return
        
        if extracted:
            # If a list of groups is provided, add them
            for group in extracted:
                self.groups.add(group)
        else:
            # Otherwise, randomly add 1-3 groups if any exist
            all_groups = list(Group.objects.all())
            if all_groups:
                num_groups = random.randint(1, min(3, len(all_groups)))
                selected_groups = random.sample(all_groups, num_groups)
                for group in selected_groups:
                    self.groups.add(group)
    
    @factory.post_generation
    def assigned_users(self, create, extracted, **kwargs):
        """Add assigned users to the client if provided."""
        if not create:
            return
        
        if extracted:
            # If a list of users is provided, add them
            for user in extracted:
                self.assigned_users.add(user)
        else:
            # Otherwise, randomly add 0-2 users if any exist
            all_users = list(User.objects.all())
            if all_users:
                num_users = random.randint(0, min(2, len(all_users)))
                selected_users = random.sample(all_users, num_users)
                for user in selected_users:
                    self.assigned_users.add(user)
