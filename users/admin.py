from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from users.models import User, Achievement, UserInfo


@admin.action(description="is_active = True")
def is_active_true(modeladmin, request, queryset):
    """Django Admin에서 is_admin을 일괄적으로 True 처리"""
    queryset.update(is_active=True)


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "is_active",
            "is_admin",
            "username",
            "image",
            "wear_achievement",
            "achieve",
            "followings",
        ]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    actions = [is_active_true]

    list_display = ["email", "id", "is_active", "is_admin"]
    list_filter = ["is_admin", "is_active"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        (
            "Personal info",
            {
                "fields": [
                    "username",
                    "image",
                    "wear_achievement",
                    "achieve",
                    "followings",
                ]
            },
        ),
        ("Permissions", {"fields": ["is_admin", "is_active"]}),
        ("Important dates", {"fields": ["last_login"]}),
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


class AchievementAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "comment"]


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ["player"]


admin.site.register(Achievement, AchievementAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
