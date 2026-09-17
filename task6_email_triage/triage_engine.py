import os
import re
import json
from typing import Dict, Any
import requests
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from google import genai
import database

load_dotenv()
database.init_db()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env!")

client = genai.Client(api_key=GEMINI_API_KEY)

# Task 5 ChromaDB Path (Symlink or Direct relative path)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(CURRENT_DIR, "chroma_db")
if not os.path.exists(DB_DIR):
    DB_DIR = os.path.join(CURRENT_DIR, "..", "task5_rag", "chroma_db")

chroma_client = chromadb.PersistentClient(path=DB_DIR)
emb_fn = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_or_create_collection(
    name="apex_real_estate_knowledge",
    embedding_function=emb_fn
)

DISCORD_HR_WEBHOOK = os.getenv("DISCORD_HR_WEBHOOK", "")
DISCORD_MGR_WEBHOOK = os.getenv("DISCORD_MGR_WEBHOOK", "")
DISCORD_URGENT_WEBHOOK = os.getenv("DISCORD_URGENT_WEBHOOK", "")

def clean_email_body(body: str) -> str:
    """Strips signatures, tracking lines, and reply quotes."""
    text = re.split(r'(--\s*|Best regards|Sincerely|Thanks,|Sent from my iPhone|On .* wrote:)', body, flags=re.IGNORECASE)[0]
    return text.strip()

def send_discord_notification(webhook_url: str, title: str, description: str, fields: list) -> str:
    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": 15158332 if "CRITICAL" in title or "URGENT" in title else 3447003,
            "fields": fields
        }]
    }
    if webhook_url and webhook_url.startswith("http"):
        try:
            res = requests.post(webhook_url, json=payload, timeout=5)
            return "Sent (200)" if res.status_code == 204 else f"Failed ({res.status_code})"
        except Exception as e:
            return f"Error ({str(e)})"
    return "Mocked / Dispatched to Console"

def query_rag_knowledge(query: str, top_k: int = 8) -> Dict[str, Any]:
    results = collection.query(query_texts=[query], n_results=top_k)
    retrieved_docs = results["documents"][0] if results["documents"] else []
    retrieved_metas = results["metadatas"][0] if results["metadatas"] else []

    if not retrieved_docs:
        return {"answer": "The information could not be found in the uploaded documents.", "sources": []}

    context_blocks = []
    sources = []
    for doc_text, meta in zip(retrieved_docs, retrieved_metas):
        source_label = f"{meta['doc_name']} — Page {meta['page']}"
        context_blocks.append(f"[{source_label}]\n{doc_text}")
        if source_label not in sources:
            sources.append(source_label)

    prompt = f"""You are the AI Email Assistant for ApexHaven Properties.
Answer the sender's question professionally using ONLY the provided context.
If the information is missing or out-of-scope, respond strictly with:
"The information could not be found in the uploaded documents."

CONTEXT:
{chr(10).join(context_blocks)}

EMAIL QUERY:
{query}

PROFESSIONAL EMAIL REPLY:"""

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        ans = response.text.strip()
    except Exception as e:
        ans = f"Error: {str(e)}"

    return {"answer": ans, "sources": sources if "could not be found" not in ans else []}

def classify_email(sender: str, subject: str, body: str) -> Dict[str, Any]:
    clean_body = clean_email_body(body)
    classification_prompt = f"""Classify this email for ApexHaven Properties (Luxury Real Estate) into JSON.
Return ONLY a valid JSON markdown block with keys: category, priority, requires_human, action.

Categories: general_query, sales_inquiry, job_application, project_related, internal_communication, meeting_request, urgent_request, complaint, promotional, spam, other
Priorities: low, medium, high, critical
Actions: rag_reply, human_review, forward_and_notify_hr, forward_and_notify_manager, immediate_urgent_alert, delete_or_archive

Rules:
1. Job applicants/interns -> category='job_application', priority='high', requires_human=true, action='forward_and_notify_hr'.
2. Budget changes, technical updates, foundation delays -> category='project_related', priority='high', requires_human=true, action='forward_and_notify_manager'.
3. Call/Zoom requests -> category='meeting_request', priority='medium', requires_human=true, action='human_review'.
4. Wire failures, escrow blocks, urgent issues -> category='urgent_request', priority='critical', requires_human=true, action='immediate_urgent_alert'.
5. Marketing deals, cheap leads -> category='promotional', priority='low', requires_human=false, action='delete_or_archive'.
6. Free vouchers, random lottery, unverified links -> category='spam', priority='low', requires_human=false, action='delete_or_archive'.
7. Questions about property prices/specs -> category='sales_inquiry', priority='high', requires_human=false, action='rag_reply'.
8. Standard commission/fee questions or thread follow-ups -> category='general_query', priority='medium', requires_human=false, action='rag_reply'.

EMAIL:
From: {sender}
Subject: {subject}
Body: {clean_body}"""

    try:
        res = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=classification_prompt,
        )
        raw_text = res.text.strip()
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as err:
        print(f"DEBUG Classification Error: {err}")

    # Fallback heuristic if API quota or syntax hiccups occur
    lowered = (subject + " " + clean_body).lower()
    if "intern" in lowered or "resume" in lowered or "job" in lowered:
        return {"category": "job_application", "priority": "high", "requires_human": True, "action": "forward_and_notify_hr"}
    elif "scope" in lowered or "deadline" in lowered or "budget" in lowered:
        return {"category": "project_related", "priority": "high", "requires_human": True, "action": "forward_and_notify_manager"}
    elif "meeting" in lowered or "zoom" in lowered or "schedule" in lowered:
        return {"category": "meeting_request", "priority": "medium", "requires_human": True, "action": "human_review"}
    elif "critical" in lowered or "urgent" in lowered or "wire transfer" in lowered:
        return {"category": "urgent_request", "priority": "critical", "requires_human": True, "action": "immediate_urgent_alert"}
    elif "marketing" in lowered or "leads" in lowered:
        return {"category": "promotional", "priority": "low", "requires_human": False, "action": "delete_or_archive"}
    elif "bitcoin" in lowered or "voucher" in lowered or "wallet" in lowered:
        return {"category": "spam", "priority": "low", "requires_human": False, "action": "delete_or_archive"}
    elif "apx-101" in lowered or "pricing" in lowered:
        return {"category": "sales_inquiry", "priority": "high", "requires_human": False, "action": "rag_reply"}
    else:
        return {"category": "general_query", "priority": "medium", "requires_human": False, "action": "rag_reply"}

