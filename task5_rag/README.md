# Autonomous Real Estate Knowledge Engine & Document RAG System

**Developer:** Raheela Daud  
**Track:** Team AI - Task 5  
**Project Lead:** Usama  
**Status:** Production-Ready   

**Demo Video:** [https://www.loom.com/share/7a6f36f9f0914efc9342ae198c876413](https://www.loom.com/share/7a6f36f9f0914efc9342ae198c876413) 

**LinkedIn Writeup:** [https://lnkd.in/p/dkvuXNs9](https://lnkd.in/p/dkvuXNs9)  

---

## 1. Executive Summary & System Architecture

An enterprise-grade, retrieval-augmented generation (RAG) platform engineered for fictional luxury real estate firm **ApexHaven Properties**. The system ingests multi-format corporate records (PDF, DOCX, TXT), executes page-level text extraction and sliding-window chunking, indexes vector representations into a local persistent ChromaDB store, and delivers grounded question-answering powered by Google Gemini Flash with strict zero-hallucination guardrails.

```text
[User Document: PDF / DOCX / TXT]
       |
       v
[Page-Level Text Extraction & Cleaning (PyPDF / python-docx)]
       |
       v
[Sliding-Window Chunking (500 chars, 80 overlap + Page Metadata)]
       |
       v
[ChromaDB Vector Store (MiniLM Local Persistent Embeddings)]
       |
       v
[User Query Retrieval: Top-K Vector Search]
       |
       v
[Context Assembly + Zero-Extrapolation Guardrail Prompt]
       |
       v
[Gemini Flash LLM (gemini-3.6-flash)] -> [Grounded Answer + Page Citations] -> [Web Dashboard]
```

---

## 2. Dataset Selection & Ingestion Rationale

* **Domain Selected:** Luxury Real Estate Brokerage & Institutional Asset Management (**ApexHaven Properties**).
* **Ingestion Corpus:** 5 curated corporate documents simulating complex operational records:
  1. `1_Company_Overview.pdf` - Corporate profile, executive leadership, transaction history, licensing.
  2. `2_Property_Listings.pdf` - High-value residential and commercial assets with precise numerical specs.
  3. `3_Services_and_Fees.pdf` - Tiered commission structures, buyer retainers, and management fees.
  4. `4_Frequently_Asked_Questions.pdf` - Strict regulatory policies (EMD requirements, Dual Agency prohibitions).
  5. `5_Policies_and_Terms.pdf` - FinCEN AML disclosures, escrow guidelines, and termination agreements.
* **Why Selected:** Real-world enterprise RAG systems must process dense legal clauses, precise financial percentages, and cross-document dependencies without inventing figures.

---

## 3. Core Engineering & Capabilities

* **Multi-Format Ingestion:** Native text extraction supporting `.pdf`, `.docx`, and `.txt` files with automated page-number tracking.
* **Token-Aware Chunking:** Sliding-window algorithm that embeds document identity, chunk ID, and exact page numbers directly into vector metadata.
* **Persistent Vector Store:** ChromaDB instance utilizing local MiniLM embeddings for sub-second semantic retrieval.
* **Deterministic Anti-Hallucination Guardrail:** Zero-tolerance prompt conditioning. If requested information is outside the indexed documents, the system strictly outputs:  
  `"The information could not be found in the uploaded documents."`
* **Precise Citation Formatting:** Outputs exact file name and page provenance for every factual statement.
* **Operations Dashboard:** Fast and responsive web UI featuring real-time corpus counters, document ingestion dropzone, deletion/re-processing hooks, and chat history.

---

## 4. Technology Stack & Dependencies

* **Backend Framework:** FastAPI, Uvicorn (ASGI)
* **Vector Store & Embeddings:** ChromaDB (Local Persistent)
* **Inference Model:** Google Gemini Flash (`gemini-3.6-flash`) via `google-genai`
* **Parsing Utilities:** PyPDF, python-docx, ReportLab
* **Frontend UI:** HTML5, Tailwind CSS, FontAwesome

---

## 5. Local Setup & Execution Guide

### Prerequisites
Ensure Python 3.11+ is installed in your local environment.

### Step 1: Navigate to Workspace
```bash
cd task5_rag
```

### Step 2: Install Required Packages
```bash
pip install fastapi uvicorn chromadb reportlab pypdf python-docx google-genai python-dotenv
```

### Step 3: Configure Environment Variables
Ensure a `.env` file exists in the directory with your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 4: Generate Evaluation Dataset
```bash
python3 create_docs.py
```

### Step 5: Start Backend Application & Dashboard
```bash
uvicorn main:app --reload --port 8000
```
Open your browser at `http://127.0.0.1:8000` to interact with the system.

---

## 6. Evaluation Matrix & Verification Results

The pipeline was validated against a 10-query benchmark testing direct retrieval, multi-document synthesis, and negative-constraint guardrail activation:

| # | Query Category | User Prompt | System Behavior | Status |
|---|---|---|---|:---:|
| 1 | Direct Retrieval | Who is the CEO of ApexHaven Properties and what is his background? | Returns Marcus Vance details from Company Overview (Page 1) | **PASS** |
| 2 | Numerical Property Specs | What are the specifications and price of Listing APX-101? | Returns $4,850,000 USD, 5 beds, 6 baths, 6,400 sq.ft (Page 1) | **PASS** |
| 3 | Fee Extraction | What is the standard residential seller representation commission rate? | Extracts exact 5.0% gross fee structure (Page 1) | **PASS** |
| 4 | Policy Inquiry | What is the required earnest money deposit (EMD)? | Returns 3.0% residential and 5.0% commercial within 2 days (Page 1) | **PASS** |
| 5 | Cross-Doc Synthesis | Does ApexHaven allow Dual Agency, and who manages private clients? | Synthesizes FAQ prohibition with Leadership bio (Pages 1 & 1) | **PASS** |
| 6 | Cross-Doc Reasoning | What are the showing rules over $2.5M, and does APX-102 qualify? | Correlates FAQ $2.5M threshold with APX-102 $3.25M price | **PASS** |
| 7 | Legal Governance | What expenses must be reimbursed if an exclusive agreement is cancelled? | Extracts $3,500 expense cap and 90-day protection period | **PASS** |
| 8 | Negative Guardrail | What is the refund policy for residential properties in Dubai or London? | Refuses outside domain, outputs exact missing info notice | **PASS** |
| 9 | Negative Guardrail | Who is the Chief Financial Officer (CFO) of ApexHaven Properties? | Refuses hallucination of unlisted role, outputs exact notice | **PASS** |
| 10 | Negative Guardrail | What mortgage rates are currently offered by Bank of America? | Rejects external bank query, outputs exact notice | **PASS** |

*Complete raw outputs and grounding transcripts are documented in [`README.md`](./README.md).*
