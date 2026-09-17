# Task 6 — AI Email Triage & RAG Assistant: Benchmark Evaluation Report

**Developer:** Raheela Daud  
**Track:** Team AI - Task 6  
**Project Lead:** Usama  
**Evaluation Date:** September 2026  
**Status:** 10 / 10 Scenarios VERIFIED (100% PASS RATE)  

---

## 1. Evaluation Matrix (10 Required Scenarios)

| # | Test Scenario | Incoming Subject | Classified Category | System Action Taken | Expected Result | Status |
|---|---|---|---|---|---|:---:|
| 1 | General knowledge query | Inquiry regarding standard residential seller fees | `general_query` | `AUTO_REPLY_RAG` | RAG answer + email reply | **PASS** |
| 2 | Unknown question | Properties in Dubai Marina & refund guidelines | `general_query` | `ESCALATE_TO_HUMAN_UNKNOWN_QUERY` | No hallucination + human review / safe response | **PASS** |
| 3 | Job application | Application for AI Intern / Machine Learning Role | `job_application` | `FORWARD_HR_AND_NOTIFY` | Forward to HR + Discord notification | **PASS** |
| 4 | Project email | Scope change & deadline update for APX-101 remodeling | `project_related` | `FORWARD_MANAGER_AND_NOTIFY` | Forward to Manager + Discord notification | **PASS** |
| 5 | Meeting request | Request for Zoom call: Exclusive escrow API partnership | `meeting_request` | `NOTIFY_HUMAN_FOR_SCHEDULING` | Human routing/notification | **PASS** |
| 6 | Critical client issue | CRITICAL: Earnest money deposit transfer failure & escrow block | `urgent_request` | `IMMEDIATE_URGENT_HUMAN_ALERT` | High-priority notification + human handling | **PASS** |
| 7 | Promotional email | Get 50,000 High Net Worth Real Estate Leads for $99! | `promotional` | `ARCHIVED_AND_IGNORED` | Delete/archive | **PASS** |
| 8 | Spam | Claim your $5,000 Bitcoin disbursement voucher now | `spam` | `ARCHIVED_AND_IGNORED` | Spam handling | **PASS** |
| 9 | Sales inquiry | Specifications and pricing for listing APX-101 | `sales_inquiry` | `AUTO_REPLY_RAG` | RAG response if answer exists; otherwise human escalation | **PASS** |
| 10 | Follow-up email | Re: Inquiry regarding standard residential seller fees | `general_query` | `AUTO_REPLY_RAG` | Correct handling of conversation context | **PASS** |

---

## 2. Granular Scenario Analysis & Grounding Transcripts

### Scenario 1: General Knowledge Query
* **Input Query:** Standard residential seller representation commission rate inquiry.
* **System Action:** RAG vector search executed against `3_Services_and_Fees.pdf`.
* **Grounded Answer:** Directly identified 5.0% gross fee structure and drafted a professional response.

### Scenario 2: Unknown Question (Negative Guardrail)
* **Input Query:** Inquiring about luxury property refund policies in Dubai / London.
* **System Action:** Zero-hallucination guardrail detected out-of-scope domain. Prevented fabrication and safely escalated query to human real-estate advisory desk.

### Scenario 3: Job Application
* **Input Query:** AI internship resume submission from ML candidate.
* **System Action:** Classified as `job_application`, marked `requires_human=True`, forwarded to HR desk, and dispatched Discord notification. Zero AI hiring decisions taken.

### Scenario 4: Project Scope & Budget Change
* **Input Query:** Foundation delay notification and $25,000 budget extension request for APX-101.
* **System Action:** Classified as `project_related`, prioritized as high/managerial, and forwarded to Project Manager with Discord notification.

### Scenario 5: Meeting Scheduling Request
* **Input Query:** Partnership Zoom demonstration inquiry for Tuesday 2 PM.
* **System Action:** Human-in-the-loop enforced (`requires_human=True`). Auto-scheduling blocked; routed to human booking calendar desk.

### Scenario 6: Critical Client Dispute
* **Input Query:** Wire transfer failure on earnest money deposit ($150,000) for APX-102.
* **System Action:** Prioritized as `CRITICAL`, dispatched high-urgency Discord embed alert, and routed to escalations desk immediately.

### Scenario 7 & 8: Marketing Promotion & Spam
* **Input Query:** Unsolicited marketing database sales & crypto voucher phishing.
* **System Action:** Categorized as `promotional` / `spam` and safely archived without forwarding to internal staff mailboxes.

### Scenario 9: High-Value Numerical Sales Inquiry
* **Input Query:** Price, square footage, bed, and bath inquiry for APX-101.
* **System Action:** RAG retrieval extracted $4,850,000 USD, 6,400 sq.ft, 5 beds, and 6 baths from `2_Property_Listings.pdf`.

### Scenario 10: Follow-Up Thread & Context Continuity
* **Input Query:** Thread follow-up on dual agency representation.
* **System Action:** Identified previous subject thread context, executed RAG retrieval against `4_Frequently_Asked_Questions.pdf`, confirming dual agency prohibition under California regulatory compliance.

---

## 3. Database Audit Trail Verification

All 10 executions were automatically persisted into local SQLite storage (`logs/triage_logs.db`) with message IDs, category tags, human escalation flags, RAG indicators, and Discord webhook dispatch statuses.
