from datetime import date, timedelta
from io import StringIO
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
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


class SeedDataCommandTests(TestCase):
    def test_seed_data_populates_expected_models(self):
        out = StringIO()
        call_command("seed_data", stdout=out)
        self.assertIn("Successfully seeded default household data.", out.getvalue())

        self.assertEqual(Roommate.objects.count(), 4)
        self.assertEqual(Chore.objects.count(), 4)

        # Check all recurrence types exist
        recurrence_types = set(Chore.objects.values_list("recurrence_type", flat=True))
        self.assertEqual(
            recurrence_types,
            {
                Chore.RecurrenceType.DAILY,
                Chore.RecurrenceType.WEEKLY,
                Chore.RecurrenceType.BIWEEKLY,
                Chore.RecurrenceType.MONTHLY,
            },
        )

        # Check assignees are assigned and active
        for chore in Chore.objects.all():
            self.assertIsNotNone(chore.current_assignee)
            self.assertTrue(chore.current_assignee.is_active)

    def test_seed_data_is_idempotent(self):
        out1 = StringIO()
        out2 = StringIO()
        call_command("seed_data", stdout=out1)
        call_command("seed_data", stdout=out2)

        self.assertEqual(Roommate.objects.count(), 4)
        self.assertEqual(Chore.objects.count(), 4)


class ProfileSwitcherTests(TestCase):
    def setUp(self):
        self.alex = Roommate.objects.create(name="Alex", order_index=0, is_active=True)
        self.sam = Roommate.objects.create(name="Sam", order_index=1, is_active=True)
        self.taylor = Roommate.objects.create(name="Taylor", order_index=2, is_active=False)

    def test_redirect_to_select_roommate_when_no_session(self):
        response = self.client.get(reverse("index"))
        expected_url = f"{reverse('select_roommate')}?next={reverse('index')}"
        self.assertRedirects(response, expected_url)

    def test_select_roommate_page_renders_who_are_you_and_active_roommates(self):
        response = self.client.get(reverse("select_roommate"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Who are you?")
        self.assertContains(response, "Alex")
        self.assertContains(response, "Sam")
        self.assertNotContains(response, "Taylor")
        self.assertIsNone(response.context["active_roommate"])
        self.assertEqual(list(response.context["all_roommates"]), [self.alex, self.sam])

    def test_select_roommate_post_sets_session_and_redirects_to_next(self):
        target_url = reverse("index")
        response = self.client.post(
            reverse("select_roommate"),
            {"roommate_id": self.alex.id, "next": target_url},
        )
        self.assertRedirects(response, target_url)
        self.assertEqual(self.client.session.get("active_roommate_id"), self.alex.id)

        # After selection, visiting index does not redirect and displays active roommate
        follow_response = self.client.get(target_url)
        self.assertEqual(follow_response.status_code, 200)
        self.assertEqual(follow_response.context["active_roommate"], self.alex)

    def test_switch_roommate_from_navbar_updates_session(self):
        # Set session initially to Alex
        session = self.client.session
        session["active_roommate_id"] = self.alex.id
        session.save()

        response = self.client.post(
            reverse("switch_roommate"),
            {"roommate_id": self.sam.id, "next": reverse("index")},
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session.get("active_roommate_id"), self.sam.id)

        follow_response = self.client.get(reverse("index"))
        self.assertEqual(follow_response.context["active_roommate"], self.sam)

    def test_switch_roommate_ignores_invalid_or_inactive_id(self):
        # Set session initially to Alex
        session = self.client.session
        session["active_roommate_id"] = self.alex.id
        session.save()

        # Try switching to non-existent ID
        self.client.post(reverse("switch_roommate"), {"roommate_id": 99999})
        self.assertEqual(self.client.session.get("active_roommate_id"), self.alex.id)

        # Try switching to inactive roommate
        self.client.post(reverse("switch_roommate"), {"roommate_id": self.taylor.id})
        self.assertEqual(self.client.session.get("active_roommate_id"), self.alex.id)

        # Try switching to malformed input
        self.client.post(reverse("switch_roommate"), {"roommate_id": "invalid"})
        self.assertEqual(self.client.session.get("active_roommate_id"), self.alex.id)

    def test_middleware_redirects_if_session_roommate_becomes_inactive(self):
        # Set session to Sam
        session = self.client.session
        session["active_roommate_id"] = self.sam.id
        session.save()

        # Mark Sam as inactive
        self.sam.is_active = False
        self.sam.save()

        response = self.client.get(reverse("index"))
        expected_url = f"{reverse('select_roommate')}?next={reverse('index')}"
        self.assertRedirects(response, expected_url)

    def test_middleware_redirects_if_session_id_invalid(self):
        session = self.client.session
        session["active_roommate_id"] = 99999
        session.save()

        response = self.client.get(reverse("index"))
        expected_url = f"{reverse('select_roommate')}?next={reverse('index')}"
        self.assertRedirects(response, expected_url)

    def test_no_redirect_loop_when_no_roommates_exist(self):
        Roommate.objects.all().delete()
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["active_roommate"])
        self.assertEqual(list(response.context["all_roommates"]), [])

    def test_navbar_renders_active_profile_and_options(self):
        session = self.client.session
        session["active_roommate_id"] = self.alex.id
        session.save()

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active: Alex")
        self.assertContains(response, "Switch to Alex")
        self.assertContains(response, "Switch to Sam")
        self.assertNotContains(response, "Switch to Taylor")

