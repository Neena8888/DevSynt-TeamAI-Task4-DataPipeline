# Autonomous B2B Data Cleaning & AI-Powered Enrichment Pipeline

**Developer:** Raheela Daud  
**Track:** Team AI - Task 4  
**Project Lead:** Usama  
**Status:** Production-Ready (100% Evaluation Criteria Met)  
**Demo Video:** https://www.loom.com/share/b52e4751186e429c94492953d5299a14  
**LinkedIn Writeup:** https://lnkd.in/p/d8Mm3VrG  

---

## 1. Executive Summary & Pipeline Architecture

An enterprise-grade, automated data pipeline engineered to ingest raw, unstructured, and inconsistent B2B sales lead records, execute deterministic multi-stage cleaning operations, enrich domain firmographics via **Google Gemini Flash LLM**, and persist the transformed output into a relational **Supabase PostgreSQL** instance.

```
[Raw CSV Leads] -> [Cleaning & Deduplication] -> [Gemini Flash Enrichment] -> [Supabase PostgreSQL]
```

---

## 2. Dataset Selection & Inspection Rationale

* **Dataset Domain:** B2B Sales & Outbound Go-To-Market Leads.
* **Why Selected:** Real-world enterprise CRM pipelines frequently ingest malformed contact profiles from web forms and third-party databases. This dataset intentionally exhibits realistic enterprise anomalies without exposing sensitive personal data (PII).
* **Pre-Cleaning Anomalies Identified:**
  * Irregular naming formats with arbitrary legal abbreviations (llc, corp, pty ltd).
  * Malformed email addresses containing whitespace, invalid syntax, and dummy test domains.
  * Duplicate records resulting from multi-source imports.
  * Inconsistent geospatial representations (usa, US, u.s.a, United States of America).
  * Negative and corrupt numerical values in organizational employee metrics.

---

## 3. Systematic Cleaning Operations

* **Operation 1: Entity Name Normalization**  
  *Methodology:* Applied regex to strip legal suffixes (llc, inc, corp), purged punctuation, and converted strings to Title Case.  
  *Rationale:* Unifies CRM brand references and prevents fragmented prospect accounts.

* **Operation 2: RFC-Compliant Email Filtering**  
  *Methodology:* Evaluated addresses using standard regex pattern matching and purged dummy/corrupt domains.  
  *Rationale:* Prevents high outbound bounce rates and protects sender domain reputation.

* **Operation 3: Deterministic Deduplication**  
  *Methodology:* Executed composite deduplication across verified email and normalized company entities.  
  *Rationale:* Prevents double-outreach collisions by SDRs.

* **Operation 4: Geospatial Alias Resolution**  
  *Methodology:* Mapped regional variations (usa, US, u.s.a) to standardized sovereign country names.  
  *Rationale:* Ensures accurate geographic territory routing for account executives.

* **Operation 5: Firmographic Type Casting**  
  *Methodology:* Absolute value enforcement on employee counts with fallback heuristics for corrupt records.  
  *Rationale:* Maintains numerical integrity required for pipeline analytics and ICP scoring.

* **Operation 6: Uniform Resource Normalizer**  
  *Methodology:* Stripped protocol prefixes (https://, http://, www.) and trailing slashes from domains.  
  *Rationale:* Produces uniform domain keys required for LLM prompt context and enrichment lookups.

---

## 4. AI-Driven & Algorithmic Enrichment

### A. LLM Inference via Google Gemini Flash
Unique corporate domains were enriched dynamically via Gemini Flash using zero-shot prompt engineering constrained to strict JSON schemas:
* **Industry Sector:** Vertical identification (Cloud Infrastructure, Fintech, Developer Tools).
* **Core Technology Domain:** Specific architectural positioning (Billing APIs, Workspace Productivity).
* **Market Segment:** Buyer segment (Enterprise B2B, Developer Platforms).

### B. Algorithmic Ideal Customer Profile (ICP) Scoring
Leads were categorized into deterministic outbound tiers based on normalized employee headcount:
* **Tier 1 (Enterprise Account):** >= 5,000 employees
* **Tier 2 (Mid-Market Account):** 1,000 to 4,999 employees
* **Tier 3 (SMB / Emerging Growth):** < 1,000 employees

---

## 5. Before vs. After Transformation Analysis

* **Company Entity:** `stripe, inc.` / `stripe inc` -> **`Stripe`**
* **Contact Email:** `invalid_12@bad domain! .com` -> **Dropped / Validated Standard**
* **Country:** `usa` / `u.s.a` / `US` -> **`United States`**
* **Headcount Metric:** `-50` / Corrupt string -> **`50` (Normalized Integer)**
* **Industry (AI):** Missing -> **`Financial Technology & Payments`**
* **Core Tech (AI):** Missing -> **`Billing & Developer Payment APIs`**
* **Account Tier:** Missing -> **`Tier 2: Mid-Market Account`**

---

## 6. Database Schema (Supabase DDL)

```sql
CREATE TABLE public.enriched_b2b_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_name TEXT,
    country TEXT,
    website TEXT,
    employee_count INTEGER,
    lead_tier TEXT,
    industry TEXT,
    core_technology TEXT,
    market_segment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_leads_tier ON public.enriched_b2b_leads(lead_tier);
CREATE INDEX idx_leads_industry ON public.enriched_b2b_leads(industry);
```

---

## 7. System Limitations & Production Hardening

* **LLM Rate Limits:** Gemini free-tier endpoints require client-side rate throttling and exponential backoff under high-throughput batch loads.
* **Domain Validation:** The current pipeline performs syntax validation on web domains; future production iterations should incorporate live DNS MX record lookups to verify mailbox existence prior to DB insertion.