from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import Chore, Roommate


class Command(BaseCommand):
    help = "Seed the database with a default household of roommates and rotating chores"

    def handle(self, *args, **options):
        roommates_data = [
            {"name": "Alex", "color_code": "#3B82F6", "order_index": 0, "is_active": True},
            {"name": "Sam", "color_code": "#10B981", "order_index": 1, "is_active": True},
            {"name": "Jordan", "color_code": "#F59E0B", "order_index": 2, "is_active": True},
            {"name": "Taylor", "color_code": "#8B5CF6", "order_index": 3, "is_active": True},
        ]

        roommates = {}
        for data in roommates_data:
            obj, _ = Roommate.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
            roommates[obj.name] = obj

        today = date.today()
        chores_data = [
            {
                "title": "Wipe kitchen counters",
                "description": "Wipe and sanitize kitchen countertops and stovetop.",
                "recurrence_type": Chore.RecurrenceType.DAILY,
                "next_due_date": today,
                "current_assignee": roommates["Alex"],
            },
            {
                "title": "Take out bins & recycling",
                "description": "Empty household trash and recycling bins into curb wheelie bins.",
                "recurrence_type": Chore.RecurrenceType.WEEKLY,
                "next_due_date": today + timedelta(days=1),
                "current_assignee": roommates["Sam"],
            },
            {
                "title": "Vacuum & mop common areas",
                "description": "Vacuum the living room rug and mop the hallway and kitchen floor.",
                "recurrence_type": Chore.RecurrenceType.BIWEEKLY,
                "next_due_date": today + timedelta(days=3),
                "current_assignee": roommates["Jordan"],
            },
            {
                "title": "Deep clean bathroom",
                "description": "Scrub shower, sink, clean mirror, and disinfect toilet.",
                "recurrence_type": Chore.RecurrenceType.MONTHLY,
                "next_due_date": today + timedelta(days=7),
                "current_assignee": roommates["Taylor"],
            },
        ]

        for data in chores_data:
            Chore.objects.update_or_create(
                title=data["title"],
                defaults=data,
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded default household data."))
