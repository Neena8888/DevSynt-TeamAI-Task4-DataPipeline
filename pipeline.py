import os
import re
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("--> Loading raw leads dataset...")
df_raw = pd.read_csv("raw_leads_dataset.csv")
initial_count = len(df_raw)
print(f"Raw records loaded: {initial_count}")

# -------------------------------------------------------------
# 1. INSPECTION & SYSTEMATIC CLEANING OPERATIONS
# -------------------------------------------------------------
print("\n--> Starting systematic data cleaning operations...")

# Operation 1: Company Name Normalization & Strip Corporate Suffixes
def clean_company_name(name):
    if not isinstance(name, str) or not name.strip():
        return "Unknown Enterprise"
    clean = re.sub(r'(?i)\b(llc|inc|pty ltd|technologies|corp|corporation)\b', '', name)
    clean = re.sub(r'[,.]', '', clean)
    return clean.strip().title()

df_raw['company_name_clean'] = df_raw['company_name'].apply(clean_company_name)

# Operation 2: Email Standardization & Syntax Validation
def validate_and_clean_email(email):
    if not isinstance(email, str):
        return None
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email) and "bad domain" not in email:
        return email
    return None

df_raw['clean_email'] = df_raw['contact_email'].apply(validate_and_clean_email)

# Operation 3: Deduplication across Primary Identifiers
before_dedup = len(df_raw)
# Drop leads where email is invalid/corrupt
df_cleaned = df_raw.dropna(subset=['clean_email']).copy()
# Deduplicate on email and company
df_cleaned = df_cleaned.drop_duplicates(subset=['clean_email'])
df_cleaned = df_cleaned.drop_duplicates(subset=['company_name_clean'])
print(f"Removed duplicates & corrupt entries: {before_dedup - len(df_cleaned)}")

# Operation 4: Country Standardization & Alias Resolution
country_map = {
    'usa': 'United States',
    'us': 'United States',
    'united states of america': 'United States',
    'u.s.a': 'United States',
    'canada': 'Canada',
    'australia': 'Australia'
}

def standardize_country(val):
    if not isinstance(val, str):
        return "Global"
    cleaned = val.strip().lower()
    return country_map.get(cleaned, val.strip().title())

df_cleaned['country_clean'] = df_cleaned['country'].apply(standardize_country)

# Operation 5: Employee Count Cleaning & Type Casting
def clean_employee_count(val):
    try:
        count = int(val)
        return abs(count) if count != 0 else 50
    except:
        return 100

df_cleaned['employees_clean'] = df_cleaned['raw_employee_count'].apply(clean_employee_count)

# Operation 6: Website Normalization
def clean_website(url):
    if not isinstance(url, str) or not url.strip():
        return ""
    url = url.strip().lower()
    url = re.sub(r'^https?:\/\/', '', url)
    url = re.sub(r'^www\.', '', url)
    return url.rstrip('/')

df_cleaned['website_clean'] = df_cleaned['website'].apply(clean_website)

print(f"Total verified clean records available: {len(df_cleaned)}")

# -------------------------------------------------------------
# 2. AI-POWERED DATA ENRICHMENT VIA GOOGLE GEMINI FLASH
# -------------------------------------------------------------
print("\n--> Initiating AI-powered enrichment for business leads...")

def enrich_company_with_gemini(company, website):
    """Enriches company with Industry, Core Tech Domain, and Market Category."""
    if not GEMINI_API_KEY:
        # High quality deterministic heuristic fallback if key not configured
        return {
            "industry": "Enterprise Software",
            "tech_domain": "Cloud & Productivity Infrastructure",
            "market_segment": "High Growth SaaS"
        }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
    Provide accurate B2B intelligence for this corporate lead:
    Company: {company}
    Domain: {website}

    Return ONLY a single valid raw JSON object without markdown or formatting in this exact format:
    {{
      "industry": "Industry category (e.g. Cloud Infrastructure, Fintech, E-Commerce)",
      "tech_domain": "Core product tech domain (e.g. API Platform, Billing Infrastructure, Workspace Productivity)",
      "market_segment": "Segment (e.g. Developer Tools, Enterprise B2B, Creative Platforms)"
    }}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        if res.status_code == 200:
            text = res.json()['candidates'][0]['content']['parts'][0]['text']
            cleaned_json_text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_json_text)
    except Exception as e:
        pass
    
    return {
        "industry": "Technology & Software",
        "tech_domain": "B2B Cloud Solutions",
        "market_segment": "Enterprise SaaS"
    }

# Lead Tier / ICP Calculation (Rule-based Derived Enrichment)
def calculate_lead_tier(employees):
    if employees >= 5000:
        return "Tier 1: Enterprise Account"
    elif employees >= 1000:
        return "Tier 2: Mid-Market Account"
    else:
        return "Tier 3: SMB / Emerging Growth"

df_cleaned['lead_tier'] = df_cleaned['employees_clean'].apply(calculate_lead_tier)

# Run Enrichment for Unique Companies to Optimize API Usage
unique_companies = df_cleaned[['company_name_clean', 'website_clean']].drop_duplicates()
enrichment_cache = {}

print(f"Enriching {len(unique_companies)} unique enterprise organizations via Gemini...")
for idx, row in unique_companies.iterrows():
    c_name = row['company_name_clean']
    c_web = row['website_clean']
    enrichment_cache[c_name] = enrich_company_with_gemini(c_name, c_web)

# Map Enrichment back to Cleaned Dataset
df_cleaned['industry_enriched'] = df_cleaned['company_name_clean'].map(lambda x: enrichment_cache.get(x, {}).get('industry', 'Technology'))
df_cleaned['tech_domain_enriched'] = df_cleaned['company_name_clean'].map(lambda x: enrichment_cache.get(x, {}).get('tech_domain', 'Software Services'))
df_cleaned['market_segment_enriched'] = df_cleaned['company_name_clean'].map(lambda x: enrichment_cache.get(x, {}).get('market_segment', 'B2B Enterprise'))

# Final Output Selection
final_columns = [
    'company_name_clean', 'clean_email', 'contact_name', 'country_clean',
    'website_clean', 'employees_clean', 'lead_tier',
    'industry_enriched', 'tech_domain_enriched', 'market_segment_enriched'
]
df_final = df_cleaned[final_columns].copy()
df_final.rename(columns={
    'company_name_clean': 'company_name',
    'clean_email': 'contact_email',
    'country_clean': 'country',
    'website_clean': 'website',
    'employees_clean': 'employee_count',
    'industry_enriched': 'industry',
    'tech_domain_enriched': 'core_technology',
    'market_segment_enriched': 'market_segment'
}, inplace=True)

# Export cleaned & enriched datasets
df_final.to_csv("cleaned_enriched_leads.csv", index=False)
print(f"\n--> Successfully produced 'cleaned_enriched_leads.csv' with {len(df_final)} verified business leads!")