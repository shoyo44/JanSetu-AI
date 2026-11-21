"""
DocsAI Professional Sample PDF Generator.
════════════════════════════════════════
Generates 3 styled sample PDF documents across Governance, Judgment, and Legal verticals:
1. Sample_Commercial_Vendor_Agreement.pdf (Legal & Startup: triggers Red-Flag Analysis)
2. Sample_Supreme_Court_Judgment.pdf      (Judgment: triggers Case Law & Concordance)
3. Sample_PM_KISAN_Gazette_Policy.pdf     (Governance: triggers Jan Suvidha Citizen Checklist)
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

# Custom styles
primary_color = colors.HexColor("#1e293b")
secondary_color = colors.HexColor("#0284c7")
accent_red = colors.HexColor("#dc2626")
light_bg = colors.HexColor("#f8fafc")

title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=primary_color,
    alignment=1, # Center
    spaceAfter=12
)

subtitle_style = ParagraphStyle(
    "DocSubtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    textColor=colors.HexColor("#64748b"),
    alignment=1,
    spaceAfter=15
)

h1_style = ParagraphStyle(
    "SectionH1",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=17,
    textColor=secondary_color,
    spaceBefore=14,
    spaceAfter=6
)

body_style = ParagraphStyle(
    "BodyDark",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor("#334155"),
    spaceAfter=8
)

callout_style = ParagraphStyle(
    "CalloutText",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=9,
    leading=13,
    textColor=colors.HexColor("#1e3a8a"),
)

redflag_style = ParagraphStyle(
    "RedFlagText",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=14,
    textColor=accent_red,
    spaceAfter=8
)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Commercial Vendor & SaaS Agreement (Legal / Startup)
# ══════════════════════════════════════════════════════════════════════════════
def build_commercial_agreement_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Sample_Commercial_Vendor_Agreement.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    story = []

    story.append(Paragraph("MASTER SERVICES & SOFTWARE VENDOR AGREEMENT", title_style))
    story.append(Paragraph("Contract Reference: DOCSAI-MSA-2025/DEL-894 | Confidential & Proprietary", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceAfter=15))

    p_intro = (
        "This Master Services Agreement (\"Agreement\") is entered into on this 15th day of January, 2025, "
        "by and between <b>Alpha Enterprise Solutions Pvt. Ltd.</b>, a private limited company incorporated under the "
        "Companies Act, 2013 having its registered office at Connaught Place, New Delhi 110001 (hereinafter \"Customer\"), "
        "and <b>Apex Cloud Technologies LLC</b>, having its principal place of business at Cyber City, Gurugram (hereinafter \"Vendor\")."
    )
    story.append(Paragraph(p_intro, body_style))

    story.append(Paragraph("1. Scope of Work & Professional Deliverables", h1_style))
    story.append(Paragraph(
        "Vendor agrees to deliver sovereign enterprise cloud architecture, automated data migration, and API integration "
        "milestones as defined in Statement of Work (SOW-1). All deliverables must satisfy Section 16 of the Digital Personal "
        "Data Protection Act (DPDPA), 2023 regarding cross-border data processing restrictions.",
        body_style
    ))

    story.append(Paragraph("2. Payment Terms, Retainers & Late Fees", h1_style))
    story.append(Paragraph(
        "Customer shall remit net milestone fees of INR 45,00,000 within thirty (30) days from verified receipt of invoices. "
        "Uncontested overdue balances shall accrue interest at the penal rate of 2.5% per month compounded bi-weekly.",
        body_style
    ))

    story.append(Paragraph("3. Limitation of Liability (Audit Red-Flag Clause)", h1_style))
    story.append(Paragraph(
        "<b>Section 3.1 (Uncapped Liability):</b> NOTWITHSTANDING ANYTHING CONTAINED HEREIN, CUSTOMER SHALL INDEMNIFY, "
        "DEFEND, AND HOLD HARMLESS VENDOR AGAINST ANY AND ALL DIRECT, INDIRECT, CONSEQUENTIAL, INCIDENTAL, OR PUNITIVE LOSSES, "
        "WITHOUT ANY FINANCIAL CEILING OR MONETARY AGGREGATE CAP.",
        redflag_style
    ))
    story.append(Paragraph(
        "<i>[Note for DocsAI Legal Reviewer: This clause contains an asymmetrical, uncapped liability structure favoring the vendor.]</i>",
        callout_style
    ))

    story.append(Paragraph("4. Intellectual Property & Work-for-Hire", h1_style))
    story.append(Paragraph(
        "All custom source code, documentation, machine learning models, and training data developed specifically for Customer "
        "shall constitute 'work made for hire' and Customer shall exclusively retain worldwide copyright, patent, and trademark ownership.",
        body_style
    ))

    story.append(Paragraph("5. Non-Compete & Restrictive Covenants (Audit Red-Flag Clause)", h1_style))
    story.append(Paragraph(
        "<b>Section 5.2 (Unreasonable Non-Compete):</b> Customer covenants that during the term and for a period of five (5) "
        "years following termination, Customer shall not directly or indirectly engage in, invest in, or procure services from "
        "any entity offering competitive cloud software across South Asia.",
        redflag_style
    ))
    story.append(Paragraph(
        "<i>[Note for DocsAI Legal Reviewer: Under Section 27 of the Indian Contract Act, 1872, agreements in restraint of trade are void ab initio.]</i>",
        callout_style
    ))

    story.append(Paragraph("6. Governing Law, Jurisdiction & Arbitration", h1_style))
    story.append(Paragraph(
        "This Agreement shall be governed by, and construed in accordance with, the laws of the Republic of India. "
        "Any dispute arising out of or in connection with this Agreement shall be referred to arbitration in New Delhi under the "
        "Arbitration and Conciliation Act, 1996.",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Supreme Court Landmark Bail Judgment (Judgment)
# ══════════════════════════════════════════════════════════════════════════════
def build_supreme_court_judgment_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Sample_Supreme_Court_Judgment.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    story = []

    story.append(Paragraph("IN THE SUPREME COURT OF INDIA", title_style))
    story.append(Paragraph("CRIMINAL APPELLATE JURISDICTION<br/>CRIMINAL APPEAL NO. 2481 OF 2024<br/>(Arising out of SLP (Crl.) No. 8412 of 2024)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceAfter=15))

    p_parties = (
        "<b>K. VIKRAMADITYA REDDY</b> ... APPELLANT(S)<br/><br/>"
        "<b>VERSUS</b><br/><br/>"
        "<b>STATE OF TELANGANA & ANR.</b> ... RESPONDENT(S)"
    )
    story.append(Paragraph(p_parties, body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("JUDGMENT & RATIO DECIDENDI", h1_style))
    p_j1 = (
        "<b>D.Y. Chandrachud, CJI:</b><br/>"
        "1. Leave granted. The present appeal arises from the final order dated 14.05.2024 passed by the High Court "
        "for the State of Telangana dismissing the application filed by the Appellant seeking regular bail under Section 439 "
        "of the Code of Criminal Procedure, 1973 (now corresponding to Section 483 of the Bharatiya Nagarik Suraksha Sanhita, 2023)."
    )
    story.append(Paragraph(p_j1, body_style))

    story.append(Paragraph("2. Facts & Statutory Sections Invoked", h1_style))
    p_j2 = (
        "The Appellant was arrested in connection with Crime No. 112/2023 registered at PS Cyberabad for alleged offenses punishable "
        "under Section 420 (Cheating and dishonestly inducing delivery of property) of the Indian Penal Code, 1860 (now Section 318(4) "
        "of the Bharatiya Nyaya Sanhita, 2023) and Section 65B of the Indian Evidence Act, 1872 (now Section 63 of Bharatiya Sakshya Adhiniyam, 2023). "
        "The Appellant has undergone continuous pre-trial incarceration for a period of fifteen (15) months."
    )
    story.append(Paragraph(p_j2, body_style))

    story.append(Paragraph("3. Landmark Ratio on Personal Liberty (Article 21)", h1_style))
    p_j3 = (
        "The primary ratio decidendi enunciated by this Court in <i>Satender Kumar Antil v. CBI (2022) 10 SCC 51</i> and "
        "<i>Manish Sisodia v. Directorate of Enforcement (2024) INSC 595</i> is that <b>'Bail is the rule, and jail is the exception'</b>. "
        "The deprivation of personal liberty under Article 21 of the Constitution of India cannot be converted into punitive pre-trial custody "
        "when trial is unlikely to conclude within a reasonable duration."
    )
    story.append(Paragraph(p_j3, body_style))

    story.append(Paragraph("4. The Triple Test & Bail Conditions", h1_style))
    p_j4 = (
        "Applying the established Triple Test (flight risk, risk of tampering with witnesses, risk of destroying electronic evidence), "
        "this Court finds no apprehension that cannot be mitigated by stringent conditions. The Appellant is directed to be released on "
        "regular bail upon furnishing a personal bond of INR 50,000/- with two solvent sureties, surrender of passport, and weekly reporting "
        "to the jurisdictional Station House Officer."
    )
    story.append(Paragraph(p_j4, body_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. PM-KISAN Operational Guidelines Gazette (Governance)
# ══════════════════════════════════════════════════════════════════════════════
def build_governance_gazette_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "Sample_PM_KISAN_Gazette_Policy.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    story = []

    story.append(Paragraph("MINISTRY OF AGRICULTURE & FARMERS WELFARE", title_style))
    story.append(Paragraph("DEPARTMENT OF AGRICULTURE & FARMERS WELFARE<br/>CENTRAL SECTOR SCHEME OPERATIONAL GUIDELINES — PM-KISAN", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceAfter=15))

    story.append(Paragraph("1. Scheme Overview & 100% Central Funding", h1_style))
    story.append(Paragraph(
        "The <b>Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)</b> is a Central Sector Scheme with 100% funding from the Government of India. "
        "The scheme aims to augment the financial resources of farmer families to procure agricultural inputs such as seeds, fertilizers, "
        "and equipment, as well as to support domestic and household consumption needs.",
        body_style
    ))

    story.append(Paragraph("2. Universal Landholding Eligibility Criteria", h1_style))
    story.append(Paragraph(
        "<b>Universal Coverage:</b> By decision of the Union Cabinet dated May 31 / June 1, 2019, the scope of PM-KISAN was revised "
        "from the initial small and marginal farmers threshold to cover <b>all landholder farmer families</b> who possess cultivable landholding "
        "in their names in official State/UT land records, irrespective of the size of their landholdings, subject to the exclusion criteria.",
        body_style
    ))

    story.append(Paragraph("3. Financial Benefits & DBT Installment Schedule", h1_style))
    story.append(Paragraph(
        "Eligible farmer families receive a financial benefit of <b>INR 6,000 per year</b>, payable in three equal installments of "
        "<b>INR 2,000 each</b> every four months. All transfers are credited directly into Aadhaar-seeded bank accounts through "
        "Direct Benefit Transfer (DBT) protocols under Public Financial Management System (PFMS).",
        body_style
    ))

    story.append(Paragraph("4. Mandatory Verification & Exclusion Criteria", h1_style))
    story.append(Paragraph(
        "The following categories of beneficiaries of higher economic status are strictly <b>excluded</b> from receiving benefits:<br/>"
        "• All Institutional Landholders.<br/>"
        "• Farmer families holding or having held Constitutional posts.<br/>"
        "• Former and serving Ministers, MPs, MLAs, and Mayors of Municipal Corporations.<br/>"
        "• All serving or retired officers and employees of Central/State Government Ministries and public sector enterprises.<br/>"
        "• All Persons who paid Income Tax in the last assessment year.<br/>"
        "• Professionals like Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with professional bodies.",
        body_style
    ))

    story.append(Paragraph("5. Jan Suvidha Checklist: Required Documents & Application Steps", h1_style))
    story.append(Paragraph(
        "Beneficiaries must furnish: (1) Aadhaar Number, (2) Land Ownership Record (ROR / Khatauni), (3) Active Bank Account linked with Aadhaar, "
        "(4) Completed biometric/OTP e-KYC. Applications may be submitted via PM-KISAN Portal (pmkisan.gov.in) or Common Service Centers (CSC).",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")


if __name__ == "__main__":
    build_commercial_agreement_pdf()
    build_supreme_court_judgment_pdf()
    build_governance_gazette_pdf()
    print("\nAll 3 sample PDFs generated successfully in:", OUTPUT_DIR)
