from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ScanResult, PasswordAudit,EducationBlog


# Unregister the default User admin if you want to customize it
# admin.site.unregister(User)

class ScanResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'scan_type', 'target', 'timestamp', 'short_result')
    list_filter = ('scan_type', 'timestamp', 'user')
    search_fields = ('target', 'result', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def short_result(self, obj):
        return obj.result[:50] + '...' if len(obj.result) > 50 else obj.result
    short_result.short_description = 'Result (short)'

class PasswordAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'strength', 'timestamp', 'masked_password')
    list_filter = ('strength', 'timestamp', 'user')
    search_fields = ('user__username', 'strength')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    
    def masked_password(self, obj):
        return obj.password  # Already masked in the model's save method
    masked_password.short_description = 'Password'

# Optional: If you want to extend the User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    date_hierarchy = 'date_joined'

# Register your models here
admin.site.register(ScanResult, ScanResultAdmin)
admin.site.register(PasswordAudit, PasswordAuditAdmin)

# If you're customizing the User admin, uncomment this:
# admin.site.register(User, CustomUserAdmin)

class EducationBlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'updated_date', 'is_featured')
    list_filter = ('published_date', 'is_featured')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'

admin.site.register(EducationBlog, EducationBlogAdmin)