from datetime import date, datetime, timedelta
from io import StringIO
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from core.forms import ChoreForm
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


class DashboardViewTests(TestCase):
    def setUp(self):
        self.alex = Roommate.objects.create(name="Alex", color_code="#3B82F6", order_index=0, is_active=True)
        self.sam = Roommate.objects.create(name="Sam", color_code="#10B981", order_index=1, is_active=True)

        today = date.today()
        self.chore_alex = Chore.objects.create(
            title="Clean Microwave",
            description="Wipe down the inside of the microwave.",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=today,
            current_assignee=self.alex,
        )
        self.chore_sam = Chore.objects.create(
            title="Mop Kitchen",
            description="Mop the floor with hot water and soap.",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=today + timedelta(days=2),
            current_assignee=self.sam,
        )
        self.chore_unassigned = Chore.objects.create(
            title="Recycling Bins",
            description="Take the blue bins to the street.",
            recurrence_type=Chore.RecurrenceType.BIWEEKLY,
            next_due_date=today + timedelta(days=4),
            current_assignee=None,
        )

    def _set_active_roommate(self, roommate):
        session = self.client.session
        session["active_roommate_id"] = roommate.id
        session.save()

    def test_dashboard_renders_and_segregates_chores_for_alex(self):
        self._set_active_roommate(self.alex)
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

        # Context assertions
        self.assertEqual(list(response.context["my_chores"]), [self.chore_alex])
        self.assertEqual(
            list(response.context["all_chores"]),
            [self.chore_alex, self.chore_sam, self.chore_unassigned],
        )

        # Content assertions
        self.assertContains(response, "My Chores")
        self.assertContains(response, "All Household Chores")
        self.assertContains(response, "Clean Microwave")
        self.assertContains(response, "Mop Kitchen")
        self.assertContains(response, "Recycling Bins")
        self.assertContains(response, "(You)")

    def test_dashboard_switches_my_chores_when_profile_changes(self):
        # View as Sam
        self._set_active_roommate(self.sam)
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(list(response.context["my_chores"]), [self.chore_sam])
        self.assertNotIn(self.chore_alex, response.context["my_chores"])

    def test_dashboard_empty_states(self):
        # Delete all chores
        Chore.objects.all().delete()
        self._set_active_roommate(self.alex)

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["my_chores"]), [])
        self.assertEqual(list(response.context["all_chores"]), [])

        self.assertContains(response, "You're all caught up!")
        self.assertContains(response, "No chores created yet")

    def test_dashboard_displays_assignee_and_recurrence_info(self):
        self._set_active_roommate(self.alex)
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

        # Recurrence labels
        self.assertContains(response, "Daily")
        self.assertContains(response, "Weekly")
        self.assertContains(response, "Bi-weekly")

        # Assignee names and fallback
        self.assertContains(response, "Alex")
        self.assertContains(response, "Sam")
        self.assertContains(response, "Unassigned")


class ChoreFormTests(TestCase):
    def setUp(self):
        self.active_roommate = Roommate.objects.create(name="Alex", is_active=True)
        self.inactive_roommate = Roommate.objects.create(name="Taylor", is_active=False)

    def test_chore_form_valid_data(self):
        form = ChoreForm(
            data={
                "title": "Clean kitchen",
                "description": "Wipe surfaces",
                "recurrence_type": Chore.RecurrenceType.WEEKLY,
                "current_assignee": self.active_roommate.id,
                "next_due_date": date.today(),
            }
        )
        self.assertTrue(form.is_valid())

    def test_chore_form_missing_required_fields(self):
        form = ChoreForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("next_due_date", form.errors)

    def test_chore_form_assignee_queryset_excludes_inactive(self):
        form = ChoreForm()
        assignees = list(form.fields["current_assignee"].queryset)
        self.assertIn(self.active_roommate, assignees)
        self.assertNotIn(self.inactive_roommate, assignees)


