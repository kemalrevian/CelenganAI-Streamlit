import os
import re
import json
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent

# Load environment
load_dotenv()

def extract_chart_json(text: str) -> dict | None:
    """Mencoba mengekstrak JSON chart dari output LLM."""
    try:
        parsed = json.loads(text.strip())
        if parsed.get("type") == "chart":
            return parsed
    except Exception:
        pass

    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1))
            if parsed.get("type") == "chart":
                return parsed
        except Exception:
            pass

    match = re.search(r'\{[^{}]*"type"\s*:\s*"chart".*?\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return None

def ask_financial_assistant(user_message: str, user_id: int, history: list = None) -> str | dict:
    """
    Fungsi ini menerjemahkan bahasa manusia menjadi query SQL, 
    mengeksekusinya ke database SQLite, dan merangkai jawabannya.
    """
    # Connect LangChain ke database SQLite Streamlit
    db_uri = "sqlite:///database/Celengan_AI_st_database.db"
    db = SQLDatabase.from_uri(db_uri)
    
    # LLM Model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # SQL Agent
    agent_executor = create_sql_agent(
        llm=llm, 
        db=db, 
        agent_type="openai-tools", 
        verbose=True
    )
    
    # Format history
    history_text = ""
    if history:
        history_text = "Riwayat percakapan sebelumnya:\n"
        for msg in history:
            role = "AI" if msg.get("role") == "assistant" else "User"
            history_text += f"[{role}]: {msg.get('content')}\n"
        history_text += "\n"

    # System Prompt
    prompt = f"""
    Sebagai AI Agent bernama Celengan.ai (Asisten Keuangan Pribadi Gen Z), tugas utamamu adalah membantu user mencatat, menghitung, dan menganalisis keuangan mereka.

    ATURAN WAJIB (JANGAN DILANGGAR):
    1. KAMU MELAYANI USER ID = {user_id}. SETIAP query ke tabel 'transactions' atau 'budgets' WAJIB menggunakan klausa 'WHERE user_id = {user_id}'.
    2. JANGAN PERNAH menyebutkan nama tabel, ID user, proses sistem, atau hal teknis (seperti SQL, eksekusi query) kepada user. Jawablah layaknya teman ngobrol biasa.
    3. Jika user MENYAPA (halo, hai) atau TANYA BISA BANTU APA, JELASKAN DENGAN LENGKAP bahwa kamu bisa:
       - Mencatat pengeluaran & pemasukan sehari-hari
       - Mengecek total pengeluaran per bulan/kategori
       - Membuatkan grafik visual (Pie, Bar, Line chart) untuk analisis keuangan
       JANGAN LAKUKAN QUERY SQL UNTUK INI. Langsung jawab saja.
    4. PENTING: Jika user BERCERITA MENGELUARKAN/MENDAPAT UANG (misal: "tadi abis beli sate 20rb", "gua beli skincare 200 ribu"), ITU ADALAH PERINTAH MENCATAT TRANSAKSI. Lakukan eksekusi SQL INSERT secara otomatis tanpa harus menunggu kata "tolong catat".
    5. Jika user HANYA BASA-BASI MURNI atau BERTERIMA KASIH (thanks, makasih, sip, oke) yang TIDAK MENGANDUNG NOMINAL UANG, barulah BALAS SINGKAT SAJA dengan ramah. JANGAN LAKUKAN QUERY SQL.
    6. Gunakan bahasa Indonesia gaul (lu/gua) dan santai.
    7. Tampilkan nominal uang dengan format ribuan yang rapi (contoh: Rp 30.000). Gunakan emoji.

    Riwayat Chat:
    {history_text}
    
    Pesan User saat ini: "{user_message}"
    
    ATURAN KHUSUS GRAFIK:
    8. PENTING: Jika user meminta grafik PENGELUARAN, WAJIB filter query SQL-mu HANYA untuk `type = 'expense'`. JANGAN masukkan pemasukan (seperti gaji, bonus) ke dalam grafik pengeluaran.
    9. Jika user meminta GRAFIK, CHART, VISUALISASI, DIAGRAM (lingkaran/batang),
       jangan jawab dengan teks biasa sama sekali.
       Kembalikan HANYA satu JSON object (tanpa teks lain, tanpa markdown) dengan format:
       {{"type":"chart","chart_type":"pie","title":"judul grafik","data":[{{"name":"Kategori","value":50000}}]}}
    10. Pilih chart_type: "pie", "bar", atau "line". Field "value" HARUS berupa angka.
    """
    
    # Invoke agent
    response = agent_executor.invoke({"input": prompt})
    raw_output = response["output"]

    # Cek output JSON untuk grafik
    chart_data = extract_chart_json(raw_output)
    if chart_data:
        return chart_data  

    return raw_output
