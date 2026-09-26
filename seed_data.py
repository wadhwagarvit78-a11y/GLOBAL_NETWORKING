from database import get_db_connection, init_db
from datetime import datetime, timedelta

def seed_all():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing demo data
    cursor.execute("DELETE FROM circle_requests")
    cursor.execute("DELETE FROM commission_ledger")
    cursor.execute("DELETE FROM cross_vertical_requests")
    cursor.execute("DELETE FROM leads")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM vertical_groups")

    # 1. Insert Initial Profession Circles (100% Free Lifetime)
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
            0
        ),
        (
            2,
            "Travel Agents & Tour Operators Circle",
            "travel-agents",
            "Travel & Tourism",
            "B2B hotel bookings, car & cab rentals, holiday packages, visas, and corporate travel referrals.",
            "compass",
            "https://chat.whatsapp.com/invite/Travel-Agents-Hub-Official",
            "10% Net Booking Margin",
            0
        ),
        (
            3,
            "Commercial & Wedding Catering Network",
            "catering-services",
            "Catering & Hospitality",
            "High-trust circle for commercial caterers, wedding food banquets, corporate pantry suppliers, and live buffet specialists.",
            "utensils",
            "https://chat.whatsapp.com/invite/Catering-Network-Official",
            "10-15% Event Value Split",
            0
        ),
        (
            4,
            "Event Management & Production Hub",
            "event-management",
            "Events & Production",
            "B2B collaboration for luxury wedding planners, corporate summit producers, sound/stage setups, and artist management.",
            "calendar",
            "https://chat.whatsapp.com/invite/Event-Management-Hub",
            "10-15% Project Execution Split",
            0
        ),
        (
            5,
            "Himachal DMC Circle",
            "himachal-dmc",
            "Travel & DMCs",
            "Verified B2B ground operators for Shimla, Manali, Dharamshala, Spiti & Kasol — hotel allocations, Volvo/cabs, trekking & customized packages.",
            "mountain",
            "https://chat.whatsapp.com/invite/Himachal-DMC-Official",
            "10-12% B2B Net Margin Split",
            0
        ),
        (
            6,
            "Uttarakhand DMC Circle",
            "uttarakhand-dmc",
            "Travel & DMCs",
            "Verified B2B DMC for Rishikesh, Mussoorie, Nainital, Jim Corbett, and Char Dham Yatra logistics, hotel inventory & transport.",
            "map-pin",
            "https://chat.whatsapp.com/invite/Uttarakhand-DMC-Official",
            "10-12% B2B Net Margin Split",
            0
        ),
        (
            7,
            "Goa DMC Network",
            "goa-dmc",
            "Travel & DMCs",
            "Exclusive B2B DMC for Goa destination weddings, corporate MICE offsites, luxury beach villas, cruise parties, and airport fleet logistics.",
            "sun",
            "https://chat.whatsapp.com/invite/Goa-DMC-Official",
            "10-15% Net Booking Split",
            0
        ),
        (
            8,
            "Corporate & Litigation Lawyers Network",
            "legal-consultants",
            "Legal & Compliance",
            "Client consultation referrals, high-court litigation handoffs, and corporate drafting collaborations.",
            "scale",
            "https://chat.whatsapp.com/invite/Lawyers-Legal-Circle-India",
            "15% Initial Retainer Referral Cut",
            0
        ),
        (
            9,
            "Software Engineers & Tech Consultants",
            "software-engineers",
            "Technology & IT",
            "Freelance dev contracts, mobile/web app projects, AI integrations, and tech placement referrals.",
            "code",
            "https://chat.whatsapp.com/invite/Tech-Freelancers-Network",
            "10% Contract Value Split",
            0
        ),
        (
            10,
            "Architects & Interior Designers Circle",
            "architects-designers",
            "Architecture & Design",
            "Turnkey residential, commercial architectural, 3D modeling, and renovation project referrals.",
            "compass",
            "https://chat.whatsapp.com/invite/Architects-Designers-Hub",
            "8-12% Execution Project Cut",
            0
        ),
        (
            11,
            "Mechanical & Industrial Engineers Hub",
            "mechanical-engineers",
            "Engineering & Manufacturing",
            "B2B industrial requirements, fabrication contracts, machining leads, and equipment procurement.",
            "cog",
            "https://chat.whatsapp.com/invite/Mechanical-Industrial-Network",
            "5-10% Project Value / Referral Cut",
            0
        ),
        (
            12,
            "FREE Sponcered Trips",
            "free-sponcered-trips",
            "Travel & Sponsorships",
            "Exclusive circle for travel organizers, brands, influencers, hospitality sponsors & corporate groups collaborating on fully/partially funded trips.",
            "gift",

            "https://chat.whatsapp.com/invite/Free-Sponsored-Trips-Hub",
            "Sponsor Terms / Collab Split",
            0
        )
    ]


    cursor.executemany("""
    INSERT INTO vertical_groups (id, name, slug, category, description, icon, whatsapp_group_link, min_commission_rate, monthly_fee)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, groups)

    # 2. Insert Demo Users (100% Free Active Members)
    users = [
        (
            1, "Trusthub admin", "9876500000", "919876500000", "Platform Admin", None, 1,
            "Gurgaon Sector 29", "TrustHub Founders Desk", 10, "FOUNDER-001", "Direct", 1,
            "approved", 100, "admin", "active", None
        ),
        (
            2, "Rajesh Khanna", "9811002233", "919811002233", "Property Dealers & Realtors Network", None, 1,
            "Gurgaon Golf Course Ext", "Khanna Real Estate Advisors", 12, "HRERA-GGM-2021-894", "WhatsApp Group", 1,
            "approved", 98, "member", "active", None
        ),
        (
            3, "Amit Sharma", "9899112233", "919899112233", "Property Dealers & Realtors Network", None, 1,
            "Noida Expressway", "NCR Square Properties", 8, "UPRERA-NOIDA-541", "LinkedIn", 1,
            "approved", 95, "member", "active", None
        ),
        (
            4, "Sunil Verma", "9711223344", "919711223344", "Travel Agents & Tour Operators Circle", None, 2,
            "Central Delhi / Connaught Place", "Globe Trotters B2B Holidays", 10, "IATA-9812-DEL", "Travel Expo", 1,
            "approved", 96, "member", "active", None
        ),
        (
            5, "Karan Kapoor", "9818889900", "919818889900", "Software Engineers & Tech Consultants", None, 9,
            "Noida Sector 62 / Remote", "Kapoor FullStack Lab", 7, "NASSCOM-DEV-882", "GitHub Community", 1,
            "approved", 94, "member", "active", None
        ),
        (
            6, "Vikram Singhania", "9822446688", "919822446688", "Mechanical & Industrial Engineers Hub", None, 11,
            "Faridabad Industrial Area", "Singhania Precision Tooling", 15, "ISO-9001-MFG", "Industry Association", 1,
            "approved", 99, "member", "active", None
        ),
        (
            7, "Adv. Neha Saxena", "9810887766", "919810887766", "Corporate & Litigation Lawyers Network", None, 8,
            "South Delhi / Saket Court", "Saxena Legal Chambers", 9, "D/1452/2015", "Bar Association", 1,
            "approved", 97, "member", "active", None
        ),
        (
            8, "Suresh Agarwal", "9811334455", "919811334455", "Commercial & Wedding Catering Network", None, 3,
            "South Delhi / Chattarpur", "Agarwal Grand Banquet Caterers", 14, "FSSAI-1152200", "Industry Association", 1,
            "approved", 98, "member", "active", None
        ),
        (
            9, "Rohan Malhotra", "9877665544", "919877665544", "Event Management & Production Hub", None, 4,
            "Delhi Aerocity / Gurgaon", "Vivid Events & Production House", 9, "EEMA-DEL-772", "Peer Referral", 1,
            "approved", 96, "member", "active", None
        ),
        (
            10, "Pooja Thakur", "9816001122", "919816001122", "Himachal DMC Circle", None, 5,
            "Manali / Shimla", "Himalayan Escapes B2B DMC", 11, "HPTDC-REG-441", "Travel Mart", 1,
            "approved", 99, "member", "active", None
        ),
        (
            11, "Deepak Rawat", "9837112233", "919837112233", "Uttarakhand DMC Circle", None, 6,
            "Rishikesh / Jim Corbett", "Devbhoomi B2B Travel Services", 10, "UK-TOURISM-889", "DMC Association", 1,
            "approved", 97, "member", "active", None
        ),
        (
            12, "Anthony D'Souza", "9822331100", "919822331100", "Goa DMC Network", None, 7,
            "Panjim / Calangute Goa", "Goa Sun & Sand MICE Solutions", 13, "GTDC-LIC-1092", "Direct Member", 1,
            "approved", 98, "member", "active", None
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
            "Corporate Offsite: 85 Pax 3N/4D Luxury Resort Package with Flights & Cabs",
            "b2b_group", "Delhi Corporate Client", "₹12 Lakhs - ₹15 Lakhs",
            "Looking for 5-star inventory with conference hall, gala dinner, and airport transfers for IT corporate team.",
            "10% Net Booking Margin Split",
            "open", None, None, None, 1200000, 120000, 18000
        ),
        (
            3, "LEAD-103", 9, 5,
            "Mobile App MVP: Cross-Platform React Native App for Logistics Startup",
            "client_brief", "Bangalore / Remote Client", "₹2.5 Lakhs - ₹3.5 Lakhs",
            "Client needs rapid 4-week prototype with GPS tracking and payment gateway integration. Wireframes ready.",
            "15% Subcontracting Commission",
            "open", None, None, None, 300000, 45000, 6750
        ),
        (
            4, "LEAD-104", 11, 6,
            "CNC Precision Machining & Sheet Metal Fabrication for EV Enclosures",
            "supplier_mandate", "Manesar IMT / Pune", "₹8 Lakhs / Month Recurring",
            "OEM Tier-1 supplier seeking certified vendor for 5,000 units/mo aluminium CNC turned components.",
            "5% Continuous Sourcing Margin",
            "open", None, None, None, 800000, 40000, 6000
        ),
        (
            5, "LEAD-105", 8, 7,
            "Commercial Lease Dispute Litigation in Saket District Court",
            "client_consult", "South Delhi / Saket", "₹1.5 Lakh Retainer",
            "NRI landlord seeking dispute representation against defaulting commercial tenant.",
            "15% Referral Fee (₹22,500)",
            "closed", 7, (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 150000, 22500, 3375
        ),
        (
            6, "LEAD-106", 3, 8,
            "Wedding Catering for 650 Pax at Chattarpur Farms, South Delhi",
            "client_brief", "South Delhi / Chattarpur", "₹15 Lakhs - ₹18 Lakhs",
            "High-end 2-day wedding banquet. Requires live counters (Artisanal Chaat, Dimsum, Woodfired Pizza, Mughlai & traditional North Indian). Complete crockery & uniformed staff.",
            "10% Referral Cut (₹1.5 Lakhs)",
            "open", None, None, None, 1600000, 160000, 24000
        ),
        (
            7, "LEAD-107", 4, 9,
            "Corporate Annual Conclave & Gala Awards Setup: 350 Delegates at Delhi Aerocity",
            "project", "Delhi Aerocity Hotel", "₹7.5 Lakhs - ₹9.5 Lakhs",
            "Complete stage fabrication, curved P3 LED wall, professional line-array sound, moving head lights, Emcee and DJ management.",
            "12% Project Execution Split",
            "open", None, None, None, 850000, 102000, 15300
        ),
        (
            8, "LEAD-108", 5, 10,
            "Shimla & Manali 5N/6D Summer Group: 50 Pax Deluxe Hotel Allocation & 12 Innovas",
            "b2b_group", "Himachal (Shimla-Manali)", "₹7.5 Lakhs - ₹9 Lakhs",
            "Tour operator from Ahmedabad needs confirmed 3-star deluxe hotel inventory (25 rooms) with breakfast & dinner, Solang valley transfers, and local sightseeing cabs.",
            "10% Net B2B Margin Split",
            "open", None, None, None, 800000, 80000, 12000
        ),
        (
            9, "LEAD-109", 6, 11,
            "Jim Corbett Corporate Retreat: 60 Pax Luxury 5-Star Resort with Jungle Safari",
            "b2b_group", "Jim Corbett / Ramnagar", "₹8 Lakhs - ₹10 Lakhs",
            "Gurgaon MNC offsite booking. Needs 30 luxury cottages, banquet hall for seminar, gala DJ night, and 10 open gypsy safari slots.",
            "10% Net Booking Cut",
            "open", None, None, None, 850000, 85000, 12750
        ),
        (
            10, "LEAD-110", 7, 12,
            "North Goa Beachside Destination Wedding: 140 Pax 3-Day Villa & Resort Booking + Airport Fleet",
            "b2b_group", "Candolim / Calangute, Goa", "₹22 Lakhs - ₹28 Lakhs",
            "Luxury private villa cluster and 40 beach resort rooms, airport luxury coach fleet, and sundowner yacht party coordination.",
            "12% Booking Split",
            "open", None, None, None, 2500000, 300000, 45000
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
    print("Database seeded with 11 profession circles, realistic users, and high-value leads!")

if __name__ == "__main__":
    seed_all()
