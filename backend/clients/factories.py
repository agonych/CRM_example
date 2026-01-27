import factory
from django.utils import timezone
from faker import Faker
from .models import Client
from groups.models import Group
from users.models import User

fake = Faker()


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
            # Otherwise, randomly add 0-2 groups if any exist
            all_groups = Group.objects.all()
            if all_groups.exists():
                import random
                num_groups = random.randint(0, min(2, all_groups.count()))
                selected_groups = random.sample(list(all_groups), num_groups)
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
            all_users = User.objects.all()
            if all_users.exists():
                import random
                num_users = random.randint(0, min(2, all_users.count()))
                selected_users = random.sample(list(all_users), num_users)
                for user in selected_users:
                    self.assigned_users.add(user)
