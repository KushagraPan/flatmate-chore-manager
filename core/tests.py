from datetime import date, timedelta
from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from core.models import Chore, ChoreLog, Roommate


class SmokeTest(SimpleTestCase):
    def test_project_setup_and_runner(self):
        """Smoke test verifying that the test runner executes and core is installed."""
        self.assertTrue(True)
        self.assertIn("core", settings.INSTALLED_APPS)


class RoommateModelTests(TestCase):
    def test_roommate_creation_and_defaults(self):
        roommate = Roommate.objects.create(name="Alex")
        self.assertEqual(roommate.name, "Alex")
        self.assertEqual(roommate.color_code, "#3B82F6")
        self.assertEqual(roommate.order_index, 0)
        self.assertTrue(roommate.is_active)

    def test_roommate_str_representation(self):
        roommate = Roommate.objects.create(name="Sam")
        self.assertEqual(str(roommate), "Sam")

    def test_roommate_custom_attributes(self):
        roommate = Roommate.objects.create(
            name="Taylor",
            color_code="#EF4444",
            order_index=3,
            is_active=False,
        )
        self.assertEqual(roommate.name, "Taylor")
        self.assertEqual(roommate.color_code, "#EF4444")
        self.assertEqual(roommate.order_index, 3)
        self.assertFalse(roommate.is_active)


class ChoreModelTests(TestCase):
    def setUp(self):
        self.roommate = Roommate.objects.create(name="Jordan")

    def test_chore_creation_and_defaults(self):
        due = date.today() + timedelta(days=2)
        chore = Chore.objects.create(
            title="Take out the recycling",
            next_due_date=due,
        )
        self.assertEqual(chore.title, "Take out the recycling")
        self.assertEqual(chore.description, "")
        self.assertEqual(chore.recurrence_type, Chore.RecurrenceType.WEEKLY)
        self.assertEqual(chore.next_due_date, due)
        self.assertIsNone(chore.current_assignee)

    def test_chore_str_representation(self):
        chore = Chore.objects.create(
            title="Vacuum living room",
            next_due_date=date.today(),
        )
        self.assertEqual(str(chore), "Vacuum living room")

    def test_chore_foreign_key_relationship(self):
        chore = Chore.objects.create(
            title="Wipe down kitchen counters",
            next_due_date=date.today(),
            current_assignee=self.roommate,
        )
        self.assertEqual(chore.current_assignee, self.roommate)
        self.assertIn(chore, self.roommate.assigned_chores.all())

    def test_chore_foreign_key_set_null_on_roommate_delete(self):
        chore = Chore.objects.create(
            title="Clean bathroom",
            next_due_date=date.today(),
            current_assignee=self.roommate,
        )
        self.roommate.delete()
        chore.refresh_from_db()
        self.assertIsNone(chore.current_assignee)


class ChoreLogModelTests(TestCase):
    def setUp(self):
        self.roommate = Roommate.objects.create(name="Casey")
        self.chore = Chore.objects.create(
            title="Empty dishwasher",
            next_due_date=date.today(),
            current_assignee=self.roommate,
        )

    def test_chore_log_creation_and_defaults(self):
        before = timezone.now()
        log = ChoreLog.objects.create(
            chore=self.chore,
            completed_by=self.roommate,
        )
        after = timezone.now()
        self.assertEqual(log.chore, self.chore)
        self.assertEqual(log.completed_by, self.roommate)
        self.assertTrue(before <= log.completed_at <= after)

    def test_chore_log_str_representation(self):
        log = ChoreLog.objects.create(
            chore=self.chore,
            completed_by=self.roommate,
        )
        self.assertEqual(str(log), "Empty dishwasher completed by Casey")

    def test_chore_log_foreign_key_relationships(self):
        log = ChoreLog.objects.create(
            chore=self.chore,
            completed_by=self.roommate,
        )
        self.assertIn(log, self.chore.logs.all())
        self.assertIn(log, self.roommate.chore_logs.all())

    def test_chore_log_cascade_on_chore_delete(self):
        ChoreLog.objects.create(
            chore=self.chore,
            completed_by=self.roommate,
        )
        self.assertEqual(ChoreLog.objects.count(), 1)
        self.chore.delete()
        self.assertEqual(ChoreLog.objects.count(), 0)

    def test_chore_log_cascade_on_roommate_delete(self):
        ChoreLog.objects.create(
            chore=self.chore,
            completed_by=self.roommate,
        )
        self.assertEqual(ChoreLog.objects.count(), 1)
        self.roommate.delete()
        self.assertEqual(ChoreLog.objects.count(), 0)

