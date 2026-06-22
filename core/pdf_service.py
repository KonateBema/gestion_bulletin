import os
from datetime import datetime

from django.conf import settings
from django.db.models import Min, Max, Avg

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image as RLImage
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Note
from .services import calcul_moyenne_etudiant, mention
from reportlab.platypus import Flowable
from reportlab.lib import colors


class RoundedBackground(Flowable):
    def __init__(self, width, height, radius=8, fillColor=colors.whitesmoke, strokeColor=colors.black):
        super().__init__()
        self.width = width
        self.height = height
        self.radius = radius
        self.fillColor = fillColor
        self.strokeColor = strokeColor

    def draw(self):
        self.canv.setFillColor(self.fillColor)
        self.canv.setStrokeColor(self.strokeColor)

        self.canv.roundRect(
            0, 0,
            self.width,
            self.height,
            self.radius,
            stroke=1,
            fill=1
        )

# =====================================================
# STYLES
# =====================================================
styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "TITLE",
    parent=styles["Heading1"],
    alignment=1,
    fontSize=15,
    textColor=colors.HexColor("#b30000"),
)

SMALL = ParagraphStyle(
    "SMALL",
    parent=styles["Normal"],
    fontSize=9,
    leading=11
)

# =====================================================
# UTILS
# =====================================================
def get_image(path, width, height, fallback):
    if os.path.exists(path):
        return RLImage(path, width=width, height=height)
    return Paragraph(fallback, SMALL)

def safe_round(value):
    try:
        return round(float(value), 2)
    except:
        return 0

def format_rang(r):
    if r == 1:
        return "1er"
    if r == 2:
        return "2e"
    if r == 3:
        return "3e"
    return f"{r}e" if r != "-" else "-"


