from django import forms
from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Enter Password",
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Confirm Password",
    }))

    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number", "email", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter First Name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter Last Name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter Email"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Enter Phone Number"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control rounded-0"

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data["password"]
        confirm_password = cleaned_data["confirm_password"]

        if password != confirm_password:
            raise forms.ValidationError("Password doesn't match.")

        return cleaned_data

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["first_name", "last_name", "phone_number"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control rounded-0"

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages=
        {"invalid": "Image files only"}, widget=forms.FileInput()
    )
    
    class Meta:
        model = UserProfile
        fields = ["address_line_1", "address_line_2", "profile_picture", "city", "state", "country"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control rounded-0"
        