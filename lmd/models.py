from django.db import models
from django.contrib.auth.models import User

from core.models import Classe, Filiere, Niveau, Etudiant


# =====================
# UE (Unité d’Enseignement)
# =====================
class UE(models.Model):
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    credit = models.IntegerField()

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name="ues"
    )

    semestre = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.code} - {self.libelle}"


# =====================
# ECUE (Élément Constitutif d’UE)
# =====================
class ECUE(models.Model):
    ue = models.ForeignKey(
        UE,
        on_delete=models.CASCADE,
        related_name='ecues'
    )

    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=200)
    coefficient = models.IntegerField(default=1)
    credit = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.code} - {self.libelle}"


# =====================

class NoteLMD(models.Model):

    etudiant = models.ForeignKey(
        "EtudiantLMD",
        on_delete=models.CASCADE,
        related_name="notes_lmd"
    )

    ecue = models.ForeignKey(
        "ECUE",
        on_delete=models.CASCADE,
        related_name="notes"
    )

    cc = models.FloatField(default=0)
    examen = models.FloatField(default=0)

    moyenne = models.FloatField(blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.moyenne = round(
            (float(self.cc) * 0.4) + (float(self.examen) * 0.6),
            2
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.etudiant} - {self.ecue} ({self.moyenne})"

# =====================
# ÉTUDIANT LMD (structure académique)
# =====================

class EtudiantLMD(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    matricule = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)

    sexe = models.CharField(
        max_length=1,
        choices=(
            ('M', 'Masculin'),
            ('F', 'Féminin'),
        )
    )

    date_naissance = models.DateField(null=True, blank=True)

    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    # 🎓 Structure LMD
    NIVEAUX = [
        ("L1", "Licence 1"),
        ("L2", "Licence 2"),
        ("M1", "Master 1"),
        ("M2", "Master 2"),
        ("DOC", "Doctorat"),
    ]

    niveau = models.CharField(
        max_length=10,
        choices=NIVEAUX
    )

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name="etudiants_lmd"
    )

    annee_academique = models.CharField(max_length=20)

    date_inscription = models.DateTimeField(auto_now_add=True)

    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenoms}"

from django.db import models


class NiveauLMD(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True
    )

    libelle = models.CharField(
        max_length=100
    )

    ordre = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["ordre"]

    def __str__(self):
        return self.libelle

from django.db import models


class ClasseLMD(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    libelle = models.CharField(
        max_length=100
    )

    niveau = models.ForeignKey(
        "NiveauLMD",
        on_delete=models.PROTECT,
        related_name="classes"
    )

    filiere = models.ForeignKey(
        "FiliereLMD",
        on_delete=models.PROTECT,
        related_name="classes"
    )

    class Meta:
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle

class FiliereLMD(models.Model):
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        return self.libelle


# class InscriptionUE(models.Model):
#     etudiant = models.ForeignKey("EtudiantLMD", on_delete=models.CASCADE)
#     ue = models.ForeignKey("UE", on_delete=models.CASCADE)
#     annee_academique = models.CharField(max_length=20)