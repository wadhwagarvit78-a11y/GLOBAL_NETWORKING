from fastapi import FastAPI, Request, Form, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import csv
import io
import traceback
import urllib.parse
from pathlib import Path

from database import init_db
import models

# Initialize Database
init_db()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="TrustHub Networking — Verified Business & Client Solutions")
app.add_middleware(SessionMiddleware, secret_key="trusthub-prod-session-v2-2026")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    err_trace = f"RENDER EXCEPTION: {exc}\n\n{traceback.format_exc()}"
    print(err_trace)
    return PlainTextResponse(err_trace, status_code=500)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# PWA Root Endpoints
@app.get("/manifest.json")
async def get_manifest():
    return FileResponse(str(BASE_DIR / "static" / "manifest.json"), media_type="application/manifest+json")

@app.get("/sw.js")
async def get_sw():
    return FileResponse(str(BASE_DIR / "static" / "sw.js"), media_type="application/javascript")

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        user = models.get_user_by_id(user_id)
        if user:
            return user
    return None


# 1. Homepage (Universal / Vertical-Agnostic with Motto & 5 Advantages)
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    groups = models.get_all_active_groups()
    current_user = get_current_user(request)
    return templates.TemplateResponse(request=request, name="index.html", context={
        "groups": groups,
        "current_user": current_user
    })

# 2. Dedicated Onboard Page
@app.get("/onboard", response_class=HTMLResponse)
async def onboard_page(request: Request, group_id: int = None):
    groups = models.get_all_active_groups()
    current_user = get_current_user(request)
    return templates.TemplateResponse(request=request, name="onboard.html", context={
        "groups": groups,
        "selected_group_id": group_id,
        "current_user": current_user
    })

# 3. Handle Onboarding & Direct Redirect to Official WhatsApp Group
@app.post("/onboard", response_class=HTMLResponse)
async def handle_onboard(
    request: Request,
    group_id: int = Form(...),
    full_name: str = Form(...),
    whatsapp_number: str = Form(...),
    city_area: str = Form(...),
    business_name: str = Form(""),
    years_experience: int = Form(1),
    rera_or_license_id: str = Form(""),
    source_channel: str = Form("Direct")
):
    user_id = models.create_user_onboard(
        full_name=full_name,
        phone_number=whatsapp_number,
        whatsapp_number=whatsapp_number,
        group_id=group_id,
        city_area=city_area,
        business_name=business_name,
        years_experience=years_experience,
        rera_or_license_id=rera_or_license_id,
        source_channel=source_channel
    )
    request.session["user_id"] = user_id
    user = models.get_user_by_id(user_id)
    group = models.get_group_by_id(group_id)
    
    # Render instant WhatsApp redirection page with countdown & direct join link
    return templates.TemplateResponse(request=request, name="whatsapp_redirect.html", context={
        "user": user,
        "group": group,
        "current_user": user
    })

# 4. Member's Dedicated Feed Dashboard (Dual Mode: B2B Lead Feed & B2B2C Client Solutions)
@app.get("/app", response_class=HTMLResponse)
async def member_dashboard(
    request: Request,
    mode: str = "b2b",
    location: str = None,
    deal_type: str = None,
    search: str = None
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/onboard", status_code=302)
        
    group_id = current_user.get("group_id") or 1
    group = models.get_group_by_id(group_id)
    leads = models.get_leads_for_group(group_id, sub_location=location, deal_type=deal_type, search=search)
    b2b2c_inquiries = models.get_b2b2c_inquiries(user_id=current_user.get("id"), user_phone=current_user.get("phone_number"))
    
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "current_user": current_user,
        "group": group,
        "leads": leads,
        "b2b2c_inquiries": b2b2c_inquiries,
        "mode": mode,
        "location": location,
        "deal_type": deal_type,
        "search": search
    })

@app.get("/b2b")
async def b2b_redirect():
    return RedirectResponse(url="/app?mode=b2b", status_code=302)

@app.get("/b2b2c")
async def b2b2c_redirect():
    return RedirectResponse(url="/app?mode=b2b2c", status_code=302)

