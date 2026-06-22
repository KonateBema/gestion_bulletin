import os
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet


def generate_bulletin_pdf(etudiant, notes, moyenne, rang, mention,
                          logo_path=None, cachet_path=None):

    output_dir = os.path.join(settings.BASE_DIR, "media")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"bulletin_{etudiant.id}.pdf")

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    # 🖼 LOGO
    if logo_path and os.path.exists(logo_path):
        elements.append(RLImage(logo_path, width=80, height=80))

    # 👤 INFOS ETUDIANT
    elements.append(Paragraph(f"Nom: {etudiant.user.username}", styles["Title"]))
    elements.append(Paragraph(f"Matricule: {etudiant.matricule}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # 📊 RESULTATS
    elements.append(Paragraph(f"Moyenne: {moyenne:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Rang: {rang}", styles["Normal"]))
    elements.append(Paragraph(f"Mention: {mention}", styles["Normal"]))

    # 🏷 CACHET
    if cachet_path and os.path.exists(cachet_path):
        elements.append(Spacer(1, 20))
        elements.append(RLImage(cachet_path, width=120, height=120))

    doc.build(elements)

    return file_path