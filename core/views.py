# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_protect
from .forms import EtudiantForm,ClasseForm,MatiereForm,AffectationForm,NoteForm
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Filiere
import os
from .services import calcul_moyenne_etudiant
from django.conf import settings

from .models import (
    Etudiant, Professeur, Classe, Matiere, Note,
    AffectationMatiere, Inscription, Profile
)

from .forms import UserRegisterForm
from .utils import generate_matricule
from .services import (
    calcul_moyenne_etudiant,
    classement_classe,
    mention,
    moyenne_classe
)
from .pdf_service import generate_bulletin_pdf


# =========================
# 🔐 LOGIN
# =========================
@csrf_protect
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile = Profile.objects.filter(user=user).first()

            if not profile:
                return render(request, "login.html", {
                    "error": "Profil utilisateur introuvable"
                })

            if profile.role == "ADMIN":
                return redirect("dashboard_admin")

            elif profile.role == "PROF":
                return redirect("dashboard_prof")

            else:
                return redirect("dashboard_etudiant")

        return render(request, "login.html", {
            "error": "Identifiants incorrects"
        })

    return render(request, "login.html")


# =========================
# 🚪 LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# 🏠 HOME / DASHBOARD GLOBAL
# =========================
@login_required
def dashboard(request):

    return render(request, "dashboard.html", {
        "etudiants_count": Etudiant.objects.count(),
        "professeurs_count": Professeur.objects.count(),
        "classes_count": Classe.objects.count(),
        "matieres_count": Matiere.objects.count(),
        "notes_count": Note.objects.count(),
    })


# =========================
# 🧑‍💼 ADMIN
# =========================
@login_required
def dashboard_admin(request):

    return render(request, "admin_dashboard.html", {
        "etudiants": Etudiant.objects.count(),
        "professeurs": Professeur.objects.count(),
        "classes": Classe.objects.count(),
    })


# =========================
# 👨‍🏫 PROF
# =========================
@login_required
def dashboard_prof(request):

    prof = Professeur.objects.filter(user=request.user).first()

    if not prof:
        return HttpResponse("❌ Profil professeur introuvable")

    matieres = AffectationMatiere.objects.filter(professeur=prof)

    return render(request, "prof_dashboard.html", {
        "matieres": matieres,
    })


# =========================
# 🎓 ETUDIANT
# =========================
@login_required
def dashboard_etudiant(request):

    etudiant = Etudiant.objects.filter(user=request.user).first()

    if not etudiant:
        return HttpResponse("❌ Aucun profil étudiant trouvé")

    notes = Note.objects.filter(etudiant=etudiant)

    return render(request, "etudiant_dashboard.html", {
        "etudiant": etudiant,
        "notes": notes,
    })


# =========================
# 📝 INSCRIPTION UTILISATEUR
# =========================
def register_user(request):

    if request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            # 🎓 ETUDIANT
            if user.role == "ETUD":

                etudiant = Etudiant.objects.create(
                    user=user,
                    matricule=generate_matricule("ETU"),
                    date_naissance="2000-01-01",
                    sexe="M",
                    telephone="00000000",
                    classe=Classe.objects.first()
                )

                Inscription.objects.create(
                    etudiant=etudiant,
                    classe=etudiant.classe,
                    annee="2025-2026"
                )

            # 👨‍🏫 PROF
            elif user.role == "PROF":

                Professeur.objects.create(
                    user=user,
                    matricule=generate_matricule("PROF"),
                    specialite="Non définie",
                    telephone="00000000"
                )

            return redirect('login')

    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

# =========================
# 📊 BULLETIN ETUDIANT
# =========================
@login_required
def bulletin_etudiant(request):

    etudiant = Etudiant.objects.first()  # ou filtre propre

    if not etudiant:
        return HttpResponse("Aucun étudiant trouvé")

    moyenne = calcul_moyenne_etudiant(etudiant)

    return render(request, "bulletin.html", {
        "etudiant": etudiant,
        "moyenne": moyenne,
        "mention": mention(moyenne),
    })

# =========================
# 🏫 BULLETIN CLASSE
# =========================
# @login_required
# def bulletin_classe(request, classe_id):

#     classe = Classe.objects.get(id=classe_id)

#     classement = classement_classe(classe)
#     moyenne_classe_val = moyenne_classe(classe)

#     return render(request, "bulletin_classe.html", {
#         "classe": classe,
#         "classement": classement,
#         "moyenne_classe": moyenne_classe_val,
#     })

# =========================
# 📄 PDF BULLETIN
# =========================

# @login_required
# def download_bulletin_pdf(request):

#     # ⚠️ ton modèle n’a pas user → on prend un étudiant (exemple simple)
#     etudiant = Etudiant.objects.first()

#     if not etudiant:
#         return HttpResponse("Aucun étudiant trouvé")

#     file_path = generate_bulletin_pdf(etudiant)

#     return FileResponse(open(file_path, "rb"), as_attachment=True)


