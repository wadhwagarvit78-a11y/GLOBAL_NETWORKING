from database import get_db_connection
from datetime import datetime, timedelta

def get_all_active_groups():
    conn = get_db_connection()
    groups = conn.execute("SELECT * FROM vertical_groups WHERE is_active = 1 ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(g) for g in groups]

def get_group_by_id(group_id: int):
    conn = get_db_connection()
    group = conn.execute("SELECT * FROM vertical_groups WHERE id = ?", (group_id,)).fetchone()
    conn.close()
    return dict(group) if group else None

def get_group_by_slug(slug: str):
    conn = get_db_connection()
    group = conn.execute("SELECT * FROM vertical_groups WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return dict(group) if group else None

def update_group_whatsapp_link(group_id: int, new_link: str, monthly_fee: int = None):
    conn = get_db_connection()
    if monthly_fee is not None:
        conn.execute("UPDATE vertical_groups SET whatsapp_group_link = ?, monthly_fee = ? WHERE id = ?", (new_link, monthly_fee, group_id))
    else:
        conn.execute("UPDATE vertical_groups SET whatsapp_group_link = ? WHERE id = ?", (new_link, group_id))
    conn.commit()
    conn.close()

def create_user_onboard(
    full_name: str,
    phone_number: str,
    whatsapp_number: str,
    group_id: int,
    city_area: str,
    business_name: str = "",
    years_experience: int = 1,
    rera_or_license_id: str = "",
    profession_custom: str = "",
    source_channel: str = "Direct"
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Format whatsapp number
    clean_wa = whatsapp_number.strip().replace(" ", "").replace("-", "").replace("+", "")
    if len(clean_wa) == 10:
        clean_wa = "91" + clean_wa
        
    group = get_group_by_id(group_id)
    group_name = group["name"] if group else "General Network"
    trial_expiry = datetime.now() + timedelta(days=30)
    
    cursor.execute("""
    INSERT INTO users (
        full_name, phone_number, whatsapp_number, profession_category, profession_custom,
        group_id, city_area, business_name, years_experience, rera_or_license_id,
        source_channel, verification_status, reputation_score, role, subscription_status, trial_ends_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', 100, 'member', 'trial', ?)
    """, (
        full_name, phone_number, clean_wa, group_name, profession_custom,
        group_id, city_area, business_name, years_experience, rera_or_license_id,
        source_channel, trial_expiry.strftime("%Y-%m-%d %H:%M:%S")
    ))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_id(user_id: int):
    conn = get_db_connection()
    user = conn.execute("""
    SELECT u.*, g.name as group_name, g.whatsapp_group_link as group_whatsapp_link, g.slug as group_slug, g.monthly_fee as group_monthly_fee
    FROM users u
    LEFT JOIN vertical_groups g ON u.group_id = g.id
    WHERE u.id = ?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_leads_for_group(group_id: int, sub_location: str = None, deal_type: str = None, search: str = None):
    conn = get_db_connection()
    query = """
    SELECT l.*, u.full_name as author_name, u.whatsapp_number as author_whatsapp,
           u.business_name as author_business, u.city_area as author_city,
           c.full_name as claimer_name, c.whatsapp_number as claimer_whatsapp
    FROM leads l
    JOIN users u ON l.author_id = u.id
    LEFT JOIN users c ON l.claimed_by_id = c.id
    WHERE l.group_id = ?
    """
    params = [group_id]
    
    if sub_location and sub_location != "all":
        query += " AND l.sub_location LIKE ?"
        params.append(f"%{sub_location}%")
        
    if deal_type and deal_type != "all":
        query += " AND l.deal_type = ?"
        params.append(deal_type)
        
    if search:
        query += " AND (l.title LIKE ? OR l.description LIKE ? OR l.sub_location LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
    query += " ORDER BY l.id DESC"
    leads = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(l) for l in leads]

def get_lead_by_id(lead_id: int):
    conn = get_db_connection()
    lead = conn.execute("""
    SELECT l.*, u.full_name as author_name, u.whatsapp_number as author_whatsapp,
           u.business_name as author_business, u.city_area as author_city,
           u.phone_number as author_phone,
           g.name as group_name, g.whatsapp_group_link,
           c.full_name as claimer_name, c.whatsapp_number as claimer_whatsapp
    FROM leads l
    JOIN users u ON l.author_id = u.id
    JOIN vertical_groups g ON l.group_id = g.id
    LEFT JOIN users c ON l.claimed_by_id = c.id
    WHERE l.id = ?
    """, (lead_id,)).fetchone()
    conn.close()
    return dict(lead) if lead else None

def create_lead(author_id: int, group_id: int, title: str, deal_type: str, sub_location: str, budget_range: str, description: str, expected_commission: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM leads")
    next_num = cursor.fetchone()["count"] + 101
    lead_token = f"LEAD-{next_num}"
    
    cursor.execute("""
    INSERT INTO leads (
        lead_token, group_id, author_id, title, deal_type, sub_location, budget_range,
        description, expected_commission, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open')
    """, (lead_token, group_id, author_id, title, deal_type, sub_location, budget_range, description, expected_commission))
    
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def claim_lead(lead_id: int, claimer_id: int):
    conn = get_db_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
    UPDATE leads 
    SET status = 'claimed', claimed_by_id = ?, claimed_at = ?
    WHERE id = ? AND status = 'open'
    """, (claimer_id, now_str, lead_id))
    conn.commit()
    conn.close()

def close_lead_deal(lead_id: int, deal_value: float, commission_earned: float, platform_fee_pct: float = 15.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    platform_fee = (commission_earned * platform_fee_pct) / 100.0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    UPDATE leads 
    SET status = 'closed', closed_at = ?, deal_value = ?, commission_earned = ?, platform_fee = ?
    WHERE id = ?
    """, (now_str, deal_value, commission_earned, platform_fee, lead_id))
    
    # Fetch lead to record ledger
    lead = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    if lead:
        payer_id = lead["claimed_by_id"] if lead["claimed_by_id"] else lead["author_id"]
        cursor.execute("""
        INSERT INTO commission_ledger (lead_id, payer_id, amount, status)
        VALUES (?, ?, ?, 'pending')
        """, (lead_id, payer_id, platform_fee))
        
    conn.commit()
    conn.close()

def get_commission_ledger(user_id: int = None):
    conn = get_db_connection()
    query = """
    SELECT cl.*, l.title as lead_title, l.lead_token, u.full_name as payer_name, u.whatsapp_number as payer_whatsapp
    FROM commission_ledger cl
    JOIN leads l ON cl.lead_id = l.id
    JOIN users u ON cl.payer_id = u.id
    """
    params = []
    if user_id:
        query += " WHERE cl.payer_id = ?"
        params.append(user_id)
    query += " ORDER BY cl.id DESC"
    
    records = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in records]

def submit_payment_proof(ledger_id: int, proof_ref: str, notes: str):
    conn = get_db_connection()
    conn.execute("""
    UPDATE commission_ledger
    SET status = 'proof_submitted', proof_reference = ?, proof_notes = ?
    WHERE id = ?
    """, (proof_ref, notes, ledger_id))
    conn.commit()
    conn.close()

def verify_commission_payment(ledger_id: int):
    conn = get_db_connection()
    conn.execute("UPDATE commission_ledger SET status = 'verified' WHERE id = ?", (ledger_id,))
    conn.commit()
    conn.close()

def save_circle_request(name: str, phone: str, suggested_profession: str, city: str, notes: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO circle_requests (name, phone_whatsapp, suggested_profession, city, notes)
    VALUES (?, ?, ?, ?, ?)
    """, (name, phone, suggested_profession, city, notes))
    req_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return req_id

def get_all_circle_requests():
    conn = get_db_connection()
    requests = conn.execute("SELECT * FROM circle_requests ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in requests]

def get_admin_metrics():
    conn = get_db_connection()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    closed_leads = conn.execute("SELECT COUNT(*) FROM leads WHERE status = 'closed'").fetchone()[0]
    total_commission_collected = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM commission_ledger WHERE status = 'verified'").fetchone()[0]
    pending_commission = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM commission_ledger WHERE status != 'verified'").fetchone()[0]
    
    groups = conn.execute("SELECT * FROM vertical_groups ORDER BY id ASC").fetchall()
    all_users = conn.execute("SELECT u.*, g.name as group_name FROM users u LEFT JOIN vertical_groups g ON u.group_id = g.id ORDER BY u.id DESC").fetchall()
    all_leads = conn.execute("""
    SELECT l.*, u.full_name as author_name, g.name as group_name, c.full_name as claimer_name
    FROM leads l
    JOIN users u ON l.author_id = u.id
    JOIN vertical_groups g ON l.group_id = g.id
    LEFT JOIN users c ON l.claimed_by_id = c.id
    ORDER BY l.id DESC
    """).fetchall()
    all_ledger = conn.execute("""
    SELECT cl.*, l.lead_token, l.title as lead_title, u.full_name as payer_name, u.phone_number, u.whatsapp_number
    FROM commission_ledger cl
    JOIN leads l ON cl.lead_id = l.id
    JOIN users u ON cl.payer_id = u.id
    ORDER BY cl.id DESC
    """).fetchall()
    cross_requests = conn.execute("""
    SELECT * FROM cross_vertical_requests ORDER BY id DESC
    """).fetchall()
    
    conn.close()
    return {
        "total_users": total_users,
        "total_leads": total_leads,
        "closed_leads": closed_leads,
        "total_commission_collected": total_commission_collected,
        "pending_commission": pending_commission,
        "groups": [dict(g) for g in groups],
        "users": [dict(u) for u in all_users],
        "leads": [dict(l) for l in all_leads],
        "ledger": [dict(r) for r in all_ledger],
        "cross_requests": [dict(cr) for cr in cross_requests]
    }

def create_cross_vertical_request(user_id: int, user_name: str, user_phone: str, user_profession: str, target_service: str, requirement_details: str, budget_range: str = "") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO cross_vertical_requests (user_id, user_name, user_phone, user_profession, target_service, requirement_details, budget_range)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, user_name, user_phone, user_profession, target_service, requirement_details, budget_range))
    req_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return req_id
