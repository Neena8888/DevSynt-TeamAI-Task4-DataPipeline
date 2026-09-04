import pandas as pd
import numpy as np

np.random.seed(42)

companies = [
    ("google llc", "https://google.com", "Sundar Pichai", "sundar@google.com", "+1 650 253 0000", "USA", "150000"),
    ("GOOGLE", "http://google.com", "Sundar P.", "sundar.p@google.com", "650-253-0000", "United States", "150000"),
    ("stripe inc", "stripe.com", "Patrick Collison", "patrick@stripe.com", "+1-888-926-2289", "US", "8000"),
    ("stripe, inc.", "https://stripe.com/", "Patrick C", "patrick@stripe.com", "8889262289", "USA", "8000"),
    ("shopify", "shopify.com", "Tobias Lutke", "tobi@shopify.com", "1-888-746-7439", "Canada", "11600"),
    ("DATADOG", "datadoghq.com", "Olivier Pomel", "oli@datadog.com", "N/A", "usa", "4800"),
    ("notion labs", "www.notion.so", "Ivan Zhao", "ivan@notion.so", "invalid-phone", "United States of America", "500"),
    ("CANVA PTY LTD", "canva.com", "Melanie Perkins", "melanie@canva.com", "+61 2 8000 0000", "Australia", "3500"),
    ("airtable", "airtable.com", "Howie Liu", "howie@airtable.com", " ", "USA", "900"),
    ("Figma Inc.", "figma.com", "Dylan Field", "dylan@figma.com", "+1 415 555 0199", "US", "1200"),
    ("GitLab", "about.gitlab.com", "Sid Sijbrandij", "sid@gitlab.com", "+1 415 555 0122", "United States", "2100"),
    ("HubSpot", "hubspot.com", "Yamini Rangan", "yamini@hubspot.com", "888-482-7768", "USA", "7400"),
    ("slack technologies", "slack.com", "Denise Dresser", "denise@slack.com", "N/A", "usa", "2500"),
    ("Zoom Video", "zoom.us", "Eric Yuan", "eric@zoom.us", "+1 888 799 9666", "US", "7000"),
    ("Atlassian", "atlassian.com", "Mike Cannon-Brookes", "mike@atlassian.com", "+61 2 9299 9600", "Australia", "11000"),
    ("Twilio Inc", "twilio.com", "Khozema Shipchandler", "khozema@twilio.com", "+1 877 889 4546", "USA", "6000"),
    ("Asana", "asana.com", "Dustin Moskovitz", "dustin@asana.com", "N/A", "United States", "1800"),
    ("Miro", "miro.com", "Andrey Khusid", "andrey@miro.com", "+1 415 555 0188", "USA", "1800"),
    ("ClickUp", "clickup.com", "Zeb Evans", "zeb@clickup.com", "888-555-0144", "US", "900"),
    ("Zapier Inc", "zapier.com", "Wade Foster", "wade@zapier.com", "N/A", "USA", "800")
]

rows = []
for i in range(125):
    base = companies[i % len(companies)]
    is_corrupt = np.random.rand() < 0.25
    
    comp_name = base[0] if not is_corrupt else base[0].lower() + " test lead"
    website = base[1] if not is_corrupt else base[1].replace("https://", "").replace("http://", "")
    lead_name = base[2] if not is_corrupt else base[2] + f" {i}"
    email = base[3] if not is_corrupt else f"invalid_{i}@bad domain! .com"
    phone = base[4] if not is_corrupt else "000-000"
    country = base[5] if not is_corrupt else "u.s.a"
    employees = base[6] if not is_corrupt else "-50"
    
    rows.append({
        "lead_id": f"RAW_LEAD_{1000+i}",
        "company_name": comp_name,
        "website": website,
        "contact_name": lead_name,
        "contact_email": email,
        "phone_number": phone,
        "country": country,
        "raw_employee_count": employees,
        "notes": "Inbound CSV lead via Marketing Campaign 2026"
    })

df_raw = pd.DataFrame(rows)
df_raw.to_csv("raw_leads_dataset.csv", index=False)
print(f"Done! Created raw_leads_dataset.csv with {len(df_raw)} records.")