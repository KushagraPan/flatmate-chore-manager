from core.models import Roommate


def active_roommate(request):
    """
    Context processor providing the active roommate and the list of all active roommates.
    Returns None for active_roommate if no valid profile is selected in the session.
    """
    all_roommates = Roommate.objects.filter(is_active=True)
    selected_id = request.session.get("active_roommate_id")

    roommate = None
    if selected_id:
        roommate = all_roommates.filter(id=selected_id).first()

    return {
        "active_roommate": roommate,
        "all_roommates": all_roommates,
    }
