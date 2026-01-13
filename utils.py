"""
Utility functions for file parsing and gamification
"""
import pandas as pd
import fitz  # PyMuPDF
import json
from io import BytesIO
import random

def parse_file(uploaded_file) -> str:
    """
    Parse uploaded file and extract text content
    
    Supports: TXT, MD, PDF, CSV, XLSX, JSON
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        str: Extracted text content
    """
    try:
        filename = uploaded_file.name.lower()
        
        # Text files
        if filename.endswith(('.txt', '.md')):
            return uploaded_file.read().decode('utf-8')
        
        # PDF files
        elif filename.endswith('.pdf'):
            pdf_bytes = uploaded_file.read()
            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in pdf_doc:
                text += page.get_text()
            return text
        
        # CSV files
        elif filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            return df.to_string()
        
        # Excel files
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
            return df.to_string()
        
        # JSON files
        elif filename.endswith('.json'):
            data = json.load(uploaded_file)
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        else:
            return "Desteklenmeyen dosya formatı."
    
    except Exception as e:
        return f"Dosya okuma hatası: {str(e)}"

def calculate_level(score: int) -> tuple:
    """
    Calculate level based on score
    
    Returns:
        tuple: (level_name, level_number, progress_to_next_level)
    """
    if score < 0:
        return "Trainee", 0, 0
    elif score < 200:
        return "Junior Manager", 1, score / 200
    elif score < 500:
        return "Middle Manager", 2, (score - 200) / 300
    else:
        return "Senior Manager", 3, 1.0

def calculate_score_change(result: dict) -> int:
    """
    Calculate score based on simulation result
    Already included in result['score_impact']
    """
    return result.get('score_impact', 0)

def check_badges(history: list) -> list:
    """
    Check and award badges based on decision history
    
    Returns:
        list: List of earned badge dicts
    """
    badges = []
    
    if not history:
        return badges
    
    # Risk Avcısı: 5 karar, hiç "Yüksek" risk almadan
    high_risk_count = sum(1 for h in history if h['result'].get('risk_level') == 'Yüksek')
    if len(history) >= 5 and high_risk_count == 0:
        badges.append({"name": "🎯 Risk Avcısı", "desc": "5 karar aldın, hiç yüksek risk almadın!"})
    
    # Maliyet Ustası: 3 kararın hepsi maliyet düşüşü
    cost_decrease_count = sum(1 for h in history if h['result'].get('cost_change_percent', 0) < 0)
    if len(history) >= 3 and cost_decrease_count >= 3:
        badges.append({"name": "💰 Maliyet Ustası", "desc": "Maliyetleri düşük tutmayı başardın!"})
    
    # Verim Şampiyonu: Toplam üretim artışı %50+
    total_production = sum(h['result'].get('production_change_percent', 0) for h in history)
    if total_production >= 50:
        badges.append({"name": "🏆 Verim Şampiyonu", "desc": "Üretimi büyük oranda artırdın!"})
    
    # Deneyimli Yönetici: 10+ karar
    if len(history) >= 10:
        badges.append({"name": "🏅 Deneyimli Yönetici", "desc": "10'dan fazla karar aldın!"})
    
    return badges

# Pre-defined decision options
DECISION_OPTIONS = [
    "🏭 Vardiya sayısını artır (2'den 3'e)",
    "🔧 Bakım bütçesini %20 azalt",
    "👥 10 yeni operatör işe al",
    "📦 Stok seviyesini 2 katına çıkar",
    "⚙️ Makine parkını yenile (yatırım)",
    "💵 Personele %15 maaş zammı ver",
    "🚚 Teslimat süresini 3 güne düşür",
    "📊 Kalite kontrol adımlarını artır",
    "🔥 Fazla mesai uygula (hafta sonu dahil)",
    "🤖 Otomasyon sistemine geç (robot kollar)"
]

def generate_factory_profile() -> dict:
    """
    Generate a random factory profile for the simulation
    
    Returns:
        dict: Factory profile with sector, current status, employee count, etc.
    """
    sectors = [
        {
            "sector": "Otomotiv Yan Sanayi",
            "product": "Vites kutusu üretiyor",
            "situations": [
                "Siparişler patladı ama makineler eski",
                "Tedarik zinciri kırılgan, hammadde fiyatları arttı",
                "Kalite şikayetleri artıyor, müşteri kaybı riski var",
                "Enerji maliyetleri %30 arttı, sürdürülebilirlik baskısı var"
            ]
        },
        {
            "sector": "Tekstil",
            "product": "Denim kumaş üretiyor",
            "situations": [
                "Moda trendleri değişiyor, stok yönetimi kritik",
                "Çevre düzenlemeleri sıkılaştı, yeşil üretim zorunlu",
                "Çalışan memnuniyeti düşük, grev riski var",
                "İhracat pazarı daraldı, iç piyasa odaklı dönüşüm gerekli"
            ]
        },
        {
            "sector": "Gıda İşleme",
            "product": "Konserve gıda üretiyor",
            "situations": [
                "Hammaddeler bozulabilir, hijyen kritik",
                "Düzenleyici standartlar değişiyor",
                "Tedarik zinciri kesintiye uğradı",
                "Paketleme teknolojisi eski, verimlilik düşük"
            ]
        },
        {
            "sector": "Elektronik",
            "product": "Akıllı telefon şarj cihazı üretiyor",
            "situations": [
                "Teknoloji hızla değişiyor, ürün yaşam döngüsü kısa",
                "Çip krizi devam ediyor, tedarik sorunları var",
                "Rekabet yoğun, fiyat baskısı yüksek",
                "Kalite standartları çok yüksek, tolerans sıfır"
            ]
        },
        {
            "sector": "İlaç",
            "product": "Jenerik ilaç üretiyor",
            "situations": [
                "Düzenleyici onay süreçleri uzun",
                "Hammadde saflık standartları çok yüksek",
                "Rekabet fiyat baskısı altında",
                "Ar-Ge yatırımı zorunlu ama maliyetli"
            ]
        }
    ]
    
    selected_sector = random.choice(sectors)
    
    # Generate employee counts
    blue_collar = random.randint(100, 400)
    white_collar = random.randint(15, 50)
    
    # Calculate skill distribution for blue collar workers
    operators = int(blue_collar * 0.6)  # 60% operators
    technicians = int(blue_collar * 0.25)  # 25% technicians
    maintenance = blue_collar - operators - technicians  # Remaining for maintenance
    
    profile = {
        "sector": f"{selected_sector['sector']} - {selected_sector['product']}",
        "current_status": random.choice(selected_sector['situations']),
        "employee_count": {
            "blue_collar": blue_collar,
            "white_collar": white_collar,
            "total": blue_collar + white_collar,
            "skills": {
                "operators": operators,
                "technicians": technicians,
                "maintenance_crew": maintenance,
                "engineers": int(white_collar * 0.4),
                "quality_control": int(white_collar * 0.3),
                "management": white_collar - int(white_collar * 0.7)
            }
        },
        "initial_budget": random.randint(2000000, 8000000),  # 2-8M TL
        "initial_satisfaction": random.randint(60, 85),  # %
        "initial_production_rate": random.randint(70, 90),  # %
        "initial_risk": random.randint(20, 50)  # %
    }
    
    return profile
