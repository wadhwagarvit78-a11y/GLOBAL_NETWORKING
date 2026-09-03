import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "referral_platform.db"

def get_db_connection():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verticals / Profession Groups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vertical_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT 'users',
        whatsapp_group_link TEXT NOT NULL DEFAULT 'https://chat.whatsapp.com/invite-default',
        min_commission_rate TEXT DEFAULT '10-20% Brokerage / Success Fee',
        monthly_fee INTEGER DEFAULT 399,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migration for existing vertical_groups table
    cursor.execute("PRAGMA table_info(vertical_groups)")
    columns = [col[1] for col in cursor.fetchall()]
    if "monthly_fee" not in columns:
        cursor.execute("ALTER TABLE vertical_groups ADD COLUMN monthly_fee INTEGER DEFAULT 399")

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        whatsapp_number TEXT NOT NULL,
        profession_category TEXT NOT NULL,
        profession_custom TEXT,
        group_id INTEGER,
        city_area TEXT NOT NULL,
        business_name TEXT,
        years_experience INTEGER DEFAULT 1,
        rera_or_license_id TEXT,
        source_channel TEXT,
        consent_share_contact INTEGER DEFAULT 1,
        verification_status TEXT DEFAULT 'approved', -- 'pending', 'approved', 'rejected'
        reputation_score INTEGER DEFAULT 100,
        role TEXT DEFAULT 'member', -- 'member', 'admin'
        subscription_status TEXT DEFAULT 'trial', -- 'trial', 'active', 'expired'
        trial_ends_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES vertical_groups (id)
    );
    """)

    # Leads Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_token TEXT UNIQUE,
        group_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        deal_type TEXT NOT NULL, -- 'buy', 'sell', 'rent', 'project', 'client_consult', 'other'
        sub_location TEXT NOT NULL,
        budget_range TEXT NOT NULL,
        description TEXT NOT NULL,
        expected_commission TEXT,
        status TEXT DEFAULT 'open', -- 'open', 'claimed', 'in_progress', 'closed', 'disputed'
        claimed_by_id INTEGER,
        claimed_at TIMESTAMP,
        closed_at TIMESTAMP,
        deal_value REAL DEFAULT 0,
        commission_earned REAL DEFAULT 0,
        platform_fee REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES vertical_groups (id),
        FOREIGN KEY (author_id) REFERENCES users (id),
        FOREIGN KEY (claimed_by_id) REFERENCES users (id)
    );
    """)

    # Commission Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commission_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER NOT NULL,
        payer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending', -- 'pending', 'proof_submitted', 'verified'
        payment_method TEXT DEFAULT 'UPI',
        proof_reference TEXT,
        proof_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lead_id) REFERENCES leads (id),
        FOREIGN KEY (payer_id) REFERENCES users (id)
    );
    """)

    # Circle Requests (For users requesting new professions not yet listed)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS circle_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone_whatsapp TEXT NOT NULL,
        suggested_profession TEXT NOT NULL,
        city TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Cross-Vertical Peer Service Requests (When a lawyer needs property, or dealer needs a trip)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cross_vertical_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_name TEXT NOT NULL,
        user_phone TEXT NOT NULL,
        user_profession TEXT NOT NULL,
        target_service TEXT NOT NULL,
        requirement_details TEXT NOT NULL,
        budget_range TEXT,
        status TEXT DEFAULT 'pending',
        admin_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """)

    # Auto-seed if empty
    group_count = cursor.execute("SELECT COUNT(*) FROM vertical_groups").fetchone()[0]
    conn.commit()
    conn.close()
    if group_count == 0:
        import seed_data
        seed_data.seed_all()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