# 5. Post Lead
@app.get("/post-lead", response_class=HTMLResponse)
async def post_lead_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    group_id = current_user.get("group_id") or 1
    group = models.get_group_by_id(group_id)
    return templates.TemplateResponse(request=request, name="post_lead.html", context={
        "current_user": current_user,
        "group": group
    })

@app.post("/post-lead")
async def handle_post_lead(
    request: Request,
    title: str = Form(...),
    deal_type: str = Form(...),
    sub_location: str = Form(...),
    budget_range: str = Form(...),
    description: str = Form(...),
    expected_commission: str = Form("")
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    group_id = current_user.get("group_id") or 1
    lead_id = models.create_lead(
        author_id=current_user["id"],
        group_id=group_id,
        title=title,
        deal_type=deal_type,
        sub_location=sub_location,
        budget_range=budget_range,
        description=description,
        expected_commission=expected_commission
    )
    return RedirectResponse(url=f"/leads/{lead_id}?submitted=pending", status_code=302)

# 6. Lead Detail & 1-Click WhatsApp Handoff
@app.get("/leads/{lead_id}", response_class=HTMLResponse)
async def lead_detail_page(request: Request, lead_id: int, submitted: str = None):
    current_user = get_current_user(request)
    lead = models.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return templates.TemplateResponse(request=request, name="lead_detail.html", context={
        "current_user": current_user,
        "lead": lead,
        "submitted": submitted
    })

@app.post("/leads/claim/{lead_id}")
async def handle_claim_lead(request: Request, lead_id: int):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    lead = models.get_lead_by_id(lead_id)
    if lead and lead["status"] == "open":
        models.claim_lead(lead_id, current_user["id"])
        
        # Direct WhatsApp Handoff Link
        author_wa = lead["author_whatsapp"]
        token = lead["lead_token"]
        title = lead["title"]
        msg = f"Hi {lead['author_name']}, I claimed your requirement {token} ({title}) on TrustHub Networking. Let's coordinate the deal!"
        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{author_wa}?text={encoded_msg}"
        return RedirectResponse(url=wa_url, status_code=302)
        
    return RedirectResponse(url=f"/leads/{lead_id}", status_code=302)

# 7. Close Deal & Log Platform Commission
@app.post("/leads/close/{lead_id}")
async def handle_close_deal(
    request: Request,
    lead_id: int,
    deal_value: float = Form(...),
    commission_earned: float = Form(...)
):
    models.close_lead_deal(lead_id, deal_value, commission_earned)
    return RedirectResponse(url="/ledger", status_code=302)

# 8. Commission Ledger
@app.get("/ledger", response_class=HTMLResponse)
async def ledger_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    ledger_entries = models.get_commission_ledger(current_user["id"])
    return templates.TemplateResponse(request=request, name="ledger.html", context={
        "current_user": current_user,
        "ledger_entries": ledger_entries
    })

@app.post("/ledger/submit-proof")
async def handle_submit_proof(
    request: Request,
    ledger_id: int = Form(...),
    proof_ref: str = Form(...),
    notes: str = Form("")
):
    models.submit_payment_proof(ledger_id, proof_ref, notes)
# 8b. Cross-Vertical Service Request (E.g. Lawyer needing property or dealer needing trip)
@app.post("/cross-referral")
async def handle_cross_referral(
    request: Request,
    target_service: str = Form(...),
    requirement_details: str = Form(...),
    budget_range: str = Form(""),
    user_name: str = Form(None),
    user_phone: str = Form(None)
):
    current_user = get_current_user(request)
    uid = current_user["id"] if current_user else None
    uname = user_name or (current_user["full_name"] if current_user else "Guest")
    uphone = user_phone or (current_user["phone_number"] if current_user else "")
    uprof = (current_user["group_name"] if current_user else "Direct Client")
    
    models.create_cross_vertical_request(
        user_id=uid,
        user_name=uname,
        user_phone=uphone,
        user_profession=uprof,
        target_service=target_service,
        requirement_details=requirement_details,
        budget_range=budget_range
    )
    if uphone:
        request.session["client_phone"] = uphone
    if user_name:
        return RedirectResponse(url="/client-portal?submitted=1", status_code=302)
    return RedirectResponse(url="/app?cross_success=1", status_code=302)

# 8b. Dedicated Client Solutions Portal (B2B2C Dashboard)
@app.get("/client-portal", response_class=HTMLResponse)
async def client_portal_page(request: Request, submitted: int = None):
    current_user = get_current_user(request)
    client_phone = request.session.get("client_phone")
    user_id = current_user.get("id") if current_user else None
    phone = (current_user.get("phone_number") if current_user else None) or client_phone
    
    inquiries = models.get_b2b2c_inquiries(user_id=user_id, user_phone=phone) if (user_id or phone) else []
    return templates.TemplateResponse(request=request, name="client_portal.html", context={
        "current_user": current_user,
        "inquiries": inquiries,
        "submitted": submitted
    })


# 9. Subscription & Trial
@app.get("/subscription", response_class=HTMLResponse)
async def subscription_page(request: Request):
    current_user = get_current_user(request)
    return templates.TemplateResponse(request=request, name="subscription.html", context={
        "current_user": current_user
    })

@app.post("/subscription/activate")
async def handle_subscription_activate(request: Request):
    return RedirectResponse(url="/app", status_code=302)

import hashlib
import secrets

# Secure Admin Auth: Loaded from Environment Variable or verified against a salted PBKDF2 cryptographic hash
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Trusthub admin")
DEFAULT_HASH = "c1c0b0757ede62fc7ca20d9472e4171a:23e204ffa7ce0a77d83518977e733461fb7343910dee5c0d3c8a0c6a01366f01"
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", DEFAULT_HASH)

def verify_admin_password(provided_password: str) -> bool:
    env_plain = os.getenv("ADMIN_PASSWORD")
    if env_plain and secrets.compare_digest(provided_password.strip(), env_plain.strip()):
        return True
    try:
        salt_hex, key_hex = ADMIN_PASSWORD_HASH.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        derived = hashlib.pbkdf2_hmac("sha256", provided_password.strip().encode("utf-8"), salt, 100000)
        return secrets.compare_digest(derived, key)
    except Exception:
        return False

def is_admin(request: Request) -> bool:
    if request.session.get("is_admin") is True:
        return True
    user = get_current_user(request)
    if user and user.get("role") == "admin":
        return True
    return False

# 10. Admin Login & Control Center
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, error: str = None):
    if is_admin(request):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse(request=request, name="admin_login.html", context={
        "username": ADMIN_USERNAME,
        "error": error
    })

