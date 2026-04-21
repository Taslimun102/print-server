# 🖨️ Web-Based Printing Server (Flask + CUPS)

## 📌 Project Overview
This project is a web-based printing server that allows multiple users to upload files and print them through a browser interface.

## ⚙️ Technologies Used
- Flask (Web Framework)
- CUPS (Printing System)
- SQLite (Database)
- HTML + Bootstrap (UI)

## 🚀 Features
- User Signup/Login
- Admin Panel
- File Upload
- Print via CUPS
- Dropdown File Selection
- Print History Tracking

## 🖥️ System Architecture
User → Flask → lp command → CUPS → Printer/PDF

## 🔧 Setup Instructions

### 1. Install Dependencies
pip install -r requirements.txt

### 2. Setup Database
python3 init_db.py

### 3. Run Server
python3 app.py

### 4. Access
http://localhost:5000

## 🌐 LAN Access
Use:
http://YOUR-IP:5000

## 🔐 Default Behavior
- Users must signup first
- Admin also needs signup
- Role-based access control

## 📂 Output
Generated PDFs stored in:
CUPS spool or configured directory

## ⚠️ Note
Make sure CUPS service is running:
sudo systemctl start cups