class ChoreCRUDViewTests(TestCase):
    def setUp(self):
        self.alex = Roommate.objects.create(name="Alex", color_code="#3B82F6", order_index=0, is_active=True)
        self.sam = Roommate.objects.create(name="Sam", color_code="#10B981", order_index=1, is_active=True)
        session = self.client.session
        session["active_roommate_id"] = self.alex.id
        session.save()

    def test_chore_create_get(self):
        response = self.client.get(reverse("chore_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Chore")
        self.assertIsInstance(response.context["form"], ChoreForm)

    def test_chore_create_post_valid(self):
        due = date.today() + timedelta(days=3)
        response = self.client.post(
            reverse("chore_create"),
            {
                "title": "Scrub bathtub",
                "description": "Use tub cleaner",
                "recurrence_type": Chore.RecurrenceType.BIWEEKLY,
                "current_assignee": self.sam.id,
                "next_due_date": due.strftime("%Y-%m-%d"),
            },
        )
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Chore.objects.filter(title="Scrub bathtub", current_assignee=self.sam).exists())

    def test_chore_create_post_invalid(self):
        response = self.client.post(
            reverse("chore_create"),
            {
                "title": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Chore.objects.count(), 0)

    def test_chore_edit_get(self):
        chore = Chore.objects.create(
            title="Clean stove",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=date.today(),
            current_assignee=self.alex,
        )
        response = self.client.get(reverse("chore_edit", args=[chore.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Chore: Clean stove")
        self.assertContains(response, "Clean stove")

    def test_chore_edit_post_valid(self):
        chore = Chore.objects.create(
            title="Clean stove",
            description="Old desc",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=date.today(),
            current_assignee=self.alex,
        )
        new_due = date.today() + timedelta(days=5)
        response = self.client.post(
            reverse("chore_edit", args=[chore.id]),
            {
                "title": "Clean stove & oven",
                "description": "Updated desc",
                "recurrence_type": Chore.RecurrenceType.MONTHLY,
                "current_assignee": self.sam.id,
                "next_due_date": new_due.strftime("%Y-%m-%d"),
            },
        )
        self.assertRedirects(response, reverse("index"))
        chore.refresh_from_db()
        self.assertEqual(chore.title, "Clean stove & oven")
        self.assertEqual(chore.description, "Updated desc")
        self.assertEqual(chore.recurrence_type, Chore.RecurrenceType.MONTHLY)
        self.assertEqual(chore.current_assignee, self.sam)
        self.assertEqual(chore.next_due_date, new_due)

    def test_chore_archive_post(self):
        chore = Chore.objects.create(
            title="Old temporary task",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=date.today(),
            current_assignee=self.alex,
        )
        self.assertFalse(chore.is_archived)

        response = self.client.post(reverse("chore_archive", args=[chore.id]))
        self.assertRedirects(response, reverse("index"))
        chore.refresh_from_db()
        self.assertTrue(chore.is_archived)

        # Verify it no longer appears in active dashboard lists
        dashboard_res = self.client.get(reverse("index"))
        self.assertNotIn(chore, dashboard_res.context["my_chores"])
        self.assertNotIn(chore, dashboard_res.context["all_chores"])
        self.assertNotContains(dashboard_res, "Old temporary task")


class RoundRobinRotationEngineTests(TestCase):
    def setUp(self):
        self.alex = Roommate.objects.create(name="Alex", order_index=0, is_active=True)
        self.sam = Roommate.objects.create(name="Sam", order_index=1, is_active=True)
        self.jordan = Roommate.objects.create(name="Jordan", order_index=2, is_active=True)
        self.today = timezone.now().date()

    def test_full_rotation_cycle_and_wraparound(self):
        chore = Chore.objects.create(
            title="Take out trash",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=self.today - timedelta(days=10),  # Overdue chore
            current_assignee=self.alex,
        )

        # 1st completion: Alex completes -> advances to Sam, due in today + 7 days
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.current_assignee, self.sam)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=7))

        # 2nd completion: Sam completes -> advances to Jordan, due in today + 7 days
        chore.mark_done(completed_by=self.sam)
        self.assertEqual(chore.current_assignee, self.jordan)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=7))

        # 3rd completion: Jordan completes -> wraps around to Alex, due in today + 7 days
        chore.mark_done(completed_by=self.jordan)
        self.assertEqual(chore.current_assignee, self.alex)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=7))

    def test_chore_log_creation_on_mark_done(self):
        chore = Chore.objects.create(
            title="Clean bathroom",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=self.today,
            current_assignee=self.alex,
        )
        before = timezone.now()
        log = chore.mark_done(completed_by=self.alex)
        after = timezone.now()

        self.assertIsNotNone(log)
        self.assertEqual(log.chore, chore)
        self.assertEqual(log.completed_by, self.alex)
        self.assertTrue(before <= log.completed_at <= after)
        self.assertEqual(ChoreLog.objects.filter(chore=chore).count(), 1)

    def test_due_date_math_daily(self):
        chore = Chore.objects.create(
            title="Wipe counters",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=self.today - timedelta(days=5),
            current_assignee=self.alex,
        )
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=1))

    def test_due_date_math_weekly(self):
        chore = Chore.objects.create(
            title="Mop kitchen floor",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=self.today - timedelta(days=14),
            current_assignee=self.alex,
        )
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=7))

    def test_due_date_math_biweekly(self):
        chore = Chore.objects.create(
            title="Clean fridge",
            recurrence_type=Chore.RecurrenceType.BIWEEKLY,
            next_due_date=self.today - timedelta(days=30),
            current_assignee=self.alex,
        )
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=14))

    def test_due_date_math_monthly(self):
        chore = Chore.objects.create(
            title="Deep clean oven",
            recurrence_type=Chore.RecurrenceType.MONTHLY,
            next_due_date=self.today - timedelta(days=60),
            current_assignee=self.alex,
        )
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=30))

    def test_overdue_chore_due_date_calculated_from_today_not_past_date(self):
        # Even if chore was due 100 days ago, next due date is today + interval
        chore = Chore.objects.create(
            title="Wash windows",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=self.today - timedelta(days=100),
            current_assignee=self.alex,
        )
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=7))

    def test_edge_case_single_active_roommate(self):
        # Only Alex is active
        self.sam.is_active = False
        self.sam.save()
        self.jordan.is_active = False
        self.jordan.save()

        chore = Chore.objects.create(
            title="Solo chore",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=date(2026, 9, 1),
            current_assignee=self.alex,
        )
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.current_assignee, self.alex)

        # Mark done again - assignee stays Alex
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.current_assignee, self.alex)

    def test_edge_case_current_assignee_becomes_inactive(self):
        # Sam (order_index=1) is deactivated
        self.sam.is_active = False
        self.sam.save()

        # Chore was assigned to Sam before deactivation
        chore = Chore.objects.create(
            title="Dishes",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=date(2026, 9, 1),
            current_assignee=self.sam,
        )

        # Should skip inactive Sam and assign to Jordan (order_index=2)
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.current_assignee, self.jordan)

    def test_edge_case_inactive_assignee_past_end_wraps_around(self):
        # Jordan (order_index=2) is deactivated
        self.jordan.is_active = False
        self.jordan.save()

        # Chore was assigned to Jordan before deactivation
        chore = Chore.objects.create(
            title="Dishes",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=date(2026, 9, 1),
            current_assignee=self.jordan,
        )

        # Jordan was at the end of order, so it should wrap to Alex (order_index=0)
        chore.mark_done(completed_by=self.alex)
        self.assertEqual(chore.current_assignee, self.alex)

    def test_edge_case_no_active_roommates(self):
        Roommate.objects.update(is_active=False)

        chore = Chore.objects.create(
            title="Orphaned task",
            recurrence_type=Chore.RecurrenceType.DAILY,
            next_due_date=date(2026, 9, 1),
            current_assignee=None,
        )

        # Must not crash, leaves assignee as None
        chore.mark_done(completed_by=None)
        self.assertIsNone(chore.current_assignee)
        self.assertEqual(chore.next_due_date, self.today + timedelta(days=1))

    def test_unassigned_chore_rotates_to_first_active_roommate(self):
        chore = Chore.objects.create(
            title="New unassigned chore",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=date(2026, 9, 1),
            current_assignee=None,
        )
        self.assertEqual(chore.get_next_assignee(), self.alex)


