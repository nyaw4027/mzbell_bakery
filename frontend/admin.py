from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ContactMessage, TeamMember

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25





@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')


    

    # Optional: paginate fewer items per page
    # list_per_page = 10
