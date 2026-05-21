import sqlite3
from datetime import datetime

def init_db():
    # Menghubungkan ke file database
    conn = sqlite3.connect('Celengan_AI_st_database.db')
    cursor = conn.cursor()

    print("Membuat tabel database Celengan.AI...")

    # Membuat Tabel Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        job_status TEXT,                 -- Kolom baru (Opsional)
        financial_goal TEXT,             -- Kolom baru (Opsional)
        initial_balance REAL DEFAULT 0,  -- Kolom baru (Opsional, default 0)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

    # 2. Membuat Tabel Transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL, -- Berisi 'income' atau 'expense'
            category TEXT NOT NULL, -- Contoh: 'Makanan', 'Transportasi', 'Gaji'
            description TEXT, -- Contoh: 'Kopi Susu Senopati'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # 3. Membuat Tabel Budgets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            limit_amount REAL NOT NULL,
            month_year TEXT NOT NULL, -- Format: 'MM-YYYY' (Contoh: '05-2026')
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Database dan 3 tabel utama berhasil dibuat!")

if __name__ == '__main__':
    init_db()