from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


class ChangeAccountSettingsForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangeAccountSettingsForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
