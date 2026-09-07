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

    class Meta:
        ordering = ["next_due_date", "id"]

    def __str__(self):
        return self.title


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
