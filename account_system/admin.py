from account_system.models import UserProfile, Department
from django.contrib import admin


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
    )


admin.site.register(UserProfile, UserAdmin)


class DepartMentAdmin(admin.ModelAdmin):
    list_display = (
      #  'company_name',
        "department_name",
        'level'
    )


admin.site.register(Department, DepartMentAdmin)