@app.post("/admin/login")
async def handle_admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_match = secrets.compare_digest(username.strip().lower(), ADMIN_USERNAME.lower())
    pass_match = verify_admin_password(password)
    
    if user_match and pass_match:
        request.session["is_admin"] = True
        request.session["user_id"] = 1  # Trusthub admin user ID
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse(request=request, name="admin_login.html", context={
        "username": username,
        "error": "Invalid username or password. Access denied."
    }, status_code=401)


@app.get("/admin/logout")
async def handle_admin_logout(request: Request):
    request.session.pop("is_admin", None)
    return RedirectResponse(url="/", status_code=302)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, tab: str = None, approved: int = None, rejected: int = None):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    current_user = get_current_user(request)
    metrics = models.get_admin_metrics()
    
    approved_lead_token = request.session.pop("approved_lead_token", None)
    approved_lead_group = request.session.pop("approved_lead_group", None)
    broadcast_text = request.session.pop("broadcast_text", None)
    whatsapp_send_url = request.session.pop("whatsapp_send_url", None)
    group_link = request.session.pop("group_link", None)
    
    return templates.TemplateResponse(request=request, name="admin.html", context={
        "current_user": current_user,
        "metrics": metrics,
        "active_tab": tab,
        "approved": approved,
        "rejected": rejected,
        "approved_lead_token": approved_lead_token,
        "approved_lead_group": approved_lead_group,
        "broadcast_text": broadcast_text,
        "whatsapp_send_url": whatsapp_send_url,
        "group_link": group_link
    })

