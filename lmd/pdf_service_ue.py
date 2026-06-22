from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from django.conf import settings
import os
from lmd.models import EtudiantLMD
from .models import EtudiantLMD, UE, NoteLMD


# =========================================================
# STYLES
# =========================================================

styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "TITLE",
    parent=styles["Normal"],
    fontSize=14,
    leading=16,
    alignment=1,
    spaceAfter=10,
    textColor=colors.HexColor("#1a1a1a"),
    fontName="Helvetica-Bold"
)

SMALL = ParagraphStyle(
    "SMALL",
    parent=styles["Normal"],
    fontSize=9,
    leading=11
)


# =========================================================
# HELPERS
# =========================================================

def get_image(path, width, height, fallback):
    if path and os.path.exists(path):
        return Image(path, width=width, height=height)
    return Paragraph(fallback, SMALL)


# =========================================================
# GENERATION PDF
# =========================================================

def generate_bulletin_lmd_pdf(etudiant_id, file_path):

    etudiant = EtudiantLMD.objects.get(id=etudiant_id)

    ues = UE.objects.filter(
        filiere=etudiant.filiere
    ).prefetch_related("ecues")

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []


    # =========================================================
    # HEADER REPUBLIQUE
    # =========================================================
   

    header_table = Table([
    [
        Paragraph("""
        <para align="left">
       <b> MINISTÈRE DE L'ENSEIGNEMENT SUPÉRIEUR<br/>
        ET DE LA RECHERCHE SCIENTIFIQUE</b>
        </para>
        """, SMALL),

        Paragraph("""
        <para align="right">
        <b>RÉPUBLIQUE DE CÔTE D'IVOIRE</b><br/>
        Union - Discipline - Travail
        </para>
        """, SMALL)
      ]], colWidths=[9 * cm, 9 * cm])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(header_table)


    # =========================================================
    # LOGO
    # =========================================================

    logo_path = os.path.join(settings.BASE_DIR, "core/static/logo.jpeg")
    logo = get_image(logo_path, 2 * cm, 2 * cm, "LOGO")


    # =========================================================
    # CADRE UNIVERSITE
    # =========================================================

    cadre_universite = Table([[
        Paragraph("""
            <b>UNIVERSITÉ INTERNATIONALE</b><br/>
            RELEVÉ DE NOTES LMD<br/>
            ANNÉE 2025 - 2026
        """, SMALL)
    ]], colWidths=[8 * cm], rowHeights=[2.5 * cm])

    cadre_universite.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 arrondi
    ]))


    # =========================================================
    # LOGO CENTER
    # =========================================================

    logo_center = Table([[logo]], colWidths=[2.5 * cm])
    logo_center.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))


    # =========================================================
    # ETUDIANT
    # =========================================================

    cadre_etudiant = Table([
        [Paragraph("<b>Nom</b>", SMALL), Paragraph(str(etudiant.nom), SMALL)],
        [Paragraph("<b>Prénoms</b>", SMALL), Paragraph(str(etudiant.prenoms), SMALL)],
        [Paragraph("<b>Matricule</b>", SMALL), Paragraph(str(etudiant.matricule), SMALL)],
        [Paragraph("<b>Filière</b>", SMALL), Paragraph(str(etudiant.filiere), SMALL)],
        [Paragraph("<b>Niveau</b>", SMALL), Paragraph(str(etudiant.niveau), SMALL)],
    ], colWidths=[3 * cm, 5 * cm])

    cadre_etudiant.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 arrondi
    ]))


    # =========================================================
    # HEADER GLOBAL
    # =========================================================

    header_global = Table(
        [[cadre_universite, logo_center, cadre_etudiant]],
        colWidths=[8 * cm, 2.5 * cm, 7 * cm],
        rowHeights=[3.5 * cm]
    )

    header_global.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(header_global)
    elements.append(Spacer(1, 10))

    TITLE_GREEN = ParagraphStyle(
    "TITLE_GREEN",
    parent=styles["Normal"],
    fontSize=14,
    leading=16,
    alignment=1,
    spaceAfter=10,
    textColor=colors.green,
    fontName="Helvetica-Bold"
    )

    elements.append(
    Paragraph("BULLETIN DE NOTES - 1er SEMESTRE", TITLE_GREEN)
    )
    # =========================================================
    # TABLE BULLETIN
    # =========================================================

    data = [["CODE","UE:UNITES D'ENSEIGNEMENTS","ECUE","C.ECUE","C.EU","M.ECUE","M.UE","DÉCISION"]]

    somme_generale = 0
    total_ue = 0
    ue_validees = 0
    ue_non_validees = 0
    credits_total = 0
    credits_obtenus = 0
    somme_ponderee_ue = 0
    total_credit_ue = 0
    ecues_total = 0
    ecues_validees = 0
    

    for ue in ues:

        ecues = ue.ecues.all()
        somme_ue = 0
        count = 0
        lignes = []
        credit_ue = getattr(ue, "credit", 6)
        somme_ponderee = 0
        credit_total_ue = 0
       

        premiere_ligne = True

        for ecue in ecues:
            ecues_total += 1
            note = NoteLMD.objects.filter(
                etudiant=etudiant,
                ecue=ecue
            ).first()
            moy_ecue = float(note.moyenne) if note and note.moyenne is not None else 0
            # ✔ ECUE validée
            if moy_ecue >= 10:
                 ecues_validees += 1
                 
            credit_ecue = ecue.credit
             # ✔ pondération correcte
            somme_ponderee += credit_ecue * moy_ecue
            credit_total_ue += credit_ecue
            moy_ue = round(somme_ponderee / credit_total_ue, 2) if credit_total_ue else 0

            somme_ue += moy_ecue
            count += 1

            lignes.append([
                ue.code if premiere_ligne else "",
                ue.libelle if premiere_ligne else "",
                ecue.libelle,
                # getattr(ecue, "credit", 0),
                ecue.credit,
                credit_ue,
                round(moy_ecue, 2),
                "",
                ""
            ])

            premiere_ligne = False

        if count == 0:
            continue

        moy_ue = round(somme_ue / count, 2)
        # decision = "VALIDÉE" if moy_ue >= 10 else "NON VALIDÉE"
        decision = (
            '<para align="center"><font color="green"><b>VALIDÉE</b></font></para>'
            if moy_ue >= 10
            else '<para align="center"><font color="red"><b>NON VALIDÉE</b></font></para>'
        )

        credits_total += credit_ue

        if moy_ue >= 10:
            ue_validees += 1
            credits_obtenus += credit_ue
          
        else:
            ue_non_validees += 1

        somme_generale += moy_ue
        total_ue += 1

        for r in lignes:
            r[6] = moy_ue
            # r[7] = decision
            r[7] = Paragraph(decision, SMALL)
            data.append(r)


    moyenne_generale = round(somme_generale / total_ue, 2) if total_ue else 0

    credits_restants = credits_total - credits_obtenus
    table = Table(data, colWidths=[
        1.4 * cm,
        6 * cm,
        6 * cm,
        1.4 * cm,
        1 * cm,
        1.5 * cm,
        1.2 * cm,
        2.2 * cm
    ],
    rowHeights=[30] + [22] * (len(data) - 1)
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 arrondi
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))


    # =========================================================
    # RECAP TABLE (TA DEMANDE EXACTE)
    # =========================================================
    rang = "-"
    decision_globale = (
    '<para align="center"><font color="green"><b>ADMIS</b></font></para>'
    if moyenne_generale >= 10
    else '<para align="center"><font color="red"><b>AJOURNÉ</b></font></para>'
    )

    recap_final_table = Table([
        [
            Paragraph("<b>Récapitulatif</b>", SMALL),
            Paragraph("<b>Responsable</b>", SMALL),
            Paragraph("<b>Année</b>", SMALL),
            Paragraph("<b>Décision</b>", SMALL),
        ],
        [
            Paragraph(
                f"""
                <para color="#1F4E79">
                Total ECUE validés : {ecues_validees}/{ecues_total}<br/>
                Total UE validées : {ue_validees}/{total_ue}<br/>
                Total crédits acquis : {credits_obtenus}/{credits_total}<br/>
                Total Crédits restants : {credits_restants}/{credits_total}<br/>
                Moyenne obtenue : {moyenne_generale}/20<br/>
                Rang occupé : {rang}
                 </para>
                """,
                SMALL
            ),
            Paragraph("Dr.JERRY TAFOTIE", SMALL),
            Paragraph("2025 - 2026", SMALL),
            Paragraph(decision_globale, SMALL),
        ]
    ], colWidths=[8.5 * cm, 3.5 * cm, 3 * cm, 3 * cm])

    recap_final_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),  # 🔥 plus grand pour header
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),  # 👉 arrondi
    ]))

    elements.append(recap_final_table)

    # =========================================================
    # SIGNATURE
    # =========================================================

    signature_table = Table([[
        Paragraph("<b>RESPONSABLE</b><br/>__________", styles["Normal"]),
        Paragraph("<b>VISA</b><br/>__________", styles["Normal"]),
    ]], colWidths=[9 * cm, 9 * cm], rowHeights=[5 * cm])

    signature_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(Spacer(1, 15))
    elements.append(signature_table)

    footer_table = Table([
         [
        Paragraph(
            "<b>ÉTABLISSEMENT :</b><br/>Université Internationale",
            styles["Normal"]
        ),
        Paragraph(
            "<b>LIEU :</b><br/>Abidjan, Côte d’Ivoire",
            styles["Normal"]
        ),
         Paragraph(
            "<b>ANNÉE ACADÉMIQUE :</b><br/>2026 - 2027",
            styles["Normal"]
        ),
    ],
     
   ], colWidths=[6 * cm, 6 * cm, 6 * cm])

    elements.append(Spacer(1, 20))
    elements.append(footer_table)
    # =========================================================
    # BUILD
    # =========================================================

    doc.build(elements)

    return file_path