# def download_bulletin_pdf(request):

#     etudiant = Etudiant.objects.first()

#     if not etudiant:
#         return HttpResponse("Aucun étudiant trouvé")

#     file_path = generate_bulletin_pdf(
#         etudiant,
#         logo_path="static/images/logo.png",
#         cachet_path="static/images/cachet.png"
#     )

#     return FileResponse(open(file_path, "rb"), as_attachment=True)

def etudiant_list(request):
    query = request.GET.get("q")
    classe_id = request.GET.get("classe")
    etudiants = Etudiant.objects.select_related("classe").all()
    # 🔎 SEARCH
    if query:
        etudiants = etudiants.filter(
            Q(matricule__icontains=query) |
            Q(user__username__icontains=query) |
            Q(prenoms__icontains=query) |
            Q(nom__icontains=query)
        )

    # 🎯 FILTER
    if classe_id:
        etudiants = etudiants.filter(classe_id=classe_id)

    # 📄 PAGINATION
    paginator = Paginator(etudiants, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "etudiants/list.html", {
        "page_obj": page_obj,
        "classes": Classe.objects.all()
    })

def etudiant_create(request):
    form = EtudiantForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("etudiant_list")
    return render(request, "etudiants/form.html", {"form": form})


def etudiant_update(request, id):
    etudiant = Etudiant.objects.get(id=id)
    form = EtudiantForm(request.POST or None, instance=etudiant)
    if form.is_valid():
        form.save()
        return redirect("etudiant_list")
    return render(request, "etudiants/form.html", {"form": form})


def etudiant_delete(request, id):
    Etudiant.objects.get(id=id).delete()
    return redirect("etudiant_list")

def classe_list(request):

    # 🟢 CREATE (IMPORTANT)
    if request.method == "POST":
        form = ClasseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("classe_list")

    # 🟢 LIST
    query = request.GET.get("q")
    filiere = request.GET.get("filiere")
    niveau = request.GET.get("niveau")

    classes = Classe.objects.all().order_by("-id")

    if query:
        classes = classes.filter(nom__icontains=query)

    if filiere:
        classes = classes.filter(filiere__nom__icontains=filiere)

    if niveau:
        classes = classes.filter(niveau__nom__icontains=niveau)

    paginator = Paginator(classes, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    form = ClasseForm()

    return render(request, "classes/list.html", {
        "page_obj": page_obj,
        "form": form
    })

def classe_create(request):
    if request.method == "POST":
        form = ClasseForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('classe_list')
    else:
        form = ClasseForm()

    return render(request, 'classes/form.html', {
        'form': form
    })

# def matiere_list(request):
#     return render(request, "matieres/list.html", {
#         "matieres": Matiere.objects.all()
#     })

def matiere_list(request):
    query = request.GET.get("q")
    filiere = request.GET.get("filiere")

    matieres = Matiere.objects.all().order_by("-id")

    # 🔎 SEARCH
    if query:
        matieres = matieres.filter(
            Q(code__icontains=query) |
            Q(libelle__icontains=query)
        )

    # 🎯 FILTER
    if filiere:
        matieres = matieres.filter(filiere_id=filiere)

    # 📄 PAGINATION
    paginator = Paginator(matieres, 10)  # 10 par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "matieres/list.html", {
        "page_obj": page_obj,
        "filiere_list": Filiere.objects.all()
    })





def matiere_create(request):
    form = MatiereForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("matiere_list")
    return render(request, "matieres/form.html", {"form": form})


from .models import AffectationMatiere

from .forms import AffectationForm


def affectation_list(request):
    return render(request, "affectations/list.html", {
        "affectations": Affectation.objects.select_related(
            "professeur", "matiere", "classe"
        )
    })


def affectation_create(request):
    form = AffectationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("affectation_list")

    return render(request, "affectations/form.html", {
        "form": form,
        "title": "Affecter professeur"
    })


def affectation_delete(request, id):
    Affectation.objects.get(id=id).delete()
    return redirect("affectation_list")

from .models import Note
from .forms import NoteForm


def note_listAAA(request):
    notes = Note.objects.select_related("etudiant", "matiere").all()

    return render(request, "notes/list.html", {
        "notes": notes
    })

def note_listTO(request):
    notes = Note.objects.select_related(
        "etudiant",
        "matiere"
    ).all()

    etudiant_id = request.GET.get("etudiant")
    matiere_id = request.GET.get("matiere")
    semestre = request.GET.get("semestre")

    if etudiant_id:
        notes = notes.filter(etudiant_id=etudiant_id)

    if matiere_id:
        notes = notes.filter(matiere_id=matiere_id)

    if semestre:
        notes = notes.filter(semestre=semestre)

    return render(request, "notes/list.html", {
        "notes": notes,
        "etudiants": Etudiant.objects.all(),
        "matieres": Matiere.objects.all(),
        
    })

from django.core.paginator import Paginator

