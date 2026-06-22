from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Etudiant,
    Classe,
    Matiere,
    Note,
    AffectationMatiere
)

# =========================
# USER REGISTER FORM
# =========================
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


# =========================
# CLASSE FORM
# =========================
class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

# =========================
# MATIERE FORM
# =========================
class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })


# =========================
# ETUDIANT FORM
# =========================
class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = [
            "matricule",
            "nom",
            "prenoms",
            "date_naissance",
            "sexe",
            "telephone",
            "email",
            "classe"
        ]


# =========================
# AFFECTATION FORM
# =========================
class AffectationForm(forms.ModelForm):
    class Meta:
        model = AffectationMatiere
        fields = "__all__"


# =========================
# NOTE FORM
# =========================
from django import forms
from .models import Note

class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })