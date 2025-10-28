from django.core.management.base import BaseCommand
from users.models import Badge


class Command(BaseCommand):
    help = 'Create initial badges for gamification'
    
    def handle(self, *args, **options):
        badges_data = [
            {
                'name': 'First Contribution',
                'badge_type': 'first_contribution',
                'description': 'Uploaded your first audio clip',
                'points_reward': 10
            },
            {
                'name': '7 Day Streak',
                'badge_type': 'streak_7',
                'description': 'Contributed for 7 consecutive days',
                'points_reward': 50
            },
            {
                'name': '30 Day Streak',
                'badge_type': 'streak_30',
                'description': 'Contributed for 30 consecutive days',
                'points_reward': 200
            },
            {
                'name': '100 Contributions',
                'badge_type': 'contributor_100',
                'description': 'Uploaded 100 audio clips',
                'points_reward': 100
            },
            {
                'name': '100 Validations',
                'badge_type': 'validator_100',
                'description': 'Validated 100 audio clips',
                'points_reward': 100
            },
            {
                'name': '$10 Earned',
                'badge_type': 'earnings_10',
                'description': 'Earned $10 in USDC rewards',
                'points_reward': 25
            },
            {
                'name': '$100 Earned',
                'badge_type': 'earnings_100',
                'description': 'Earned $100 in USDC rewards',
                'points_reward': 250
            },
            {
                'name': 'Quality Expert',
                'badge_type': 'quality_expert',
                'description': 'Consistently high-quality contributions',
                'points_reward': 150
            },
            {
                'name': 'Early Adopter',
                'badge_type': 'early_adopter',
                'description': 'One of the first 100 users',
                'points_reward': 50
            },
        ]
        
        created_count = 0
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                badge_type=badge_data['badge_type'],
                defaults=badge_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created badge: {badge.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Badge already exists: {badge.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal badges created: {created_count}')
        )