def note_list(request):

    notes = Note.objects.select_related(
        "etudiant",
        "matiere"
    ).all().order_by("-id")

    etudiant_id = request.GET.get("etudiant")
    matiere_id = request.GET.get("matiere")
    semestre = request.GET.get("semestre")

    if etudiant_id:
        notes = notes.filter(etudiant_id=etudiant_id)

    if matiere_id:
        notes = notes.filter(matiere_id=matiere_id)

    if semestre:
        notes = notes.filter(semestre=semestre)

    paginator = Paginator(notes, 10)  # 10 lignes par page

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "notes/list.html", {
        "notes": page_obj,
        "page_obj": page_obj,
        "etudiants": Etudiant.objects.all(),
        "matieres": Matiere.objects.all(),
    })

def note_create(request):

    form = NoteForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            note = form.save(commit=False)

            # DEBUG OPTIONNEL
            print("✔ Note enregistrée")

            note.save()
            return redirect("note_list")

        else:
            print(form.errors)

    return render(request, "notes/form.html", {
        "form": form,
        "title": "Ajouter note"
    })
    
def note_update(request, id):
    note = Note.objects.get(id=id)
    form = NoteForm(request.POST or None, instance=note)

    if form.is_valid():
        form.save()
        return redirect("note_list")

    return render(request, "notes/form.html", {
        "form": form,
        "title": "Modifier note"
    })


def note_delete(request, id):
    Note.objects.get(id=id).delete()
    return redirect("note_list")

def moyenne_etudiant(etudiant):
    notes = Note.objects.filter(etudiant=etudiant)

    if not notes:
        return 0

    total = sum(n.moyenne for n in notes)
    return total / notes.count()

def mention(moyenne):
    if moyenne >= 16:
        return "Très Bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez Bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Insuffisant"


def classe_edit(request, pk):
    classe = Classe.objects.get(pk=pk)
    form = ClasseForm(request.POST or None, instance=classe)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('classe_list')

    return render(request, 'classes/form.html', {
        'form': form
    })

def classe_delete(request, pk):
    classe = get_object_or_404(Classe, pk=pk)
    classe.delete()
    return redirect('classe_list')

def matiere_update(request, id):
    matiere = get_object_or_404(Matiere, id=id)
    form = MatiereForm(request.POST or None, instance=matiere)

    if form.is_valid():
        form.save()
        return redirect('matiere_list')

    return render(request, 'matieres/form.html', {'form': form})

def matiere_delete(request, id):
    matiere = get_object_or_404(Matiere, id=id)
    matiere.delete()
    return redirect('matiere_list')

from .pdf_service import generate_bulletin_pdf

from django.http import FileResponse, HttpResponse

from .models import Etudiant



def download_bulletin_pdfOOOO(request):

    # Récupérer un étudiant
    etudiant = Etudiant.objects.first()

    if not etudiant:
        return HttpResponse("Aucun étudiant trouvé.")

    # Génération du PDF
    file_path = generate_bulletin_pdf(etudiant)

    # Téléchargement du PDF
    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=f"bulletin_{etudiant.matricule}.pdf"
    )


from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponse
from .models import Etudiant, Classe
from .pdf_service import generate_bulletin_pdf


def download_bulletin_pdf(request, etudiant_id, classe_id):

    etudiant = Etudiant.objects.get(id=etudiant_id)
    classe = Classe.objects.get(id=classe_id)

    file_path = generate_bulletin_pdf(
        etudiant,
        classe
    )

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=f"bulletin_{etudiant.matricule}.pdf"
    )

def bulletin_classe(request, classe_id):

    classe = Classe.objects.get(id=classe_id)

    data = classement(classe)

    return render(request, "bulletin_classe.html", {
        "classe": classe,
        "data": data
    })

from .models import Etudiant

def bulletin_listQQ(request):
    etudiants = Etudiant.objects.select_related("classe").all()
    return render(request, "bulletins/list.html", {
        "etudiants": etudiants
    })



from django.core.paginator import Paginator
from .models import Etudiant, Classe

def bulletin_list(request):

    etudiants = Etudiant.objects.select_related("classe").all()

    # 🔎 Filtres GET
    matricule = request.GET.get("matricule")
    telephone = request.GET.get("telephone")
    filiere = request.GET.get("filiere")
    classe = request.GET.get("classe")

    # 🔽 Filtrage dynamique
    if matricule:
        etudiants = etudiants.filter(matricule__icontains=matricule)

    if telephone:
        etudiants = etudiants.filter(telephone__icontains=telephone)

    if filiere:
        etudiants = etudiants.filter(filiere__icontains=filiere)

    if classe:
        etudiants = etudiants.filter(classe_id=classe)

    # 📄 PAGINATION
    paginator = Paginator(etudiants, 10)  # 10 étudiants par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "bulletins/list.html", {
        "etudiants": page_obj,
        "page_obj": page_obj,
        "classes": Classe.objects.all(),
    })
 