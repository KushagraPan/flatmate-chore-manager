from datetime import timedelta
from django.db import models
from django.utils import timezone


class Roommate(models.Model):
    name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7, default="#3B82F6")
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order_index", "id"]

    def __str__(self):
        return self.name


class Chore(models.Model):
    class RecurrenceType(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    recurrence_type = models.CharField(
        max_length=20,
        choices=RecurrenceType.choices,
        default=RecurrenceType.WEEKLY,
    )
    next_due_date = models.DateField()
    current_assignee = models.ForeignKey(
        Roommate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_chores",
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["next_due_date", "id"]

    def __str__(self):
        return self.title

    def get_next_assignee(self):
        """
        Calculates the next active roommate in order_index sequence.
        Handles:
        - Wrap-around after the last active roommate.
        - Single active roommate (stays the same).
        - Inactive current assignee (skips to next active one).
        - Zero active roommates (returns None).
        """
        active_roommates = list(
            Roommate.objects.filter(is_active=True).order_by("order_index", "id")
        )
        if not active_roommates:
            return None

        if len(active_roommates) == 1:
            return active_roommates[0]

        if self.current_assignee_id:
            current_idx = None
            for idx, roommate in enumerate(active_roommates):
                if roommate.id == self.current_assignee_id:
                    current_idx = idx
                    break

            if current_idx is not None:
                return active_roommates[(current_idx + 1) % len(active_roommates)]

            # Current assignee has become inactive or deleted
            try:
                current_roommate = self.current_assignee
            except Roommate.DoesNotExist:
                current_roommate = None

            if current_roommate:
                current_key = (current_roommate.order_index, current_roommate.id)
                for roommate in active_roommates:
                    if (roommate.order_index, roommate.id) > current_key:
                        return roommate

        return active_roommates[0]

    def calculate_next_due_date(self):
        """
        Calculates the next due date based on recurrence_type from today:
        - Daily: today + 1 day
        - Weekly: today + 7 days
        - Bi-weekly: today + 14 days
        - Monthly: today + 30 days
        """
        days_map = {
            self.RecurrenceType.DAILY: 1,
            self.RecurrenceType.WEEKLY: 7,
            self.RecurrenceType.BIWEEKLY: 14,
            self.RecurrenceType.MONTHLY: 30,
        }
        days = days_map.get(self.recurrence_type, 7)
        return timezone.now().date() + timedelta(days=days)

    def mark_done(self, completed_by=None):
        """
        Marks chore as completed:
        1. Records a ChoreLog entry.
        2. Advances current_assignee to the next active roommate.
        3. Recalculates next_due_date according to recurrence_type.
        """
        if completed_by is None and self.current_assignee is not None:
            completed_by = self.current_assignee

        log = None
        if completed_by:
            log = ChoreLog.objects.create(
                chore=self,
                completed_by=completed_by,
            )

        self.current_assignee = self.get_next_assignee()
        self.next_due_date = self.calculate_next_due_date()
        self.save()
        return log


class ChoreLog(models.Model):
    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    completed_by = models.ForeignKey(
        Roommate,
        on_delete=models.CASCADE,
        related_name="chore_logs",
    )
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-completed_at", "-id"]

    def __str__(self):
        chore_title = self.chore.title if self.chore else "Unknown"
        actor = self.completed_by.name if self.completed_by else "Unknown"
        return f"{chore_title} completed by {actor}"
