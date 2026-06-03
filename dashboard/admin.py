from django.contrib import admin
from .models import *

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active', 'category')
    search_fields = ('question', 'answer')
    list_filter = ('is_active', 'category')


admin.site.register(ContactMessage)
admin.site.register(SuccessStory)

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'designation', 'expertise', 'experience_years', 'rating', 'order_index', 'is_active')
    list_editable = ('designation', 'experience_years', 'rating', 'order_index', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'designation', 'expertise')
    list_filter = ('is_active', 'expertise')
@admin.register(CommunityStory)
class CommunityStoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'location', 'order_index', 'is_active')
    list_editable = ('order_index', 'is_active')
    search_fields = ('name', 'role', 'location', 'bio', 'full_story')
    list_filter = ('is_active', 'location')
