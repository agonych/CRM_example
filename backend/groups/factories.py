import factory
from django.utils import timezone
from .models import Group
from users.models import User


class GroupFactory(factory.django.DjangoModelFactory):
    """Factory for Group model."""
    
    class Meta:
        model = Group
    
    name = factory.Sequence(lambda n: f"Group {n}")
    is_active = True
    created_at = factory.LazyFunction(timezone.now)
    
    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        """Add users to the group if provided."""
        if not create:
            return
        
        if extracted:
            # If a list of users is provided, add them
            for user in extracted:
                self.users.add(user)
        else:
            # Otherwise, randomly add 0-3 users if any exist
            all_users = User.objects.all()
            if all_users.exists():
                import random
                num_users = random.randint(0, min(3, all_users.count()))
                selected_users = random.sample(list(all_users), num_users)
                for user in selected_users:
                    self.users.add(user)
