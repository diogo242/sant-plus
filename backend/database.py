import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "santeplus.db"

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Table des patients
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            wallet_address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des rendez-vous
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_email TEXT NOT NULL,
            hospital_id TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_email) REFERENCES patients(email)
        )
    ''')
    
    # Table des documents médicaux
    c.execute('''
        CREATE TABLE IF NOT EXISTS medical_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_email TEXT NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            ipfs_cid TEXT,
            btc_tx_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_email) REFERENCES patients(email)
        )
    ''')
    
    # Table des transactions Lightning
    c.execute('''
        CREATE TABLE IF NOT EXISTS lightning_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_hash TEXT UNIQUE NOT NULL,
            patient_email TEXT NOT NULL,
            amount_sats INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    """Connexion à la base de données"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_patient(email: str, name: str, phone: str = None):
    """Sauvegarde un nouveau patient"""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO patients (email, name, phone) VALUES (?, ?, ?)",
        (email, name, phone)
    )
    conn.commit()
    conn.close()

def save_appointment(patient_email: str, hospital_id: str, hospital_name: str, 
                     date: str, time_slot: str, status: str = 'pending'):
    """Sauvegarde un rendez-vous"""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO appointments (patient_email, hospital_id, hospital_name, date, time_slot, status) 
         VALUES (?, ?, ?, ?, ?, ?)",
        (patient_email, hospital_id, hospital_name, date, time_slot, status)
    )
    conn.commit()
    conn.close()

def get_patient_appointments(email: str):
    """Récupère les rendez-vous d'un patient"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM appointments WHERE patient_email = ?", (email,))
    appointments = c.fetchall()
    conn.close()
    return [dict(apt) for apt in appointments]