@app.post("/admin/leads/approve/{lead_id}")
async def handle_admin_approve_lead(request: Request, lead_id: int):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    lead = models.approve_lead(lead_id)
    if lead:
        broadcast_text = models.format_whatsapp_broadcast_message(lead)
        encoded_text = urllib.parse.quote(broadcast_text)
        group_link = lead.get("whatsapp_group_link") or ""
        request.session["approved_lead_token"] = lead.get("lead_token")
        request.session["approved_lead_group"] = lead.get("group_name")
        request.session["broadcast_text"] = broadcast_text
        request.session["whatsapp_send_url"] = f"https://api.whatsapp.com/send?text={encoded_text}"
        request.session["group_link"] = group_link
    return RedirectResponse(url="/admin?tab=approvals&approved=1", status_code=302)

@app.post("/admin/leads/reject/{lead_id}")
async def handle_admin_reject_lead(request: Request, lead_id: int):
    if not is_admin(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    models.reject_lead(lead_id)
    return RedirectResponse(url="/admin?tab=approvals&rejected=1", status_code=302)


@app.post("/admin/update-group-link")
async def handle_update_group_link(
    group_id: int = Form(...),
    whatsapp_group_link: str = Form(...),
    monthly_fee: int = Form(None)
):
    models.update_group_whatsapp_link(group_id, whatsapp_group_link, monthly_fee)
    return RedirectResponse(url="/admin", status_code=302)

@app.post("/admin/verify-payment/{ledger_id}")
async def handle_verify_payment(ledger_id: int):
    models.verify_commission_payment(ledger_id)
    return RedirectResponse(url="/admin", status_code=302)

# 10b. Export Members Directory to CSV / Excel
@app.get("/admin/export-members-csv")
async def export_members_csv():
    members = models.get_all_members_for_export()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow([
        "Member ID", 
        "Full Name", 
        "Company / Business Name", 
        "WhatsApp Number", 
        "Calling Phone", 
        "Profession Circle", 
        "City / Operating Region", 
        "Experience (Years)", 
        "License / RERA / Reg ID", 
        "Verification Status", 
        "Subscription Status", 
        "Registration Date"
    ])
    
    for m in members:
        writer.writerow([
            m.get("id"),
            m.get("full_name"),
            m.get("business_name") or "N/A",
            m.get("whatsapp_number"),
            m.get("phone_number"),
            m.get("circle_name"),
            m.get("city_area"),
            m.get("years_experience"),
            m.get("rera_or_license_id") or "N/A",
            m.get("verification_status"),
            m.get("subscription_status"),
            m.get("created_at")
        ])
    
    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=trusthub_members_directory.csv"
        }
    )

# 11. Request Custom Profession Circle
@app.post("/request-circle")
async def handle_request_circle(
    name: str = Form(...),
    phone: str = Form(...),
    suggested_profession: str = Form(...),
    city: str = Form(...),
    notes: str = Form("")
):
    models.save_circle_request(name, phone, suggested_profession, city, notes)
    return RedirectResponse(url="/#professions", status_code=302)

# 12. Auth / Account Switcher for Demo
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    demo_users = models.get_admin_metrics()["users"]
    current_user = get_current_user(request)
    return templates.TemplateResponse(request=request, name="login.html", context={
        "demo_users": demo_users,
        "current_user": current_user
    })

@app.get("/login/switch/{user_id}")
async def switch_user(request: Request, user_id: int):
    request.session["user_id"] = user_id
    return RedirectResponse(url="/app", status_code=302)

@app.post("/login")
async def handle_login(request: Request, whatsapp_number: str = Form(...)):
    clean_wa = whatsapp_number.strip().replace(" ", "").replace("-", "").replace("+", "")
    if len(clean_wa) == 10:
        clean_wa = "91" + clean_wa
    
    conn = models.get_db_connection()
    user = conn.execute("SELECT id FROM users WHERE whatsapp_number LIKE ? OR phone_number LIKE ?", (f"%{clean_wa}%", f"%{clean_wa}%")).fetchone()
    conn.close()
    
    if user:
        request.session["user_id"] = user["id"]
        return RedirectResponse(url="/app", status_code=302)
    return RedirectResponse(url="/onboard", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
