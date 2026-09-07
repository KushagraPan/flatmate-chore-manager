from django.contrib import admin
from .models import Chore, ChoreLog, Roommate

admin.site.register(Roommate)
admin.site.register(Chore)
admin.site.register(ChoreLog)
