from core.models import Roommate


def active_roommate(request):
    """
    Context processor providing the active roommate and the list of all active roommates.
    Uses request.active_roommate attached by middleware, or falls back to session lookup.
    """
    all_roommates = Roommate.objects.filter(is_active=True)

    if hasattr(request, "active_roommate"):
        roommate = request.active_roommate
    else:
        selected_id = request.session.get("active_roommate_id")
        roommate = all_roommates.filter(id=selected_id).first() if selected_id else None

    return {
        "active_roommate": roommate,
        "all_roommates": all_roommates,
    }
