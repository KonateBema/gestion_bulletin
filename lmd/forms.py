from django import forms
from .models import EtudiantLMD


class EtudiantLMDForm(forms.ModelForm):

    class Meta:
        model = EtudiantLMD
        fields = [
            "matricule",
            "nom",
            "prenoms",
            "sexe",
            "telephone",
            "filiere",
            "annee_academique",
        ]