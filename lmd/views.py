from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
# from .models import ECUE, UE
# from .pdf_service_ue import bulletin_lmd_pdf
import os
from django.conf import settings
from django.http import FileResponse
from .pdf_service_ue import generate_bulletin_lmd_pdf
from .forms import EtudiantLMDForm
from django.db.models import Sum
from .pdf_service_ue import generate_bulletin_lmd_pdf
from django.core.paginator import Paginator

def niveau_list(request):
    niveaux = Niveau.objects.all()
    return render(request, "lmd/niveaux/list.html", {"niveaux": niveaux})


def niveau_add(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        Niveau.objects.create(nom=nom)
        return redirect("niveau_lmd_list")

    return render(request, "lmd/niveaux/add.html")

def filiere_list(request):
    filieres = Filiere.objects.all()
    return render(request, "lmd/filieres/list.html", {"filieres": filieres})


def filiere_add(request):
    if request.method == "POST":
        Filiere.objects.create(
            nom=request.POST.get("nom")
        )
    return redirect("filiere_lmd_list")

# UPDATE
def filiere_edit(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)

    if request.method == "POST":
        filiere.nom = request.POST.get("nom")
        filiere.save()
        return redirect("filiere_lmd_list")

    return render(request, "lmd/filieres/edit.html", {
        "filiere": filiere
    })


def filiere_delete(request, pk):
    filiere = Filiere.objects.get(pk=pk)

    if request.method == "POST":
        filiere.delete()
        return redirect("filiere_lmd_list")

    return redirect("filiere_lmd_list")



def classe_list(request):
    classes = Classe.objects.all()
    return render(request, "lmd/classes/list.html", {
        "classes": classes
    })


def classe_add(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        niveau=request.POST.get("niveau"),
        filiere_id = request.POST.get("filiere")

        Classe.objects.create(
            nom=nom,
            niveau=request.POST.get("niveau"),   # 🔥 IMPORTANT
            filiere_id=filiere_id
        )
        return redirect("classe_lmd_list")

    return render(request, "lmd/classes/add.html", {
        "niveaux": Niveau.objects.all(),
        "filieres": Filiere.objects.all()
    })


def ue_list(request):

    ues = UE.objects.select_related(
        "filiere"
    ).order_by(
        "filiere__nom",
        "semestre",
        "code"
    )

    return render(
        request,
        "lmd/ue/list.html",
        {
            "ues": ues
        }
    )


def ue_add(request):

    if request.method == "POST":

        UE.objects.create(
            code=request.POST.get("code"),
            libelle=request.POST.get("libelle"),
            credit=request.POST.get("credit"),
            filiere_id=request.POST.get("filiere"),
            semestre=request.POST.get("semestre")
        )

        return redirect("ue_list")

    return render(
        request,
        "lmd/ue/add.html",
        {
            "filieres": Filiere.objects.all()
        }
    )


def ue_edit(request, pk):

    ue = UE.objects.get(pk=pk)

    if request.method == "POST":

        ue.code = request.POST.get("code")
        ue.libelle = request.POST.get("libelle")
        ue.credit = request.POST.get("credit")
        ue.filiere_id = request.POST.get("filiere")
        ue.semestre = request.POST.get("semestre")

        ue.save()

        return redirect("ue_list")

    return render(
        request,
        "lmd/ue/edit.html",
        {
            "ue": ue,
            "filieres": Filiere.objects.all()
        }
    )

def ue_delete(request, pk):

    ue = UE.objects.get(pk=pk)

    if request.method == "POST":
        ue.delete()
        return redirect("ue_list")

    return render(
        request,
        "lmd/ue/delete.html",
        {
            "ue": ue
        }
    )


# =====================
# LISTE + FILTRE
# =====================
def ecue_list(request):

    ue_id = request.GET.get("ue")

    ecues = ECUE.objects.select_related("ue").all()

    if ue_id:
        ecues = ecues.filter(ue_id=ue_id)

    total_credits = ecues.aggregate(
     total=Sum("credit")
     )["total"] or 0

    return render(request, "lmd/ecue/list.html", {
        "ecues": ecues,
        "ues": UE.objects.all(),
        "ue_selected": ue_id,
        "total_credits": total_credits,
    })


# =====================
# CREATE
# =====================
def ecue_add(request):

    if request.method == "POST":

        ECUE.objects.create(
            ue_id=request.POST.get("ue"),
            code=request.POST.get("code"),
            libelle=request.POST.get("libelle"),
            coefficient=request.POST.get("coefficient"),
            credit=request.POST.get("credit")
        )

        return redirect("ecue_list")

    return render(request, "lmd/ecue/add.html", {
        "ues": UE.objects.all()
    })


# =====================
# UPDATE
# =====================
def ecue_edit(request, pk):

    ecue = get_object_or_404(ECUE, pk=pk)

    if request.method == "POST":

        ecue.ue_id = request.POST.get("ue")
        ecue.code = request.POST.get("code")
        ecue.libelle = request.POST.get("libelle")
        ecue.coefficient = request.POST.get("coefficient")
        ecue.credit = request.POST.get("credit")

        ecue.save()

        return redirect("ecue_list")

    return render(request, "lmd/ecue/edit.html", {
        "ecue": ecue,
        "ues": UE.objects.all()
    })


# =====================
# DELETE
# =====================
def ecue_delete(request, pk):

    ecue = get_object_or_404(ECUE, pk=pk)

    if request.method == "POST":
        ecue.delete()
        return redirect("ecue_list")

    return render(request, "lmd/ecue/delete.html", {
        "ecue": ecue
    })


from django.db.models import Q
from .models import NoteLMD, EtudiantLMD, ECUE


def note_lmd_list(request):

    notes = NoteLMD.objects.select_related(
        "etudiant",
        "ecue"
    )

    etudiant = request.GET.get("etudiant")
    ecue = request.GET.get("ecue")

    if etudiant:
        notes = notes.filter(
            Q(etudiant__nom__icontains=etudiant) |
            Q(etudiant__prenoms__icontains=etudiant) |
            Q(etudiant__matricule__icontains=etudiant)
        )

    if ecue:
        notes = notes.filter(ecue__code__icontains=ecue)

    return render(request, "lmd/notes/list.html", {
        "notes": notes,
        "ecues": ECUE.objects.all(),
    })

def note_lmd_add(request):

    if request.method == "POST":

        NoteLMD.objects.create(
            etudiant_id=request.POST.get("etudiant"),
            ecue_id=request.POST.get("ecue"),
            cc=request.POST.get("cc"),
            examen=request.POST.get("examen"),
        )

        return redirect("note_lmd_list")

    return render(request, "lmd/notes/form.html", {
        "etudiants": EtudiantLMD.objects.all(),
        "ecues": ECUE.objects.all(),
    })


def note_lmd_edit(request, pk):

    note = NoteLMD.objects.get(pk=pk)

    if request.method == "POST":

        note.etudiant_id = request.POST.get("etudiant")
        note.ecue_id = request.POST.get("ecue")
        note.cc = request.POST.get("cc")
        note.examen = request.POST.get("examen")

        note.save()
        return redirect("note_lmd_list")

    return render(request, "lmd/notes/form.html", {
        "note": note,
        "etudiants": EtudiantLMD.objects.all(),
        "ecues": ECUE.objects.all(),
    })

def note_lmd_delete(request, pk):

    note = NoteLMD.objects.get(pk=pk)
    note.delete()

    return redirect("note_lmd_list")

from .models import EtudiantLMD

from django.db.models import Q

def bulletin_lmd_listDD(request):

    classes = ClasseLMD.objects.select_related('filiere')

    matricule = request.GET.get("matricule")
    nom = request.GET.get("nom")
    telephone = request.GET.get("telephone")
    niveau = request.GET.get("niveau")
    classe = request.GET.get("classe")

    if matricule:
        etudiants = etudiants.filter(matricule__icontains=matricule)

    if nom:
        etudiants = etudiants.filter(
            Q(nom__icontains=nom) |
            Q(prenoms__icontains=nom)
        )

    if telephone:
        etudiants = etudiants.filter(
            telephone__icontains=telephone
        )

    if niveau:
        etudiants = etudiants.filter(
            niveau=request.POST.get("niveau"),   # 🔥 IMPORTANT
        )

    if classe:
        etudiants = etudiants.filter(
            classe_id=classe
        )

    return render(
        request,
        "lmd/bulletins/list.html",
        {
            "etudiants": etudiants,
            "niveaux": NiveauLMD.objects.all(),
            "classes": ClasseLMD.objects.all(),
        }
    )

from django.db.models import Q

def bulletin_lmd_list(request):

    matricule = request.GET.get("matricule")
    nom = request.GET.get("nom")
    telephone = request.GET.get("telephone")
    niveau = request.GET.get("niveau")
    classe = request.GET.get("classe")

    # Charger tous les étudiants au départ
    etudiants = EtudiantLMD.objects.select_related(
        "niveau",
        "classe"
    ).all()

    if matricule:
        etudiants = etudiants.filter(
            matricule__icontains=matricule
        )

    if nom:
        etudiants = etudiants.filter(
            Q(nom__icontains=nom) |
            Q(prenoms__icontains=nom)
        )

    if telephone:
        etudiants = etudiants.filter(
            telephone__icontains=telephone
        )

    if niveau:
        etudiants = etudiants.filter(
            niveau_id=niveau
        )

    if classe:
        etudiants = etudiants.filter(
            classe_id=classe
        )

    return render(
        request,
        "lmd/bulletins/list.html",
        {
            "etudiants": etudiants,
            "niveaux": NiveauLMD.objects.all(),
            "classes": ClasseLMD.objects.select_related("filiere"),
            "matricule": matricule,
            "nom": nom,
            "telephone": telephone,
            "niveau_selected": niveau,
            "classe_selected": classe,
        }
    )

from django.db.models import Q
def bulletin_lmd_list(request):

    etudiants = EtudiantLMD.objects.select_related(
        "user",
        "filiere"
    )

    matricule = request.GET.get("matricule")
    nom = request.GET.get("nom")
    telephone = request.GET.get("telephone")
    classe = request.GET.get("classe")

    if matricule:
        etudiants = etudiants.filter(matricule__icontains=matricule)

    if nom:
        etudiants = etudiants.filter(
            Q(nom__icontains=nom) |
            Q(prenoms__icontains=nom)
        )

    if telephone:
        etudiants = etudiants.filter(telephone__icontains=telephone)

    if classe:
        etudiants = etudiants.filter(classe_id=classe)

    return render(request, "lmd/bulletins/list.html", {
        "etudiants": etudiants,
        "classes": ClasseLMD.objects.select_related("filiere"),
    })

def bulletin_lmd_list(request):

    matricule = request.GET.get("matricule")
    nom = request.GET.get("nom")
    telephone = request.GET.get("telephone")
    classe = request.GET.get("classe")

    etudiants = EtudiantLMD.objects.select_related(
        "user",
        "filiere"
    ).all()

    if matricule:
        etudiants = etudiants.filter(matricule__icontains=matricule)

    if nom:
        etudiants = etudiants.filter(
            Q(nom__icontains=nom) |
            Q(prenoms__icontains=nom)
        )

    if telephone:
        etudiants = etudiants.filter(telephone__icontains=telephone)

    if classe:
        etudiants = etudiants.filter(classe_id=classe)

    return render(request, "lmd/bulletins/list.html", {
        "etudiants": etudiants,
        "classes": ClasseLMD.objects.select_related("filiere"),
    })


def etudiant_lmd_add(request):

    if request.method == "POST":

        etudiant = EtudiantLMD.objects.create(
            matricule=request.POST.get("matricule"),
            nom=request.POST.get("nom"),
            prenoms=request.POST.get("prenoms"),
            sexe=request.POST.get("sexe"),
            date_naissance=request.POST.get("date_naissance"),
            telephone=request.POST.get("telephone"),
            email=request.POST.get("email"),
            niveau=request.POST.get("niveau"),   # 🔥 IMPORTANT
            filiere_id=request.POST.get("filiere"),
            annee_academique=request.POST.get("annee_academique"),
        )

        # 🔥 UE automatique selon filière
        ues = UE.objects.filter(filiere=etudiant.filiere)

        return redirect("etudiant_lmd_list")

    return render(request, "lmd/etudiants/add.html", {
        "niveaux": Niveau.objects.all(),
        "filieres": Filiere.objects.all(),
        "ues": UE.objects.all(),
        "ecues": ECUE.objects.all(),
    })

def calcul_moyenne_ecue(note):
    if not note:
        return 0

    cc = note.cc or 0
    examen = note.examen or 0

    return round((cc * 0.4) + (examen * 0.6), 2)

def calcul_moyenne_ue(etudiant, ue):

    ecues = ue.ecues.all()

    notes = NoteLMD.objects.filter(
        etudiant=etudiant,
        ecue__ue=ue
    )

    total = 0
    count = 0

    for note in notes:
        total += calcul_moyenne_ecue(note)
        count += 1

    if count == 0:
        return 0

    return round(total / count, 2)
def ue_validee(moyenne_ue):
    return moyenne_ue >= 10

def etudiant_lmd_editDDD(request, pk):
    etudiant = EtudiantLMD.objects.get(pk=pk)
    return render(request, "lmd/etudiants/edit.html", {"etudiant": etudiant})


def etudiant_lmd_delete(request, pk):
    etudiant = get_object_or_404(EtudiantLMD, pk=pk)

    if request.method == "POST":
        etudiant.delete()

    return redirect("etudiant_lmd_list")

def etudiant_lmd_update(request, pk):
    etudiant = get_object_or_404(EtudiantLMD, pk=pk)

    if request.method == "POST":
        etudiant.matricule = request.POST.get("matricule")
        etudiant.nom = request.POST.get("nom")
        etudiant.prenoms = request.POST.get("prenoms")
        etudiant.telephone = request.POST.get("telephone")
        etudiant.sexe = request.POST.get("sexe")
        etudiant.annee_academique = request.POST.get("annee_academique")

        etudiant.save()

    return redirect("etudiant_lmd_list")


def resultat_ue(request, etudiant_id):

    from .models import EtudiantLMD, UE

    etudiant = EtudiantLMD.objects.get(id=etudiant_id)
    ues = UE.objects.all()

    resultats = []

    for ue in ues:
        moyenne = calcul_moyenne_ue(etudiant, ue)

        resultats.append({
            "ue": ue,
            "moyenne": moyenne,
            "statut": statut_ue(moyenne)
        })

    return render(request, "lmd/resultats_ue.html", {
        "etudiant": etudiant,
        "resultats": resultats
    })



def bulletin_lmd_pdf(request, etudiant_id):

    file_path = os.path.join(
        settings.BASE_DIR,
        f"bulletin_{etudiant_id}.pdf"
    )

    generate_bulletin_lmd_pdf(etudiant_id, file_path)

    return FileResponse(open(file_path, "rb"))

def etudiant_lmd_listSSS(request):

    etudiants = EtudiantLMD.objects.select_related(
        "user",
        "filiere"
    )

    matricule = request.GET.get("matricule")
    nom = request.GET.get("nom")
    telephone = request.GET.get("telephone")
    ue = request.GET.get("ue")

    if matricule:
        etudiants = etudiants.filter(matricule__icontains=matricule)

    if nom:
        etudiants = etudiants.filter(
            Q(nom__icontains=nom) |
            Q(prenoms__icontains=nom)
        )

    if telephone:
        etudiants = etudiants.filter(telephone__icontains=telephone)

    if ue:
        etudiants = etudiants.filter(note_lmd__ecue__code__icontains=ue)

    return render(request, "lmd/etudiants/list.html", {
        "etudiantslmd": etudiants
    })


def etudiant_lmd_list(request):

    etudiants = EtudiantLMD.objects.select_related(
        "user",
        "filiere"
    )

    matricule = request.GET.get("matricule")
    nom = request.GET.get("nom")
    telephone = request.GET.get("telephone")
    ue = request.GET.get("ue")

    if matricule:
        etudiants = etudiants.filter(
            matricule__icontains=matricule
        )

    if nom:
        etudiants = etudiants.filter(
            Q(nom__icontains=nom) |
            Q(prenoms__icontains=nom)
        )

    if telephone:
        etudiants = etudiants.filter(
            telephone__icontains=telephone
        )

    if ue:
        etudiants = etudiants.filter(
            note_lmd__ecue__code__icontains=ue
        ).distinct()

    # Trier les étudiants
    etudiants = etudiants.order_by("nom")

    # Pagination (10 étudiants par page)
    paginator = Paginator(etudiants, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "lmd/etudiants/list.html", {
        "page_obj": page_obj,
    })


