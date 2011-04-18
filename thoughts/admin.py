from django.contrib import admin
from thoughts.models import Thought

class ThoughtAdmin(admin.ModelAdmin):
    pass

admin.site.register(Thought, ThoughtAdmin)