# =====================================================
# GENERATION PDF
# =====================================================
def generate_bulletin_pdf(etudiant, classe):

    output_dir = os.path.join(settings.BASE_DIR, "media", "bulletins")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"bulletin_{etudiant.matricule}.pdf")

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm
    )

    elements = []

    # =====================================================
    # EN-TÊTE ÉTAT
    # =====================================================

    header_table = Table([
       [Paragraph("""
        <para align="left">
        <b>RÉPUBLIQUE DE CÔTE D'IVOIRE</b><br/>
        Union - Discipline - Travail
        </para>
    """, SMALL)]
  ], colWidths=[18*cm])

    header_table.setStyle(TableStyle([
       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
       ('LEFTPADDING', (0, 0), (-1, -1), 0),
       ('TOPPADDING', (0, 0), (-1, -1), 0),
   ]))

    elements.append(header_table)

    elements.append(Paragraph("""
        <para align="right">
        ANNÉE ACADÉMIQUE : 2025 - 2026
        </para>
    """, SMALL))

    elements.append(Spacer(1, 8))
    # =====================================================
    # LOGO
    # =====================================================
    logo = get_image(
        os.path.join(settings.BASE_DIR, "core/static/logo.jpeg"),
        1.6 * cm,
        1.6 * cm,
        "LOGO"
    )

    cachet = get_image(
        os.path.join(settings.BASE_DIR, "core/static/cachet.png"),
        2.5 * cm,
        2.5 * cm,
        "CACHET"
    )

    # =====================================================
    # CADRE UNIVERSITÉ
    # =====================================================
    cadre_universite = Table(
        [[
            logo,
            Paragraph("""
                <b>UNIVERSITÉ INTERNATIONALE DE COCODY</b><br/>
                BP Abidjan - Côte d'Ivoire<br/>
                Tel: +225 07 78 63 74 00<br/>
                Email: contact@uic.ci
                Email: contact@uic.ci
            """, SMALL)
        ]],
        colWidths=[2.5 * cm, 7.5 * cm],
        rowHeights=[3.7 * cm]
    )

    cadre_universite.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 effet arrondi
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    # =====================================================
    # CADRE ÉTUDIANT
    # =====================================================
    cadre_etudiant = Table(
        [
            ["Nom & Prénom", f"{etudiant.nom} {etudiant.prenoms}"],
            ["Matricule", etudiant.matricule],
            ["Sexe", getattr(etudiant, "sexe", "")],
            ["Classe", classe.nom],
            ["Filière", classe.nom],
            ["Redoublant", "NON"],
        ],
        colWidths=[3 * cm, 4.5 * cm]
    )

    cadre_etudiant.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 arrondi
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f7f7f7")),
    ]))

    # =====================================================
    # HEADER GLOBAL
    # =====================================================
    page_width = A4[0]
    usable_width = page_width - doc.leftMargin - doc.rightMargin

    header = Table(
        [[cadre_universite, cadre_etudiant]],
        colWidths=[
            usable_width * 0.58,
            usable_width * 0.42
        ]
    )

    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 12))

    # =====================================================
    # TITRE
    # =====================================================
    elements.append(Paragraph("BULLETIN DE NOTES - 1er SEMESTRE", TITLE))
    elements.append(Spacer(1, 10))

    # =====================================================
    # NOTES
    # =====================================================
    notes = Note.objects.filter(etudiant=etudiant).select_related("matiere")

    stats_map = {
        s["matiere"]: s
        for s in Note.objects.filter(etudiant__classe=classe)
        .values("matiere")
        .annotate(
            min_note=Min("moyenne"),
            max_note=Max("moyenne"),
            avg_note=Avg("moyenne"),
        )
    }

    classement = (
        Note.objects.filter(etudiant__classe=classe)
        .values("etudiant")
        .annotate(moy=Avg("moyenne"))
        .order_by("-moy")
    )

    rangs = {item["etudiant"]: i + 1 for i, item in enumerate(classement)}
    rang_general = format_rang(rangs.get(etudiant.id, "-"))

    data = [[
        "MATIÈRE", "MOY", "COEF", "MOY*COEF",
        "MENTION","RANG", "MIN", "MOY", "MAX"
    ]]

    total_points = 0
    total_coef = 0

    for n in notes:
        m = n.matiere
        stats = stats_map.get(m.id, {})
        moy = safe_round(n.moyenne)
        coef = safe_round(m.coefficient)
        total_points += moy * coef
        total_coef += coef
        rang_matiere = (
          Note.objects.filter(
          etudiant__classe=classe,
          matiere=m,
          moyenne__gt=n.moyenne
          )
       .count() + 1
     )

        data.append([
            m.libelle,
            moy,
            coef,
            safe_round(moy * coef),
            mention(moy),
            format_rang(rang_matiere),
            safe_round(stats.get("min_note")),
            safe_round(stats.get("avg_note")),
            safe_round(stats.get("max_note")),
        ])

    table_width = A4[0] - 2.4 * cm
    table_height = 200  # ajuste selon ton contenu
 
    # table = Table(data)
    table = Table(data, colWidths=[
    6 * cm,   # MATIÈRE (plus large)
    1.5 * cm,
    1.5 * cm,
    2 * cm,
    2.5 * cm,
    1.5 * cm,
    1.5 * cm,
    1.5 * cm,
  ])
    table.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 effet arrondi
   ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # =====================================================
    # RECAP
    # =====================================================
    moyenne_generale = calcul_moyenne_etudiant(etudiant)

    recap_data = [
       ["RAPPEL SEMESTRE", "TRAVAIL", "CONDUITE", "CONSEIL DE CLASSE"],

       [
        "",

        # TRAVAIL
        f"Total points : {safe_round(total_points)}\n"
        f"Total coef : {safe_round(total_coef)}\n"
        f"Moyenne : {safe_round(moyenne_generale)} / 20\n"
        f"Rang : {rang_general}",

        # CONDUITE (discipline)
        f"Absences totales : ...\n"
        f"Absences justifiées : ...\n"
        f"Consignes : ...\n"
        f"Exclusions : ...",

        # CONSEIL DE CLASSE
        f"Note conduite : ...\n"
        f"Blâme : ...\n"
        f"Félicitations : ...\n"
        f"Tableau d'honneur : ...\n"
        f"Encouragement : ...\n"
        f"Avertissement : ..."
     ],
   ]

    recap = Table(
     recap_data,
      colWidths=[4.5 * cm, 4.5 * cm, 4.5 * cm, 5 * cm]
    )
    
    recap.setStyle(TableStyle([
    # Bordures globales
    ("BOX", (0, 0), (-1, -1), 1.2, colors.black),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

    # HEADER
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 9),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),

    # CONTENU
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 1), (-1, -1), 8),
    ("VALIGN", (0, 1), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 1), (-1, -1), 6),
    ("RIGHTPADDING", (0, 1), (-1, -1), 6),
    ("TOPPADDING", (0, 1), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 effet arrondi
  ]))

    elements.append(recap)
    observation = Paragraph(
    """
    <br/>
    <b>OBSERVATION DU CONSEIL DE CLASSE :</b><br/><br/>
    L’étudiant a montré un travail satisfaisant au cours de ce semestre.
    Le conseil encourage l’étudiant à poursuivre ses efforts pour améliorer ses résultats
    et maintenir une discipline exemplaire.
    """,
    SMALL
)

    elements.append(observation)
    elements.append(Spacer(1, 20))



    visa_table = Table([
    [
        Paragraph("<b>Le Chef d’établissement</b><br/><br/><br/><br/>Signature & Cachet", SMALL),
        Paragraph("<b>Le Président du Jury</b><br/><br/><br/><br/>Signature", SMALL),
    ]
   ], colWidths=[8 * cm, 8 * cm])



    visa_table.setStyle(TableStyle([
    # bordure principale plus élégante
    ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#222222")),

    # grille interne discrète (si plusieurs cases)
    ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),

    # fond léger (style administratif)
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F7F7")),

    # alignement propre
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

    # padding équilibré (important pour effet “carte”)
    ("TOPPADDING", (0, 0), (-1, -1), 15),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),

    # typo plus propre
    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
   ]))

    elements.append(visa_table)
    # =====================================================
    # FOOTER
    # =====================================================
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        f"Edité le {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        SMALL
    ))

    doc.build(elements)

    return file_path