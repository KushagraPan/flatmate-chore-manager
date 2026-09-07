from django.contrib import admin
from .models import Chore, ChoreLog, Roommate

@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("title", "recurrence_type", "next_due_date", "current_assignee", "is_archived")
    list_filter = ("is_archived", "recurrence_type")
    search_fields = ("title", "description")


admin.site.register(Roommate)
admin.site.register(ChoreLog)
