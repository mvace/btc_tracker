from django import forms
from django.forms import DateTimeInput
from .models import Transaction, Portfolio
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name"]

    name = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Portfolio Name:",
                "maxlength": "30",
            }
        ),
    )


def validate_amount_range(value):
    min_amount = 0.00000000
    max_amount = 100000

    if value < min_amount or value > max_amount:
        raise ValidationError(
            f"Amount must be between {min_amount:.8f} and {max_amount}."
        )


class TransactionForm(forms.ModelForm):
    timestamp = forms.DateTimeField(
        label="Select Transaction Date and Time",
        widget=DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
                "placeholder": "Initial date...",
            }
        ),
    )

    amount = forms.DecimalField(
        label="",
        validators=[validate_amount_range],
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter the amount",
            }
        ),
    )

    class Meta:
        model = Transaction
        fields = ["timestamp", "amount"]


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["username"].widget.attrs["placeholder"] = "User Name"
        self.fields["username"].label = ""
        self.fields["username"].help_text = (
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        )

        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password1"].label = ""
        self.fields["password1"].help_text = [
            "Your password can't be too similar to your other personal information.",
            " Your password must contain at least 8 characters.",
            " Your password can't be a commonly used password.",
            " Your password can't be entirely numeric.",
        ]

        self.fields["password2"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm Password"
        self.fields["password2"].label = ""
        self.fields["password2"].help_text = (
            "Enter the same password as before, for verification."
        )


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
            }
        ),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        ),
    )