def process_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    msg_id = email_data["message_id"]
    if database.is_duplicate(msg_id):
        return {"status": "SKIPPED", "reason": f"Duplicate email message_id {msg_id} already processed."}

    sender = email_data.get("sender", "")
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    clean_body = clean_email_body(body)

    classification = classify_email(sender, subject, clean_body)
    category = classification.get("category", "other")
    priority = classification.get("priority", "medium")
    action = classification.get("action", "human_review")
    requires_human = classification.get("requires_human", False)

    response_text = ""
    discord_status = "Skipped"
    forwarded_to = "None"
    rag_used = False

    if action == "delete_or_archive" or category in ["promotional", "spam"]:
        response_text = "N/A - Email marked as promotional/spam and safely archived."
        action_taken = "ARCHIVED_AND_IGNORED"

    elif category in ["general_query", "sales_inquiry"] or action == "rag_reply":
        rag_res = query_rag_knowledge(clean_body)
        rag_used = True
        if "could not be found" in rag_res["answer"]:
            requires_human = True
            action_taken = "ESCALATE_TO_HUMAN_UNKNOWN_QUERY"
            response_text = "Thank you for reaching out to ApexHaven Properties. Your request has been routed to our senior advisory desk as this information requires specialist review."
            discord_status = send_discord_notification(
                DISCORD_MGR_WEBHOOK,
                "⚠️ Knowledge Base Gap / Safe Fallback",
                f"Query could not be answered from KB.\n**Sender:** {sender}",
                [{"name": "Subject", "value": subject}, {"name": "Query", "value": clean_body}]
            )
        else:
            action_taken = "AUTO_REPLY_RAG"
            response_text = rag_res["answer"]

    elif category == "job_application" or action == "forward_and_notify_hr":
        forwarded_to = "hr@apexhavenproperties.com"
        action_taken = "FORWARD_HR_AND_NOTIFY"
        discord_status = send_discord_notification(
            DISCORD_HR_WEBHOOK,
            "⚠️ New Job Application",
            f"**Candidate:** {sender}\n**Role/Subject:** {subject}\n**Priority:** {priority.upper()}",
            [{"name": "Status", "value": "Forwarded to HR department for resume screening."}]
        )
        response_text = "Application received and routed to human resource team."

    elif category in ["project_related", "internal_communication"] or action == "forward_and_notify_manager":
        forwarded_to = "manager@apexhavenproperties.com"
        action_taken = "FORWARD_MANAGER_AND_NOTIFY"
        discord_status = send_discord_notification(
            DISCORD_MGR_WEBHOOK,
            "📋 Project Update / Decision Required",
            f"**From:** {sender}\n**Subject:** {subject}",
            [{"name": "Priority", "value": priority.upper()}, {"name": "Action Required", "value": "Manager review requested."}]
        )
        response_text = "Forwarded to project manager for approval."

    elif category in ["urgent_request", "complaint"] or priority == "critical" or action == "immediate_urgent_alert":
        forwarded_to = "escalations@apexhavenproperties.com"
        action_taken = "IMMEDIATE_URGENT_HUMAN_ALERT"
        discord_status = send_discord_notification(
            DISCORD_URGENT_WEBHOOK,
            "🚨 CRITICAL / URGENT ESCALATION",
            f"**From:** {sender}\n**Subject:** {subject}\n**Priority:** CRITICAL",
            [{"name": "Body Excerpt", "value": clean_body[:300]}]
        )
        response_text = "Priority escalation dispatched to support management."

    elif category == "meeting_request":
        forwarded_to = "scheduling@apexhavenproperties.com"
        action_taken = "NOTIFY_HUMAN_FOR_SCHEDULING"
        discord_status = send_discord_notification(
            DISCORD_MGR_WEBHOOK,
            "📅 Meeting Request Received",
            f"**Sender:** {sender}\n**Subject:** {subject}",
            [{"name": "Note", "value": "Awaiting human agent calendar confirmation."}]
        )
        response_text = "Meeting request logged for human representative confirmation."

    else:
        action_taken = "GENERAL_HUMAN_REVIEW"
        response_text = "Routed for manual human triage."

    log_payload = {
        "message_id": msg_id,
        "thread_id": email_data.get("thread_id", msg_id),
        "sender": sender,
        "subject": subject,
        "category": category,
        "priority": priority,
        "requires_human": requires_human,
        "action_taken": action_taken,
        "rag_used": rag_used,
        "response_body": response_text,
        "forwarded_to": forwarded_to,
        "discord_status": discord_status,
        "execution_status": "SUCCESS"
    }
    database.log_email(log_payload)

    return {
        "message_id": msg_id,
        "category": category,
        "priority": priority,
        "requires_human": requires_human,
        "action_taken": action_taken,
        "rag_used": rag_used,
        "response_body": response_text,
        "discord_status": discord_status
    }