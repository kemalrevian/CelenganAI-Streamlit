import sqlite3

def seed_db():
    conn = sqlite3.connect('Celengan_AI_st_database.db')
    cursor = conn.cursor()

    print("Mengisi data dummy ke Celengan_AI_st_database.db...")

    # 2 User Dummy
    users = [
        ('Budi', 'budi@email.com', 'hash123', 'Pegawai', 'Beli Rumah', 5000000),
        ('Siti', 'siti@email.com', 'hash456', 'Freelancer', 'Liburan ke Jepang', 2000000)
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO users (name, email, password_hash, job_status, financial_goal, initial_balance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users)

    # Transaksi Dummy (Budi = user_id 1, Siti = user_id 2)
    transactions = [
        # Transaksi Budi (user_id = 1)
        (1, 7000000, 'income', 'Gaji', 'Gaji bulanan kantor'),
        (1, 50000, 'expense', 'Makanan', 'Makan siang nasi padang'),
        (1, 150000, 'expense', 'Transportasi', 'Isi bensin motor'),
        # Transaksi Siti (user_id = 2)
        (2, 3000000, 'income', 'Freelance', 'Project desain logo'),
        (2, 35000, 'expense', 'Hiburan', 'Langganan Netflix'),
        (2, 120000, 'expense', 'Makanan', 'Nongkrong di cafe')
    ]
    cursor.executemany('''
        INSERT INTO transactions (user_id, amount, type, category, description)
        VALUES (?, ?, ?, ?, ?)
    ''', transactions)

    conn.commit()
    conn.close()
    print("Data dummy berhasil dimasukkan! 🚀")

if __name__ == '__main__':
    seed_db()