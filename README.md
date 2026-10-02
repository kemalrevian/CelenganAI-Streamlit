# 🪙 CELENGAN.AI
**Asisten Keuangan Pribadi Gen Z**

AI-powered personal finance assistant — chat naturally to log expenses, analyze spending, and visualize your money.

---

## 🧩 Problem

Most people forget or are simply too lazy to log their daily expenses. Traditional finance apps feel overwhelming — too many buttons, manual number inputs, confusing category selections, or complicated spreadsheets. With **Celengan.AI**, users just need to chat casually. Expenses and income are recorded automatically — even by voice or by uploading a receipt photo.

---

## ✨ Key Features

- **Natural Language Logging** — Chat casually (e.g. *"tadi beli kopi 30rb"*) and the AI auto-records the transaction into the database via a LangChain SQL Agent.
- **Receipt Scanner** — Upload a receipt photo and GPT-4o Vision auto-extracts the amount, category, and description.
- **Voice Input** — Speak your expense and OpenAI Whisper transcribes it instantly into a recordable command.
- **Smart Chart Visualization** — Request spending breakdowns and get interactive **Pie**, **Bar**, or **Line** charts rendered live inside the app.
- **Multi-User Auth System** — Secure login & register with SHA-256 password hashing. Every query is fully isolated per user.
- **Monthly Overview** — Navigate past months with prev/next controls to review total spending history.

---

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python | Core language |
| Streamlit | Web UI framework |
| LangChain | SQL Agent orchestration |
| OpenAI GPT-4o-mini | Natural language understanding & chart generation |
| OpenAI GPT-4o Vision | Receipt image parsing |
| OpenAI Whisper | Voice-to-text transcription |
| SQLite | Local database for users & transactions |
| Pydantic | Structured output schema for multimodal agent |
| Altair | Interactive chart rendering |

---

## 🗂️ Project Structure

```
CelenganAI (st)/
├── app.py                  # Main Streamlit app (UI, auth, chat interface)
├── ai_agent.py             # LangChain SQL Agent (natural language → SQL)
├── multimodal_agent.py     # GPT-4o Vision (receipt) + Whisper (voice)
├── database/
│   ├── create_db.py        # Database initializer (3 tables: users, transactions, budgets)
│   ├── dummy_db.py         # Dummy data seeder for testing
│   └── Celengan_AI_st_database.db  # SQLite database file
└── .env                    # API keys (OPENAI_API_KEY)
```

---

## 🚀 How to Run

```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI API key in .env
# OPENAI_API_KEY=sk-...

# 4. Run the app
streamlit run app.py
```

App will be available at: **http://localhost:8501**

---

## 🗄️ Database Schema

**`users`** — Stores registered accounts  
**`transactions`** — Stores all income/expense entries per user  
**`budgets`** — Stores monthly budget limits per category  

---

## 💬 Example Usage

| User says | What happens |
|---|---|
| *"tadi beli makan siang 25rb"* | AI inserts an expense of Rp 25,000 → Food category |
| *"dapat gaji bulan ini 5 juta"* | AI inserts an income of Rp 5,000,000 → Salary category |
| *"buatin grafik pengeluaran bulan ini"* | AI queries DB and returns a Pie chart |
| 📷 Upload struk Indomaret | AI reads the receipt and auto-fills amount & category |
| 🎤 Record voice "beli bensin 50 ribu" | Whisper transcribes → AI records the expense |
