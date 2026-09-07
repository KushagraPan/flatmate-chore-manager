from django.shortcuts import redirect
from django.urls import reverse
from core.models import Roommate


class RoommateSessionMiddleware:
    """
    Ensures an active roommate profile is selected in the session.
    Redirects unselected sessions to the 'Who are you?' picker page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_prefixes = [
            "/admin/",
            "/static/",
        ]
        exempt_names = [
            "select_roommate",
            "switch_roommate",
        ]

        active_id = request.session.get("active_roommate_id")
        request.active_roommate = (
            Roommate.objects.filter(id=active_id, is_active=True).first()
            if active_id
            else None
        )

        # Allow exempt URL prefixes
        if any(request.path.startswith(prefix) for prefix in exempt_prefixes):
            return self.get_response(request)

        # Allow exempt named endpoints
        try:
            exempt_urls = [reverse(name) for name in exempt_names]
            if any(request.path == url or request.path.startswith(url) for url in exempt_urls):
                return self.get_response(request)
        except Exception:
            pass

        # Only redirect if active roommates exist in the database
        if Roommate.objects.filter(is_active=True).exists():
            if not request.active_roommate:
                select_url = reverse("select_roommate")
                return redirect(f"{select_url}?next={request.path}")

        return self.get_response(request)
