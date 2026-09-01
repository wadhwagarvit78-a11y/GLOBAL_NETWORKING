# ReferralCircle — Professional Referral & Community Platform

A hyper-local, multi-vertical referral exchange and networking platform designed for professionals (Travel Agents, Mechanical Engineers, Realtors, Lawyers, Architects, Tech Freelancers) to monetize excess client inquiries and coordinate leads directly via WhatsApp.

---

## 🚀 Key Features

- **Universal & High-Converting Homepage**: Vertical-agnostic motto and 5 core business advantages that appeal to any profession.
- **Instant WhatsApp Group Redirection**: Immediately routes newly registered members to their profession's official WhatsApp Group with an automated countdown.
- **Isolated Profession Dashboard**: Members only see leads and community tools tailored to their specific industry circle.
- **1-Click WhatsApp Lead Coordination**: Claiming any lead opens a direct WhatsApp chat with the author pre-filled with the exact Lead ID.
- **Deal Lifecycle & Commission Ledger**: Track deal progress (`Open` → `Claimed` → `In Progress` → `Closed`) and log platform commission with UPI proof submission.
- **30-Day Free Trial & ₹500/mo Subscription**: Integrated trial countdown and simulated Razorpay recurring autopay.
- **Founder Admin Control Center (`/admin`)**: Edit WhatsApp group invite links for any vertical on the fly, inspect cross-vertical leads, and verify UPI commission payments.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLite
- **Frontend**: Tailwind CSS (CDN), Lucide Icons, Alpine.js
- **Templates**: Jinja2

---

## ⚡ Quick Start

### On Linux / macOS
```bash
# 1. Clone the repository
git clone <YOUR_REPO_URL>
cd referral_network

# 2. Install dependencies
pip install fastapi uvicorn jinja2 starlette

# 3. Seed database with demo data
python seed_data.py

# 4. Start the server
./run.sh
# Or: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### On Windows
1. Double-click `run_windows.bat` (automatically installs packages, sets up database, and launches `http://localhost:8000`).

---

## 🔑 Default Test Accounts

You can switch test accounts instantly via the `/login` switcher:

| User | Vertical Circle | Role |
|---|---|---|
| **Admin Founder** | Platform Admin | Full access to `/admin` & WhatsApp Link Editor |
| **Rajesh Khanna** | Property Dealers & Realtors | Verified Broker (NCR) |
| **Sunil Verma** | Travel Agents & Tour Operators | Verified Agent (Delhi) |
| **Vikram Singhania** | Mechanical & Industrial Engineers | Verified Consultant (Faridabad) |
| **Adv. Neha Saxena** | Corporate & Litigation Lawyers | Verified Advocate (Saket Court) |

---

## 📄 License
MIT License
