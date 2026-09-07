from django.shortcuts import get_object_or_404, redirect, render
from core.forms import ChoreForm
from core.models import Chore, ChoreLog, Roommate


def index(request):
    """
    Main household dashboard displaying:
    - 'my_chores': active chores assigned to the active roommate
    - 'all_chores': active chores across the household
    - 'activity_feed': recent chore completion logs (up to 10)
    """
    active_roommate = getattr(request, "active_roommate", None)
    if not active_roommate:
        active_id = request.session.get("active_roommate_id")
        active_roommate = (
            Roommate.objects.filter(id=active_id, is_active=True).first()
            if active_id
            else None
        )

    all_chores = Chore.objects.filter(is_archived=False).select_related("current_assignee")
    my_chores = (
        all_chores.filter(current_assignee=active_roommate)
        if active_roommate
        else Chore.objects.none()
    )
    activity_feed = ChoreLog.objects.select_related(
        "chore", "completed_by"
    ).order_by("-completed_at", "-id")[:10]

    return render(
        request,
        "core/index.html",
        {
            "my_chores": my_chores,
            "all_chores": all_chores,
            "activity_feed": activity_feed,
        },
    )


def chore_create(request):
    """Create a new chore."""
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = ChoreForm()

    return render(
        request,
        "core/chore_form.html",
        {
            "form": form,
            "title": "Add New Chore",
            "submit_btn_text": "Create Chore",
        },
    )


def chore_edit(request, chore_id):
    """Edit an existing chore."""
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == "POST":
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = ChoreForm(instance=chore)

    return render(
        request,
        "core/chore_form.html",
        {
            "form": form,
            "chore": chore,
            "title": f"Edit Chore: {chore.title}",
            "submit_btn_text": "Save Changes",
        },
    )


def chore_archive(request, chore_id):
    """Archive a chore so it stops appearing in rotation without being deleted."""
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == "POST":
        chore.is_archived = True
        chore.save()
    return redirect("index")


def chore_mark_done(request, chore_id):
    """
    Mark a chore as done:
    1. Records ChoreLog with active_roommate.
    2. Advances rotation to the next active roommate.
    3. Recalculates next_due_date.
    """
    chore = get_object_or_404(Chore, id=chore_id)
    if request.method == "POST":
        active_roommate = getattr(request, "active_roommate", None)
        if not active_roommate:
            active_id = request.session.get("active_roommate_id")
            if active_id:
                active_roommate = Roommate.objects.filter(id=active_id, is_active=True).first()

        chore.mark_done(completed_by=active_roommate)

    return redirect("index")


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
