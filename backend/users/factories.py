import factory
from django.utils import timezone
from .models import User

_user_counter = 0


def _make_unique_email(obj):
    global _user_counter
    _user_counter += 1
    base = f"{obj.first_name.lower()}.{obj.last_name.lower()}"
    email = f"{base}@crmdemo.com.au"
    if User.objects.filter(email=email).exists():
        email = f"{base}{_user_counter}@crmdemo.com.au"
    return email


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User
        django_get_or_create = ('email',)

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(_make_unique_email)
    is_active = True
    created_at = factory.LazyFunction(timezone.now)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'Test123')
        manager = cls._get_manager(model_class)
        email = kwargs.get('email', '')
        try:
            existing = model_class.objects.get(email=email)
            return existing
        except model_class.DoesNotExist:
            user = manager.create(*args, **kwargs)
            user.set_password(password)
            user.save()
            return user
