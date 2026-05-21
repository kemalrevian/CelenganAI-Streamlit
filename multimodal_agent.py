import os
import base64
from openai import OpenAI
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load env
load_dotenv()
client = OpenAI()

# Skema Data (Pydantic)
class TransactionExtraction(BaseModel):
    amount: float = Field(description="Nominal uang dalam angka saja, tanpa titik atau koma (contoh: 35000)")
    type: str = Field(description="Pilih salah satu: 'income' jika mendapat uang, atau 'expense' jika mengeluarkan uang")
    category: str = Field(description="Kategori transaksi, contoh: 'Makanan & Minuman', 'Transportasi', 'Hiburan', 'Gaji'")
    description: str = Field(description="Deskripsi singkat tentang barang/jasa yang ditransaksikan")

def transcribe_audio(audio_file) -> str:
    """
    Mengubah file suara audio (dari Streamlit audio_input) menjadi teks menggunakan Whisper.
    `audio_file` adalah objek UploadedFile dari Streamlit.
    """
    # OpenAI Whisper
    audio_file.name = "audio.wav"
    
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text

def parse_receipt_image(image_file) -> dict:
    """
    Mengekstrak data dari gambar struk menggunakan GPT-4o-mini Vision.
    `image_file` adalah objek UploadedFile dari Streamlit.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(TransactionExtraction)
    
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    messages = [
        (
            "system", 
            "Kamu adalah asisten keuangan Gen Z. Tugasmu adalah membaca gambar struk belanja. "
            "Ekstrak total harga akhir (amount), tentukan kategorinya (category), pastikan jenisnya 'expense' (type), "
            "dan buat deskripsi singkat mengenai nama toko atau barang dominan di struk tersebut. "
            "Abaikan teks yang tidak penting."
        ),
        HumanMessage(
            content=[
                {"type": "text", "text": "Tolong ekstrak data transaksi dari struk belanja ini:"},
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        )
    ]
    
    # Invoke agent
    result = structured_llm.invoke(messages)
    return result.model_dump()