class ChoreMarkDoneViewTests(TestCase):
    def setUp(self):
        self.alex = Roommate.objects.create(name="Alex", color_code="#3B82F6", order_index=0, is_active=True)
        self.sam = Roommate.objects.create(name="Sam", color_code="#10B981", order_index=1, is_active=True)
        self.today = timezone.now().date()
        self.chore = Chore.objects.create(
            title="Clean windows",
            recurrence_type=Chore.RecurrenceType.WEEKLY,
            next_due_date=self.today - timedelta(days=5),
            current_assignee=self.alex,
        )
        session = self.client.session
        session["active_roommate_id"] = self.alex.id
        session.save()

    def test_mark_done_post_advances_chore_and_records_log(self):
        url = reverse("chore_mark_done", args=[self.chore.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("index"))

        self.chore.refresh_from_db()
        self.assertEqual(self.chore.current_assignee, self.sam)
        self.assertEqual(self.chore.next_due_date, self.today + timedelta(days=7))

        log = ChoreLog.objects.filter(chore=self.chore).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.completed_by, self.alex)

    def test_mark_done_post_by_different_active_roommate(self):
        # Sam marks done instead of Alex
        session = self.client.session
        session["active_roommate_id"] = self.sam.id
        session.save()

        url = reverse("chore_mark_done", args=[self.chore.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse("index"))

        log = ChoreLog.objects.filter(chore=self.chore).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.completed_by, self.sam)

    def test_mark_done_get_does_not_mutate_state(self):
        url = reverse("chore_mark_done", args=[self.chore.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse("index"))

        self.chore.refresh_from_db()
        self.assertEqual(self.chore.current_assignee, self.alex)
        self.assertEqual(self.chore.next_due_date, self.today - timedelta(days=5))
        self.assertEqual(ChoreLog.objects.filter(chore=self.chore).count(), 0)

    def test_dashboard_renders_mark_done_button(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "✓ Mark Done")
        self.assertContains(response, reverse("chore_mark_done", args=[self.chore.id]))


class ChoreStatusHierarchyTests(TestCase):
    def test_status_boundary_more_than_24_hours_is_upcoming(self):
        now = timezone.now()
        chore_25h = Chore(next_due_date=now + timedelta(hours=25))
        self.assertEqual(chore_25h.status, "upcoming")
        self.assertEqual(chore_25h.get_status(as_of=now), "upcoming")

    def test_status_boundary_exactly_24_hours_is_due_today(self):
        now = timezone.now()
        chore_24h = Chore(next_due_date=now + timedelta(hours=24))
        self.assertEqual(chore_24h.status, "due_today")
        self.assertEqual(chore_24h.get_status(as_of=now), "due_today")

    def test_status_boundary_within_24_hours_is_due_today(self):
        now = timezone.now()
        chore_23h = Chore(next_due_date=now + timedelta(hours=23))
        self.assertEqual(chore_23h.status, "due_today")
        self.assertEqual(chore_23h.get_status(as_of=now), "due_today")

        chore_1h = Chore(next_due_date=now + timedelta(hours=1))
        self.assertEqual(chore_1h.status, "due_today")
        self.assertEqual(chore_1h.get_status(as_of=now), "due_today")

    def test_status_boundary_past_deadline_is_overdue(self):
        now = timezone.now()
        chore_past_sec = Chore(next_due_date=now - timedelta(seconds=1))
        self.assertEqual(chore_past_sec.status, "overdue")
        self.assertEqual(chore_past_sec.get_status(as_of=now), "overdue")

        chore_past_hours = Chore(next_due_date=now - timedelta(hours=5))
        self.assertEqual(chore_past_hours.status, "overdue")
        self.assertEqual(chore_past_hours.get_status(as_of=now), "overdue")

    def test_status_with_persisted_date_objects(self):
        today = timezone.now().date()
        chore_today = Chore.objects.create(title="Today Task", next_due_date=today)
        self.assertEqual(chore_today.status, "due_today")

        chore_future = Chore.objects.create(title="Future Task", next_due_date=today + timedelta(days=2))
        self.assertEqual(chore_future.status, "upcoming")

        chore_overdue = Chore.objects.create(title="Overdue Task", next_due_date=today - timedelta(days=1))
        self.assertEqual(chore_overdue.status, "overdue")

    def test_status_fallback_when_no_due_date(self):
        chore = Chore(title="No date")
        chore.next_due_date = None
        self.assertEqual(chore.status, "upcoming")


class DashboardStatusBadgesAndNagBannerTests(TestCase):
    def setUp(self):
        self.alex = Roommate.objects.create(name="Alex", color_code="#3B82F6", order_index=0, is_active=True)
        self.sam = Roommate.objects.create(name="Sam", color_code="#10B981", order_index=1, is_active=True)
        session = self.client.session
        session["active_roommate_id"] = self.alex.id
        session.save()
        self.today = timezone.now().date()

    def test_dashboard_renders_color_coded_badges(self):
        Chore.objects.create(
            title="Overdue Chore",
            next_due_date=self.today - timedelta(days=2),
            current_assignee=self.alex,
        )
        Chore.objects.create(
            title="Due Today Chore",
            next_due_date=self.today,
            current_assignee=self.alex,
        )
        Chore.objects.create(
            title="Upcoming Chore",
            next_due_date=self.today + timedelta(days=3),
            current_assignee=self.sam,
        )

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

        # Assert all 3 status badge texts are present
        self.assertContains(response, "Overdue")
        self.assertContains(response, "Due Today")
        self.assertContains(response, "Upcoming")

        # Assert color classes for badges are present
        self.assertContains(response, "bg-red-100 text-red-800")
        self.assertContains(response, "bg-amber-100 text-amber-800")
        self.assertContains(response, "bg-emerald-100 text-emerald-800")

    def test_nag_banner_appears_when_overdue_chores_exist(self):
        Chore.objects.create(
            title="Old Trash",
            next_due_date=self.today - timedelta(days=1),
            current_assignee=self.alex,
        )

        # Visible on dashboard
        response_index = self.client.get(reverse("index"))
        self.assertEqual(response_index.status_code, 200)
        self.assertContains(response_index, "id=\"overdue-nag-banner\"")
        self.assertContains(response_index, "Overdue Chores Warning")

        # Visible on other pages (e.g. chore create page)
        response_create = self.client.get(reverse("chore_create"))
        self.assertEqual(response_create.status_code, 200)
        self.assertContains(response_create, "id=\"overdue-nag-banner\"")
        self.assertContains(response_create, "Overdue Chores Warning")

    def test_nag_banner_hidden_when_no_overdue_chores_exist(self):
        Chore.objects.create(
            title="Today chore",
            next_due_date=self.today,
            current_assignee=self.alex,
        )
        Chore.objects.create(
            title="Future chore",
            next_due_date=self.today + timedelta(days=5),
            current_assignee=self.sam,
        )

        # Hidden on dashboard
        response_index = self.client.get(reverse("index"))
        self.assertEqual(response_index.status_code, 200)
        self.assertNotContains(response_index, "id=\"overdue-nag-banner\"")
        self.assertNotContains(response_index, "Overdue Chores Warning")

        # Hidden on other pages
        response_create = self.client.get(reverse("chore_create"))
        self.assertEqual(response_create.status_code, 200)
        self.assertNotContains(response_create, "id=\"overdue-nag-banner\"")

    def test_archived_overdue_chore_does_not_trigger_nag_banner(self):
        Chore.objects.create(
            title="Retired Past Chore",
            next_due_date=self.today - timedelta(days=3),
            current_assignee=self.alex,
            is_archived=True,
        )

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "id=\"overdue-nag-banner\"")
        self.assertNotContains(response, "Overdue Chores Warning")




