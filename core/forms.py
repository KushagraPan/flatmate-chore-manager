from django import forms
from core.models import Chore, Roommate


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = [
            "title",
            "description",
            "recurrence_type",
            "current_assignee",
            "next_due_date",
        ]
        labels = {
            "current_assignee": "Assignee",
            "recurrence_type": "Recurrence Frequency",
            "next_due_date": "Next Due Date",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
                    "placeholder": "e.g. Empty dishwasher",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full rounded-lg border border-slate-300 px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
                    "rows": 3,
                    "placeholder": "Additional instructions or details (optional)...",
                }
            ),
            "recurrence_type": forms.Select(
                attrs={
                    "class": "w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
                }
            ),
            "current_assignee": forms.Select(
                attrs={
                    "class": "w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
                }
            ),
            "next_due_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-sm text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["current_assignee"].queryset = Roommate.objects.filter(is_active=True)
        self.fields["current_assignee"].empty_label = "Unassigned"
        self.fields["description"].required = False
