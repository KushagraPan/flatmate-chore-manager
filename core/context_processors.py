from django.utils import timezone
from core.models import Chore, Roommate


def active_roommate(request):
    """
    Context processor providing:
    - active_roommate: currently active Roommate or None
    - all_roommates: queryset of all active Roommates
    - overdue_chores: list of active overdue chores across household
    - has_overdue_chores: boolean indicating if any household chore is overdue
    - overdue_chores_count: integer count of overdue chores
    """
    all_roommates = Roommate.objects.filter(is_active=True)

    if hasattr(request, "active_roommate"):
        roommate = request.active_roommate
    else:
        selected_id = request.session.get("active_roommate_id")
        roommate = all_roommates.filter(id=selected_id).first() if selected_id else None

    today = timezone.now().date()
    overdue_chores = list(
        Chore.objects.filter(is_archived=False, next_due_date__lt=today).select_related("current_assignee")
    )

    return {
        "active_roommate": roommate,
        "all_roommates": all_roommates,
        "overdue_chores": overdue_chores,
        "has_overdue_chores": len(overdue_chores) > 0,
        "overdue_chores_count": len(overdue_chores),
    }
