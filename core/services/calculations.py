def calcul_moyenne(notes):
    if not notes:
        return 0
    return sum(n.moyenne for n in notes) / len(notes)


def mention(moyenne):
    if moyenne >= 16:
        return "Très Bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez Bien"
    elif moyenne >= 10:
        return "Passable"
    return "Insuffisant"

def classement(classe):
    etudiants = classe.etudiant_set.all()

    data = []
    for e in etudiants:
        moyenne = calcul_moyenne(e.note_set.all())
        data.append((e, moyenne))

    data.sort(key=lambda x: x[1], reverse=True)

    result = []
    rang = 1

    for etudiant, moyenne in data:
        result.append({
            "etudiant": etudiant,
            "moyenne": moyenne,
            "rang": rang
        })
        rang += 1

    return result