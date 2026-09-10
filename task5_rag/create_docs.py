import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("sample_documents", exist_ok=True)
styles = getSampleStyleSheet()

title = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#1A365D"))
h2 = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor("#2B6CB0"), spaceBefore=8, spaceAfter=4)
body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor("#2D3748"), spaceAfter=5)

# 1. Company Overview
d1 = SimpleDocTemplate("sample_documents/1_Company_Overview.pdf", pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
s1 = [
    Paragraph("ApexHaven Properties — Corporate Overview & Profile", title),
    Spacer(1, 6),
    Paragraph("<b>Corporate Identity & Vision:</b> Founded in 2018 and headquartered in Seattle, Washington, ApexHaven Properties is a premier modern real estate brokerage and asset management consultancy. We specialize in luxury residential acquisitions, commercial developments, and portfolio advisory across 4 core markets: Pacific Northwest (Seattle, Bellevue), Northern California (San Francisco, Silicon Valley), Southern California (Los Angeles, Irvine), and Texas (Austin, Dallas).", body),
    Paragraph("Executive Leadership & Governance", h2),
    Paragraph("• <b>CEO:</b> Marcus Vance — Former VP of Global Real Estate Investments at Vanguard Horizon with 22 years of institutional experience.<br/>• <b>COO:</b> Elena Rostova — Specialist in architectural engineering; managed $1.4B in multi-family transformations.<br/>• <b>Head of Brokerage:</b> Tariq Mansoor — Master Broker managing high-net-worth individual private clients.", body),
    Paragraph("Scale & Accreditation", h2),
    Paragraph("Operating under DRE License #02194821 and WA DOL License #24091. As of Q2 2026, ApexHaven has closed $3.85 Billion across 1,840+ completed asset transactions with an average velocity of 18.4 calendar days on market.", body)
]
d1.build(s1)

# 2. Property Listings
d2 = SimpleDocTemplate("sample_documents/2_Property_Listings.pdf", pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
s2 = [
    Paragraph("ApexHaven Properties — Active Portfolio Listings (Q3 2026)", title),
    Spacer(1, 6),
    Paragraph("Listing APX-101: The Cascade Crest Villa (Bellevue, WA)", h2),
    Paragraph("• <b>Address:</b> 8420 Summit Ridge Way, Bellevue, WA 98004<br/>• <b>Price:</b> $4,850,000 USD<br/>• <b>Specs:</b> 5 Beds, 6 Baths, 6,400 sq.ft, 0.65 Acre lot<br/>• <b>Features:</b> Lake Washington panoramic views, geothermal radiant heating, 3-car EV subterranean garage, private 800-bottle wine cellar.<br/>• <b>Annual Tax:</b> $46,200 | <b>HOA:</b> $650/month.", body),
    Paragraph("Listing APX-102: Silicon Terrace Penthouse (San Francisco, CA)", h2),
    Paragraph("• <b>Address:</b> 350 Mission Boulevard, Penthouse 42B, San Francisco, CA 94105<br/>• <b>Price:</b> $3,250,000 USD<br/>• <b>Specs:</b> 3 Beds, 3.5 Baths, 3,100 sq.ft<br/>• <b>Features:</b> 360-degree Bay Bridge & skyline vistas, wrap-around cantilevered terrace, Miele appliances, 24/7 biometric concierge.<br/>• <b>Annual Tax:</b> $38,500 | <b>HOA:</b> $1,850/month.", body),
    Paragraph("Listing APX-103: Austin Tech Ridge Commercial Hub (Austin, TX)", h2),
    Paragraph("• <b>Address:</b> 11200 Innovation Way, Austin, TX 78753<br/>• <b>Price:</b> $12,750,000 USD (Class-A Commercial)<br/>• <b>Specs:</b> 42,000 rentable sq.ft, 140 reserved surface parking spots<br/>• <b>Tenancy:</b> 82% pre-leased to 2 enterprise AI firms with 7-year NNN leases; Net Operating Income is $892,500 at a 7.0% cap rate.", body)
]
d2.build(s2)

# 3. Services & Fees
d3 = SimpleDocTemplate("sample_documents/3_Services_and_Fees.pdf", pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
s3 = [
    Paragraph("ApexHaven Properties — Professional Services & Fee Schedule", title),
    Spacer(1, 6),
    Paragraph("1. Residential Seller Representation", h2),
    Paragraph("Standard commission is 5.0% of gross settlement price (2.5% listing desk, 2.5% buyer procuring broker). Includes Matterport 3D digital twins, architectural twilight photography, and luxury portal staging.", body),
    Paragraph("2. Buyer Advisory Services", h2),
    Paragraph("Retainer fee of $2,500 upfront (credited against closing proceeds). Standard 2.5% representation commission satisfied by seller proceeds at escrow closing.", body),
    Paragraph("3. Commercial Brokerage & Triple Net (NNN)", h2),
    Paragraph("4.0% for assets below $10M; 3.0% for institutional transactions above $10M. Commercial leasing fee: 4.5% of cumulative base rent over years 1-5.", body),
    Paragraph("4. Property Management", h2),
    Paragraph("Monthly fee: 7.0% of gross monthly rental receipts (minimum $300/month per unit). Tenant placement: 50% of first full month's rent. Flat $350 lease renewal fee.", body)
]
d3.build(s3)

# 4. FAQs
d4 = SimpleDocTemplate("sample_documents/4_Frequently_Asked_Questions.pdf", pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
s4 = [
    Paragraph("ApexHaven Properties — Frequently Asked Questions (FAQ)", title),
    Spacer(1, 6),
    Paragraph("Q1: What is the mandatory earnest money deposit (EMD)?", h2),
    Paragraph("<b>Answer:</b> ApexHaven requires a minimum earnest money deposit of 3.0% on residential purchases and 5.0% on commercial transactions. EMD must be wired directly to First American Title or Chicago Title escrow within two (2) business days of mutual execution.", body),
    Paragraph("Q2: Does ApexHaven allow Dual Agency representation?", h2),
    Paragraph("<b>Answer:</b> No. To uphold strict fiduciary standards and eliminate conflicts of interest, ApexHaven maintains a strict prohibition against Dual Agency. Buyers bidding on ApexHaven listings must engage an independent outside broker or sign an unrepresented customer waiver.", body),
    Paragraph("Q3: How are showings arranged for luxury properties over $2.5M?", h2),
    Paragraph("<b>Answer:</b> Requires minimum 24-hour advance notice along with verified Proof of Funds (POF) or an active institutional pre-approval letter prior to entry access.", body),
    Paragraph("Q4: What happens if an appraisal comes in lower than the contracted price?", h2),
    Paragraph("<b>Answer:</b> Under an appraisal contingency, the buyer may renegotiate the price, bridge the cash deficit, or terminate the contract with a 100% full refund of their earnest money deposit within 5 business days.", body)
]
d4.build(s4)

# 5. Policies & Terms
d5 = SimpleDocTemplate("sample_documents/5_Policies_and_Terms.pdf", pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
s5 = [
    Paragraph("ApexHaven Properties — Policies & Governance Terms", title),
    Spacer(1, 6),
    Paragraph("Section 1: Escrow & Fund Disbursement Protocol", h2),
    Paragraph("All financial transactions must clear bonded, state-regulated third-party escrow accounts. ApexHaven never holds, accepts, or disburses client funds directly.", body),
    Paragraph("Section 2: Exclusive Listing Cancellation Rights", h2),
    Paragraph("Sellers may terminate an exclusive listing agreement with ten (10) calendar days written notice, subject to reimbursing actual out-of-pocket staging and media expenses capped at $3,500. A 90-day Broker Protection Period applies if an introduced prospect purchases.", body),
    Paragraph("Section 3: Anti-Money Laundering (AML) & FinCEN Compliance", h2),
    Paragraph("In compliance with FinCEN Geographic Targeting Orders, all cash or non-bank purchases over $300,000 in King County (WA), San Francisco County (CA), and Travis County (TX) must disclose beneficial owners owning 25% or greater equity.", body),
    Paragraph("Section 4: Dispute Resolution", h2),
    Paragraph("Disputes not settled via mediation within 30 days shall be resolved by binding neutral arbitration administered by the American Arbitration Association (AAA) under Commercial Arbitration Rules.", body)
]
d5.build(s5)

print("SUCCESS: 5 PDFs created in task5_rag/sample_documents/")