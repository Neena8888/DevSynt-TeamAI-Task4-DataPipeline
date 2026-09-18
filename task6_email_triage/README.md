# Autonomous AI Email Triage & RAG Assistant

**Developer:** Raheela Daud  
**Track:** Team AI - Task 6  
**Project Lead:** Usama  
**Deadline:** Saturday, 19 September 2026  
**Evaluation Status:** 10/10 Benchmark Tests Verified (100% Pass)  
**Demo Video:** [https://www.loom.com/share/02bddc446ad0450981bfcf7663f63a89](https://www.loom.com/share/02bddc446ad0450981bfcf7663f63a89)  
**LinkedIn Writeup:** [https://www.linkedin.com/in/your-post-here](https://www.linkedin.com/in/your-post-here)  

---

## 1. Executive Summary & Core Principles

An enterprise-grade autonomous email triage and response routing system built for **ApexHaven Properties**. The platform processes incoming corporate emails, strips boilerplate artifacts, applies structured zero-shot intent and priority classification via Google Gemini Flash, queries the persistent ChromaDB luxury real estate knowledge base for grounded answers, and deterministically routes non-generative tasks (HR recruitment, managerial escalations, scheduling, and spam filtering) to human stakeholders with Discord notification webhooks.

**Core Operational Principle:** *AI should not always answer. Autonomous generation is strictly constrained to domain facts; human-in-the-loop escalation is enforced for administrative, managerial, and critical communications.*

---

## 2. End-to-End System Architecture

```text
               [Incoming Email Intake: IMAP / API / Webhook]
                                     |
                                     v
                 [Body Cleaner & Thread Deduplication]
                  (Strips Signatures, Tracking, Quotes)
                                     |
                                     v
             [Structured Classifier: Intent + Priority Engine]
                       (Gemini Flash JSON Inference)
                                     |
                                     v
                         [Central Decision Engine]
                                     |
     +-------------------------------+-------------------------------+
     |                               |                               |
     v                               v                               v
[General / Sales Query]     [HR / Project / Urgent]         [Promotions / Spam]
     |                               |                               |
     v                               v                               v
[ChromaDB RAG Retrieval]   [Discord Webhook Alert Engine]  [Safe Deletion / Archive]
     |                     (#hr, #manager, #escalations)             |
     +-------+-------+               |                               v
     |               |               v                      [Mark Archived]
[Found in KB]   [Out of Scope]  [Human Routing]
     |               |
     v               v
[Auto-Reply]    [Safe Fallback +
                 Advisory Desk]
     |               |               |                               |
     +---------------+---------------+-------------------------------+
                                     |
                                     v
                  [SQLite Audit Trail & Logging Database]
                  (Message ID, Intent, RAG State, Timestamps)
```

---

## 3. Classification & Decision Matrix

| Category | Priority | Requires Human | Target Action | Routing Destination |
|---|---|:---:|---|---|
| `general_query` | Medium | No | `AUTO_REPLY_RAG` | Auto-dispatched reply via ChromaDB grounding |
| `sales_inquiry` | High | No / Conditional | `AUTO_REPLY_RAG` | In-scope spec retrieval; escalates on KB gap |
| `job_application` | High | Yes | `FORWARD_HR_AND_NOTIFY` | `hr@apexhavenproperties.com` + Discord HR channel |
| `project_related` | High | Yes | `FORWARD_MANAGER_AND_NOTIFY` | `manager@apexhavenproperties.com` + Discord alert |
| `meeting_request` | Medium | Yes | `NOTIFY_HUMAN_FOR_SCHEDULING` | Calendar desk; zero auto-booking without review |
| `urgent_request` | Critical | Yes | `IMMEDIATE_URGENT_HUMAN_ALERT` | Support escalations desk + Immediate Discord ping |
| `promotional` | Low | No | `ARCHIVED_AND_IGNORED` | Archived; completely isolated from employee inboxes |
| `spam` | Low | No | `ARCHIVED_AND_IGNORED` | Quarantined and purged; anti-phishing defense |

---

## 4. Key Engineering Modules

* **Artifact-Free Ingestion:** Regular expressions parse and strip signatures, reply headers, and mobile tags (`Sent from my iPhone`).
* **Duplicate Protection:** Cryptographic validation of `message_id` against SQLite index guarantees zero duplicate reprocessing.
* **Knowledge Base Reuse:** Integrates directly with Task 5 ChromaDB instance without duplicate embedding overhead.
* **Granular Audit Trail:** SQLite database (`logs/triage_logs.db`) maintains complete observability across all 14 execution fields.

---

## 5. Local Setup & Execution Guide

### Prerequisites
* Python 3.11+
* Gemini API Key

### Installation
```bash
cd task6_email_triage
pip install fastapi uvicorn google-genai chromadb pydantic python-dotenv requests
```

### Environment Configuration
Configure `.env` in the working directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DISCORD_HR_WEBHOOK=[https://discord.com/api/webhooks/](https://discord.com/api/webhooks/)...
DISCORD_MGR_WEBHOOK=[https://discord.com/api/webhooks/](https://discord.com/api/webhooks/)...
DISCORD_URGENT_WEBHOOK=[https://discord.com/api/webhooks/](https://discord.com/api/webhooks/)...
```

### Running Test Verification Suite
```bash
python3 run_tests.py
```

---

## 6. Evaluation Benchmark Results

All 10 required project scenarios were verified with zero regressions:

| # | Scenario | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|:---:|
| 1 | General knowledge query | RAG answer + email reply | 5.0% fee extracted and auto-replied | **PASS** |
| 2 | Unknown question | Safe response + Human escalation | Refused hallucination; routed to advisory | **PASS** |
| 3 | Job application | Forward to HR + Discord alert | Formatted alert sent; hiring decision blocked | **PASS** |
| 4 | Project email | Forward to Manager + Discord alert | Budget/timeline change routed to Manager | **PASS** |
| 5 | Meeting request | Human routing for scheduling | Blocked auto-booking; sent to calendar desk | **PASS** |
| 6 | Critical client issue | High-priority escalation | Triggered critical Discord alert + fast triage | **PASS** |
| 7 | Promotional email | Delete/archive | Safely archived without forwarding | **PASS** |
| 8 | Spam | Quarantine/spam handling | Phishing attempt archived and logged | **PASS** |
| 9 | Sales inquiry | RAG retrieval of specs | APX-101 $4,850,000 price retrieved and sent | **PASS** |
| 10 | Follow-up email | Thread continuity | Identified dual agency ban from context | **PASS** |
