from .models import Note, Etudiant
from django.db.models import Avg

def calcul_moyenne_etudiant1(etudiant):

    notes = Note.objects.filter(etudiant=etudiant)

    if not notes.exists():
        return 0

    total = 0

    for n in notes:
        moyenne_matiere = (n.devoir + n.examen) / 2
        total += moyenne_matiere

    return total / notes.count()

def calcul_moyenne_etudiant(etudiant):

    notes = Note.objects.filter(etudiant=etudiant)

    if not notes.exists():
        return 0

    total_points = 0
    total_coef = 0

    for note in notes:

        coef = note.matiere.coefficient

        total_points += note.moyenne * coef
        total_coef += coef

    if total_coef == 0:
        return 0

    return round(total_points / total_coef, 2)



def moyenne_classe(classe):
    etudiants = Etudiant.objects.filter(classe=classe)

    moyennes = []

    for e in etudiants:
        moyennes.append(calcul_moyenne_etudiant(e))

    if len(moyennes) == 0:
        return 0

    return round(sum(moyennes) / len(moyennes), 2)

def classement_classe(classe):
    etudiants = Etudiant.objects.filter(classe=classe)

    data = []

    for e in etudiants:
        moyenne = calcul_moyenne_etudiant(e)
        data.append({
            "etudiant": e,
            "moyenne": moyenne
        })

    # tri décroissant
    data = sorted(data, key=lambda x: x["moyenne"], reverse=True)

    # attribution rang
    for index, item in enumerate(data, start=1):
        item["rang"] = index

    return data


def mention(moyenne):
    if moyenne < 10:
        return "Échec ❌"
    elif moyenne < 12:
        return "Passable"
    elif moyenne < 14:
        return "Assez bien"
    elif moyenne < 16:
        return "Bien"
    else:
        return "Très bien ⭐"


def obtenir_rang(etudiant):

    classe = etudiant.classe

    classement = classement_classe(classe)

    for item in classement:
        if item["etudiant"].id == etudiant.id:
            return item["rang"]

    return "-"