from django import forms
from django.utils.translation import gettext_lazy as _
import forwarder.models as fm

class ForwardForm(forms.Form):

    student_id = forms.CharField(
        label=_("Student ID"),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        student_id = cleaned_data["student_id"]
        try:
            record = fm.ForwardMapping.objects.get(student_id=student_id)
        except fm.ForwardMapping.DoesNotExist:
            self.add_error("student_id", _("The ID is not in the registration list"))
        else:
            cleaned_data["record"] = record
        return cleaned_data


class RegisterForm(ForwardForm):

    password = forms.CharField(
        label=_("Password"),
        max_length=64,
        widget=forms.PasswordInput,
        required=True
    )
    password_check = forms.CharField(
        label=_("Password again"),
        max_length=64,
        widget=forms.PasswordInput,
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["password"] != cleaned_data["password_check"]:
            self.add_error("password_check", _("Passwords must match"))
        if cleaned_data["record"].created:
            self.add_error("student_id", _("Account has already been created"))



