import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing in .env file!")

print("--> Connecting to Supabase...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("--> Reading cleaned & enriched leads CSV...")
df = pd.read_csv("cleaned_enriched_leads.csv")

# Fill NaN with None for clean JSON serialization in PostgreSQL
records = df.where(pd.notnull(df), None).to_dict(orient="records")

print(f"--> Uploading {len(records)} records to table 'enriched_b2b_leads'...")

batch_size = 50
for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]
    response = supabase.table("enriched_b2b_leads").insert(batch).execute()
    print(f"Uploaded batch {i // batch_size + 1} ({len(batch)} records)")

print("\nAll records successfully synced to Supabase!")