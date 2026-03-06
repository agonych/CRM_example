"""
Management command to seed the database with sample data.
Creates users, groups, clients, task types, and tasks.
"""
import random
from django.core.management.base import BaseCommand
from users.factories import UserFactory
from groups.factories import GroupFactory
from clients.factories import ClientFactory, ClientStatusFactory, CLIENT_STATUS_NAMES
from tasks.factories import TaskTypeFactory, TaskFactory, TASK_TYPE_NAMES


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users', type=int, default=10,
            help='Number of users to create (default: 10)',
        )
        parser.add_argument(
            '--groups', type=int, default=3,
            help='Number of groups to create (default: 3)',
        )
        parser.add_argument(
            '--clients', type=int, default=200,
            help='Number of clients to create (default: 200)',
        )
        parser.add_argument(
            '--tasks', type=int, default=200,
            help='Number of tasks to create (default: 200)',
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_groups = options['groups']
        num_clients = options['clients']
        num_tasks = options['tasks']

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create users
        self.stdout.write(f'Creating {num_users} users...')
        users = []
        for i in range(num_users):
            user = UserFactory()
            users.append(user)
            self.stdout.write(f'  [+] Created user: {user.email} (password: Test123)')
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Create groups
        self.stdout.write(f'Creating {num_groups} groups...')
        groups = []
        for i in range(num_groups):
            group = GroupFactory()
            groups.append(group)
            self.stdout.write(f'  [+] Created group: {group.name}')
        self.stdout.write(self.style.SUCCESS(f'Created {len(groups)} groups'))

        # Create client statuses
        self.stdout.write('Creating client statuses...')
        client_statuses = []
        for name in CLIENT_STATUS_NAMES:
            cs = ClientStatusFactory(name=name)
            client_statuses.append(cs)
            self.stdout.write(f'  [+] Created client status: {cs.name}')
        self.stdout.write(self.style.SUCCESS(f'Created {len(client_statuses)} client statuses'))

        # Create clients
        self.stdout.write(f'Creating {num_clients} clients...')
        created = 0
        for i in range(num_clients):
            if groups and random.random() < 0.7:
                selected_groups = random.sample(groups, random.randint(1, min(2, len(groups))))
                client = ClientFactory(groups=selected_groups)
            else:
                client = ClientFactory()
            created += 1
            if created % 50 == 0:
                self.stdout.write(f'  Created {created}/{num_clients} clients...')
        self.stdout.write(self.style.SUCCESS(f'Created {created} clients'))

        # Create task types (always creates the full set of 10)
        self.stdout.write('Creating task types...')
        task_types = []
        for name in TASK_TYPE_NAMES:
            tt = TaskTypeFactory(name=name)
            task_types.append(tt)
            self.stdout.write(f'  [+] Created task type: {tt.name}')
        self.stdout.write(self.style.SUCCESS(f'Created {len(task_types)} task types'))

        # Create tasks
        self.stdout.write(f'Creating {num_tasks} tasks...')
        created = 0
        for i in range(num_tasks):
            task = TaskFactory()
            created += 1
            if created % 50 == 0:
                self.stdout.write(f'  Created {created}/{num_tasks} tasks...')
        self.stdout.write(self.style.SUCCESS(f'Created {created} tasks'))

        self.stdout.write(self.style.SUCCESS('\nDatabase seeding complete!'))
