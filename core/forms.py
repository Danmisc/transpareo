from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
#from captcha.fields import ReCaptchaField
#from captcha.widgets import ReCaptchaV2Checkbox
from phonenumber_field.formfields import PhoneNumberField
import re

User = get_user_model()


class SignupForm(UserCreationForm):
    """Formulaire d'inscription avancé"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com',
            'autocomplete': 'email'
        })
    )
    
    username = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur',
            'autocomplete': 'username'
        })
    )
    
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum 8 caractères',
            'autocomplete': 'new-password',
            'id': 'password1'
        })
    )
    
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Retapez votre mot de passe',
            'autocomplete': 'new-password'
        })
    )
    
    phone_number = PhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+33 6 12 34 56 78 (optionnel)',
            'autocomplete': 'tel'
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="J'accepte les conditions d'utilisation et la politique de confidentialité"
    )
    
    newsletter = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Je souhaite recevoir la newsletter"
    )
    
    #captcha = ReCaptchaField(
     #   widget=ReCaptchaV2Checkbox(attrs={
      #      'data-theme': 'light',
       # })
    #)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2', 'phone_number']
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres et @/./+/-/_")
        return username
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        # Vérifications personnalisées
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        
        if not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        
        return password
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.newsletter_subscribed = self.cleaned_data.get('newsletter', False)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Formulaire de connexion"""
    
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe',
            'autocomplete': 'current-password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Se souvenir de moi"
    )


class PasswordResetRequestForm(forms.Form):
    """Formulaire de demande de réinitialisation"""
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com',
            'autocomplete': 'email'
        })
    )
    
    #captcha = ReCaptchaField(
     #   widget=ReCaptchaV2Checkbox()
    #)


class PasswordResetForm(forms.Form):
    """Formulaire de réinitialisation du mot de passe"""
    
    password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum 8 caractères',
            'id': 'password1'
        })
    )
    
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Retapez votre mot de passe'
        })
    )
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        
        if not re.search(r'\d', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'bio', 'date_of_birth', 
                  'avatar', 'newsletter_subscribed', 'notifications_enabled']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'newsletter_subscribed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notifications_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
