from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from . import models
from django import forms
from .models import Capteur


class CapteurForm(ModelForm):
    class Meta:
        model = models.Capteur
        fields = ('nom_capteur', 'pieces')
        labels = {
            'nom_capteur': _('Nom du capteur'),
            'pieces': _('Emplacement'),
        
        }


class DonneeForm(ModelForm):
    class Meta:
        model = models.Donnée
        fields = ('id_capteur', 'timestamp', 'temperature')



    
class DonneeFilterForm(forms.Form):
    maison = forms.CharField(max_length=100, required=False, label='Maison')
    capteur = forms.ModelChoiceField(queryset=Capteur.objects.all(), required=False, label='Capteur')
    pieces = forms.CharField(max_length=100, required=False, label='Emplacement')
    date_start = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False, label='Date start')
    date_end = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False, label='Date end')
    
    