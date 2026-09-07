from django.shortcuts import redirect, render
from core.models import Chore, Roommate


def index(request):
    """
    Main household dashboard displaying:
    - 'my_chores': chores assigned to the active roommate
    - 'all_chores': all chores across the household
    """
    active_roommate = getattr(request, "active_roommate", None)
    if not active_roommate:
        active_id = request.session.get("active_roommate_id")
        active_roommate = (
            Roommate.objects.filter(id=active_id, is_active=True).first()
            if active_id
            else None
        )

    all_chores = Chore.objects.select_related("current_assignee").all()
    my_chores = (
        all_chores.filter(current_assignee=active_roommate)
        if active_roommate
        else Chore.objects.none()
    )

    return render(
        request,
        "core/index.html",
        {
            "my_chores": my_chores,
            "all_chores": all_chores,
        },
    )


def select_roommate(request):
    """
    Explicit 'Who are you?' picker page.
    Renders active roommates to pick from and saves selection to session.
    """
    next_url = request.GET.get("next") or request.POST.get("next") or "/"

    if request.method == "POST":
        roommate_id = request.POST.get("roommate_id")
        if roommate_id:
            try:
                roommate_id = int(roommate_id)
                if Roommate.objects.filter(id=roommate_id, is_active=True).exists():
                    request.session["active_roommate_id"] = roommate_id
                    return redirect(next_url)
            except (ValueError, TypeError):
                pass

    active_roommates = Roommate.objects.filter(is_active=True)
    return render(
        request,
        "core/select_roommate.html",
        {
            "roommates": active_roommates,
            "next_url": next_url,
        },
    )


def switch_roommate(request):
    """
    Updates the active roommate ID in the session from the navbar dropdown.
    Accepts POST with 'roommate_id' and redirects back to previous page or index.
    """
    if request.method == "POST":
        roommate_id = request.POST.get("roommate_id")
        if roommate_id:
            try:
                roommate_id = int(roommate_id)
                if Roommate.objects.filter(id=roommate_id, is_active=True).exists():
                    request.session["active_roommate_id"] = roommate_id
            except (ValueError, TypeError):
                pass

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    return redirect(next_url)
