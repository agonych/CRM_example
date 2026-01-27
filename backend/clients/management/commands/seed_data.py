"""
Management command to seed the database with sample data.
Creates 3 groups and 100 clients (leads).
"""
from django.core.management.base import BaseCommand
from groups.factories import GroupFactory
from clients.factories import ClientFactory


class Command(BaseCommand):
    help = 'Seed the database with 3 groups and 100 clients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--groups',
            type=int,
            default=3,
            help='Number of groups to create (default: 3)',
        )
        parser.add_argument(
            '--clients',
            type=int,
            default=100,
            help='Number of clients to create (default: 100)',
        )

    def handle(self, *args, **options):
        num_groups = options['groups']
        num_clients = options['clients']
        
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Create groups
        self.stdout.write(f'Creating {num_groups} groups...')
        groups = []
        for i in range(num_groups):
            group = GroupFactory()
            groups.append(group)
            self.stdout.write(f'  [+] Created group: {group.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(groups)} groups'))
        
        # Create clients
        self.stdout.write(f'Creating {num_clients} clients...')
        created = 0
        for i in range(num_clients):
            # Randomly assign some clients to groups
            import random
            if groups and random.random() < 0.7:  # 70% chance to assign to a group
                selected_groups = random.sample(groups, random.randint(1, min(2, len(groups))))
                client = ClientFactory(groups=selected_groups)
            else:
                client = ClientFactory()
            
            created += 1
            if created % 10 == 0:
                self.stdout.write(f'  Created {created}/{num_clients} clients...')
        
        self.stdout.write(self.style.SUCCESS(f'Created {created} clients'))
        self.stdout.write(self.style.SUCCESS('\nDatabase seeding complete!'))
