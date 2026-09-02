from database import get_db_connection, init_db
from datetime import datetime, timedelta

def seed_all():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing demo data
    cursor.execute("DELETE FROM circle_requests")
    cursor.execute("DELETE FROM commission_ledger")
    cursor.execute("DELETE FROM leads")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM vertical_groups")

    # 1. Insert Initial Profession Circles
    groups = [
        (
            1,
            "Property Dealers & Realtors Network",
            "property-dealers",
            "Real Estate",
            "High-trust circle for verified brokers and property dealers in NCR and major metros.",
            "building",
            "https://chat.whatsapp.com/invite/NCR-Property-Dealers-Official",
            "10-20% Brokerage Commission",
            499
        ),
        (
            2,
            "Travel Agents & Tour Operators Circle",
            "travel-agents",
            "Travel & Tourism",
            "Exclusive network for B2B flight, holiday package, visa, and corporate travel referrals.",
            "plane",
            "https://chat.whatsapp.com/invite/Travel-Agents-Hub-Official",
            "10% Net Booking Margin",
            0
        ),
        (
            3,
            "Mechanical & Industrial Engineers Hub",
            "mechanical-engineers",
            "Engineering & Manufacturing",
            "B2B industrial requirements, fabrication contracts, machining leads, and equipment procurement.",
            "cog",
            "https://chat.whatsapp.com/invite/Mechanical-Industrial-Network",
            "5-10% Project Value / Referral Cut",
            299
        ),
        (
            4,
            "Corporate & Litigation Lawyers Network",
            "legal-consultants",
            "Legal & Compliance",
            "Client consultation referrals, high-court litigation handoffs, and corporate drafting collaborations.",
            "scale",
            "https://chat.whatsapp.com/invite/Lawyers-Legal-Circle-India",
            "15% Initial Retainer Referral Cut",
            399
        ),
        (
            5,
            "Software Engineers & Tech Consultants",
            "software-engineers",
            "Technology & IT",
            "Freelance dev contracts, mobile/web app projects, AI integrations, and tech placement referrals.",
            "code",
            "https://chat.whatsapp.com/invite/Tech-Freelancers-Network",
            "10% Contract Value Split",
            399
        ),
        (
            6,
            "Architects & Interior Designers Circle",
            "architects-designers",
            "Architecture & Design",
            "Turnkey residential, commercial architectural, 3D modeling, and renovation project referrals.",
            "compass",
            "https://chat.whatsapp.com/invite/Architects-Designers-Hub",
            "8-12% Execution Project Cut",
            399
        )
    ]

    cursor.executemany("""
    INSERT INTO vertical_groups (id, name, slug, category, description, icon, whatsapp_group_link, min_commission_rate, monthly_fee)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, groups)

    # 2. Insert Demo Users
    trial_expiry = datetime.now() + timedelta(days=28)
    users = [
        (
            1, "Admin Founder", "9876500000", "919876500000", "Platform Admin", None, 1,
            "Gurgaon Sector 29", "Platform Management", 10, "FOUNDER-001", "Direct", 1,
            "approved", 100, "admin", "active", trial_expiry
        ),
        (
            2, "Rajesh Khanna", "9811002233", "919811002233", "Property Dealers & Realtors Network", None, 1,
            "Gurgaon Golf Course Ext", "Khanna Real Estate Advisors", 12, "HRERA-GGM-2021-894", "WhatsApp Group", 1,
            "approved", 98, "member", "trial", trial_expiry
        ),
        (
            3, "Amit Sharma", "9899112233", "919899112233", "Property Dealers & Realtors Network", None, 1,
            "Noida Expressway", "NCR Square Properties", 8, "UPRERA-NOIDA-541", "LinkedIn", 1,
            "approved", 95, "member", "trial", trial_expiry
        ),
        (
            4, "Sunil Verma", "9711223344", "919711223344", "Travel Agents & Tour Operators Circle", None, 2,
            "Delhi Connaught Place", "Verma Global Vacations", 14, "IATA-DL-9081", "Referral", 1,
            "approved", 96, "member", "trial", trial_expiry
        ),
        (
            5, "Pooja Malhotra", "9871556677", "919871556677", "Travel Agents & Tour Operators Circle", None, 2,
            "Chandigarh Sector 17", "Malhotra Luxury Trips", 7, "TAAI-CH-114", "Instagram", 1,
            "approved", 92, "member", "trial", trial_expiry
        ),
        (
            6, "Vikram Singhania", "9822446688", "919822446688", "Mechanical & Industrial Engineers Hub", None, 3,
            "Faridabad Industrial Area", "Singhania Precision Tooling", 15, "ISO-9001-MFG", "Industry Association", 1,
            "approved", 99, "member", "trial", trial_expiry
        ),
        (
            7, "Adv. Neha Saxena", "9810887766", "919810887766", "Corporate & Litigation Lawyers Network", None, 4,
            "South Delhi / Saket Court", "Saxena Legal Chambers", 9, "D/1452/2015", "Bar Association", 1,
            "approved", 97, "member", "trial", trial_expiry
        )
    ]

    cursor.executemany("""
    INSERT INTO users (
        id, full_name, phone_number, whatsapp_number, profession_category, profession_custom, group_id,
        city_area, business_name, years_experience, rera_or_license_id, source_channel, consent_share_contact,
        verification_status, reputation_score, role, subscription_status, trial_ends_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, users)

    # 3. Insert Demo Leads
    leads = [
        (
            1, "LEAD-101", 1, 2,
            "Urgent: Verified Buyer for 4BHK Luxury Apartment in Sector 65, Gurgaon",
            "buy", "Gurgaon Sector 65", "₹4.5 Cr - ₹5.5 Cr",
            "Client looking for immediate possession in M3M Golfestate or Trump Tower. Ready cheque with pre-approved loan.",
            "20% Brokerage Split (approx ₹90k-₹1.1L)",
            "open", None, None, None, 0, 0, 0
        ),
        (
            2, "LEAD-102", 1, 3,
            "Commercial Retail Space Tenant for Sector 132 Expressway, Noida",
            "rent", "Noida Sector 132", "₹1.5 Lakh/Month",
            "Established Diagnostic Lab looking for 1,800 sq ft ground floor space on main road. 9-year lease required.",
            "1 Month Rent Commission Split (₹75k)",
            "claimed", 2, datetime.now() - timedelta(days=2), None, 0, 0, 0
        ),
        (
            3, "LEAD-103", 2, 4,
            "High-Budget Corporate Offsite Booking (120 Pax to Dubai)",
            "client_consult", "Delhi NCR / International", "₹35 Lakhs Total Package",
            "Tech MNC requiring 4-star hotel stay, flight charters, and conference hall in Dubai for 4 Nights.",
            "10% Net Margin Split",
            "open", None, None, None, 0, 0, 0
        ),
        (
            4, "LEAD-104", 3, 6,
            "CNC Precision Milling Contract for 5,000 Auto Component Units",
            "project", "Faridabad / Manesar", "₹18 Lakhs Contract",
            "Tier-1 Automotive OEM looking for certified vendor with VMC machines and CMM inspection capabilities.",
            "7% Referral Cut",
            "open", None, None, None, 0, 0, 0
        ),
        (
            5, "LEAD-105", 4, 7,
            "Commercial Lease Dispute Litigation in Saket District Court",
            "client_consult", "South Delhi / Saket", "₹1.5 Lakh Retainer",
            "NRI landlord seeking dispute representation against defaulting commercial tenant.",
            "15% Referral Fee (₹22,500)",
            "closed", 7, datetime.now() - timedelta(days=5), datetime.now() - timedelta(days=1), 150000, 22500, 3375
        )
    ]

    cursor.executemany("""
    INSERT INTO leads (
        id, lead_token, group_id, author_id, title, deal_type, sub_location, budget_range,
        description, expected_commission, status, claimed_by_id, claimed_at, closed_at,
        deal_value, commission_earned, platform_fee
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, leads)

    # 4. Insert Sample Commission Ledger
    cursor.execute("""
    INSERT INTO commission_ledger (lead_id, payer_id, amount, status, payment_method, proof_reference, proof_notes)
    VALUES (5, 7, 3375.0, 'verified', 'UPI', 'UPI/UTR-90881234987', 'Closed deal commission paid via Google Pay')
    """)

    conn.commit()
    conn.close()
    print("Database seeded with realistic multi-vertical network data!")

if __name__ == "__main__":
    seed_all()
