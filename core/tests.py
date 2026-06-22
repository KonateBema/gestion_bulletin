from django.test import TestCase

# Create your tests here.
def moyenne_matiere(etudiant, matiere):
    notes = Note.objects.filter(etudiant=etudiant, matiere=matiere)

    total = sum(n.valeur for n in notes)
    return total / len(notes) if notes else 0

def moyenne_generale(etudiant):
    matieres = Matiere.objects.all()

    total = 0
    coef_total = 0

    for matiere in matieres:
        moyenne = moyenne_matiere(etudiant, matiere)
        coef = matiere.coefficient

        total += moyenne * coef
        coef_total += coef

    return total / coef_total if coef_total else 0

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
        return "Échec"