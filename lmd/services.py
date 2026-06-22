from .models import NoteLMD

def calcul_moyenne_ue(etudiant, ue):

    notes = NoteLMD.objects.filter(
        etudiant=etudiant,
        ecue__ue=ue
    )

    total_points = 0
    total_coef = 0

    for note in notes:
        coef = note.ecue.coefficient
        total_points += note.moyenne * coef
        total_coef += coef

    if total_coef == 0:
        return 0

    return round(total_points / total_coef, 2)

def statut_ue(moyenne):
    return "VALIDÉE" if moyenne >= 10 else "NON VALIDÉE"