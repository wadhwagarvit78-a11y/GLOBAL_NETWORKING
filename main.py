from fastapi import FastAPI, Request, Form, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import urllib.parse
from pathlib import Path

from database import init_db
import models

# Initialize Database
init_db()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ReferralCircle — Professional Referral Network")
app.add_middleware(SessionMiddleware, secret_key="referralcircle-super-secret-key-2026")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        user = models.get_user_by_id(user_id)
        if user:
            return user
    # Fallback demo default user (User 2: Rajesh Khanna / Real Estate or User 4: Sunil Verma / Travel)
    default_user = models.get_user_by_id(2)
    if default_user:
        request.session["user_id"] = default_user["id"]
        return default_user
    return None

# 1. Homepage (Universal / Vertical-Agnostic with Motto & 5 Advantages)
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    groups = models.get_all_active_groups()
    current_user = get_current_user(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "groups": groups,
        "current_user": current_user
    })

# 2. Dedicated Onboard Page
@app.get("/onboard", response_class=HTMLResponse)
async def onboard_page(request: Request, group_id: int = None):
    groups = models.get_all_active_groups()
    current_user = get_current_user(request)
    return templates.TemplateResponse("onboard.html", {
        "request": request,
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
    return templates.TemplateResponse("whatsapp_redirect.html", {
        "request": request,
        "user": user,
        "group": group,
        "current_user": user
    })

# 4. Member's Dedicated Feed Dashboard (Filtered exclusively to their profession)
@app.get("/app", response_class=HTMLResponse)
async def member_dashboard(
    request: Request,
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
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user,
        "group": group,
        "leads": leads,
        "location": location,
        "deal_type": deal_type,
        "search": search
    })

# 5. Post Lead
@app.get("/post-lead", response_class=HTMLResponse)
async def post_lead_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    group_id = current_user.get("group_id") or 1
    group = models.get_group_by_id(group_id)
    return templates.TemplateResponse("post_lead.html", {
        "request": request,
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
    return RedirectResponse(url=f"/leads/{lead_id}", status_code=302)

# 6. Lead Detail & 1-Click WhatsApp Handoff
@app.get("/leads/{lead_id}", response_class=HTMLResponse)
async def lead_detail_page(request: Request, lead_id: int):
    current_user = get_current_user(request)
    lead = models.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return templates.TemplateResponse("lead_detail.html", {
        "request": request,
        "current_user": current_user,
        "lead": lead
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
        msg = f"Hi {lead['author_name']}, I claimed your requirement {token} ({title}) on ReferralCircle. Let's coordinate the deal!"
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
    return templates.TemplateResponse("ledger.html", {
        "request": request,
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
    return RedirectResponse(url="/ledger", status_code=302)

# 9. Subscription & Trial
@app.get("/subscription", response_class=HTMLResponse)
async def subscription_page(request: Request):
    current_user = get_current_user(request)
    return templates.TemplateResponse("subscription.html", {
        "request": request,
        "current_user": current_user
    })

@app.post("/subscription/activate")
async def handle_subscription_activate(request: Request):
    return RedirectResponse(url="/app", status_code=302)

# 10. Admin Control Center (WhatsApp Link Manager, KPIs, Directory, Commission Approvals)
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    current_user = get_current_user(request)
    metrics = models.get_admin_metrics()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "current_user": current_user,
        "metrics": metrics
    })

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
    return templates.TemplateResponse("login.html", {
        "request": request,
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
