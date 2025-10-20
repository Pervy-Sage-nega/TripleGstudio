from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class ClientRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # User will be inactive until OTP verification
        if commit:
            user.save()
        return user

class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        required=True, 
        label="Enter OTP",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'class': 'form-control',
            'maxlength': '6'
        })
    )

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'firstName'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'lastName'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'id': 'email'})
    )
    
    class Meta:
        model = Profile
        fields = ['phone', 'assigned_architect', 'project_name', 'project_start', 'profile_pic']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-input', 
                'id': 'phone',
                'pattern': r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}',
                'placeholder': 'Enter phone number'
            }),
            'assigned_architect': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter assigned architect name'
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter project name'
            }),
            'project_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'profile_pic': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-input',
                'id': 'id_profile_pic'  # Make sure ID matches what JS expects
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        print(f"[DEBUG] FORM - Initializing form for user: {user.username if user else 'None'}")
        
        if user:
            # Override initial values with current user data
            self.initial['first_name'] = user.first_name or ''
            self.initial['last_name'] = user.last_name or ''
            self.initial['email'] = user.email or ''
            
            # Set widget values directly to ensure they appear in the form
            self.fields['first_name'].widget.attrs['value'] = user.first_name or ''
            self.fields['last_name'].widget.attrs['value'] = user.last_name or ''
            self.fields['email'].widget.attrs['value'] = user.email or ''
            
            print(f"[DEBUG] FORM - Set user data: {user.first_name} {user.last_name} ({user.email})")
        
        # Debug profile instance data
        if hasattr(self, 'instance') and self.instance and self.instance.pk:
            print(f"[DEBUG] FORM - Profile instance: phone={self.instance.phone}, architect={self.instance.assigned_architect}, project={self.instance.project_name}")
            
            # Override initial values with profile data
            self.initial['phone'] = self.instance.phone or ''
            self.initial['assigned_architect'] = self.instance.assigned_architect or ''
            self.initial['project_name'] = self.instance.project_name or ''
            self.initial['project_start'] = self.instance.project_start or ''
            
            # Set widget values for profile fields
            self.fields['phone'].widget.attrs['value'] = self.instance.phone or ''
            self.fields['assigned_architect'].widget.attrs['value'] = self.instance.assigned_architect or ''
            self.fields['project_name'].widget.attrs['value'] = self.instance.project_name or ''
        else:
            print(f"[DEBUG] FORM - No profile instance or new profile")
    
    def save(self, user=None, commit=True):
        profile = super().save(commit=False)
        if user:
            # Security check: Ensure we're only updating the correct user's profile
            if profile.user != user:
                raise ValueError(f"Profile user mismatch! Profile belongs to {profile.user}, but trying to save for {user}")
            
            # Update User model fields
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
            
            # Ensure profile is linked to the correct user (double-check)
            profile.user = user
            if commit:
                profile.save()
                print(f"[DEBUG] Profile saved for user: {user.username} (ID: {user.id})")
                if profile.profile_pic:
                    print(f"[DEBUG] Profile picture saved: {profile.profile_pic.url}")
                else:
                    print(f"[DEBUG] No profile picture uploaded")
        return profile


# Admin Authentication Forms
class AdminRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'id': 'firstName'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'id': 'lastName'
        })
    )
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'id': 'terms'
        }),
        error_messages={'required': 'You must agree to the Terms of Service and Privacy Policy.'}
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
            'id': 'password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'confirmPassword'
        })
        
        # Remove username field (we'll use email as username)
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Inactive until admin approval
        user.is_staff = True    # Mark as staff for admin access
        if commit:
            user.save()
        return user


class AdminLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'password'
        })
    )
    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'id': 'remember'
        })
    )


class AdminOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        required=True,
        label="Verification Code",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'class': 'form-control',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'autocomplete': 'one-time-code'
        })
    )
    
    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("Please enter a valid 6-digit code.")
        return otp