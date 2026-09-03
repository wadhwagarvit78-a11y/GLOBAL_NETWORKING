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
    trial_expiry = (datetime.now() + timedelta(days=28)).strftime('%Y-%m-%d %H:%M:%S')
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
            "Central Delhi / Connaught Place", "Globe Trotters B2B Holidays", 10, "IATA-9812-DEL", "Travel Expo", 1,
            "approved", 96, "member", "active", trial_expiry
        ),
        (
            5, "Karan Kapoor", "9818889900", "919818889900", "Software Engineers & Tech Consultants", None, 5,
            "Noida Sector 62 / Remote", "Kapoor FullStack Lab", 7, "NASSCOM-DEV-882", "GitHub Community", 1,
            "approved", 94, "member", "trial", trial_expiry
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
            "1% Net Brokerage Split (approx ₹4.5 Lakhs)",
            "open", None, None, None, 45000000, 450000, 67500
        ),
        (
            2, "LEAD-102", 2, 4,
            "Corporate Offsite: 85 Pax 3N/4D Luxury Resort Package in Jim Corbett / Goa",
            "b2b_group", "Delhi Corporate Client", "₹12 Lakhs - ₹15 Lakhs",
            "Looking for 5-star inventory with conference hall, gala dinner, and airport transfers for IT corporate team.",
            "10% Net Booking Margin Split",
            "open", None, None, None, 1200000, 120000, 18000
        ),
        (
            3, "LEAD-103", 5, 5,
            "Mobile App MVP: Cross-Platform React Native App for Logistics Startup",
            "client_brief", "Bangalore / Remote Client", "₹2.5 Lakhs - ₹3.5 Lakhs",
            "Client needs rapid 4-week prototype with GPS tracking and payment gateway integration. Wireframes ready.",
            "15% Subcontracting Commission",
            "open", None, None, None, 300000, 45000, 6750
        ),
        (
            4, "LEAD-104", 3, 6,
            "CNC Precision Machining & Sheet Metal Fabrication for EV Enclosures",
            "supplier_mandate", "Manesar IMT / Pune", "₹8 Lakhs / Month Recurring",
            "OEM Tier-1 supplier seeking certified vendor for 5,000 units/mo aluminium CNC turned components.",
            "5% Continuous Sourcing Margin",
            "open", None, None, None, 800000, 40000, 6000
        ),
        (
            5, "LEAD-105", 4, 7,
            "Commercial Lease Dispute Litigation in Saket District Court",
            "client_consult", "South Delhi / Saket", "₹1.5 Lakh Retainer",
            "NRI landlord seeking dispute representation against defaulting commercial tenant.",
            "15% Referral Fee (₹22,500)",
            "closed", 7, (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 150000, 22500, 3375
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
