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

def get_dynamic_quick_actions(budget: float, satisfaction: float, risk: float, production: float) -> list:
    """
    Generate dynamic quick actions based on current KPI state
    """
    actions = []
    
    # Crisis Scenario (Negative Budget)
    if budget <= 0:
        actions.extend([
            ("🆘 Acil Kredi Çek", "🏦 Bankadan acil durum kredisi al (%20 faiz)"),
            ("📉 Küçülmeye Git", "👥 Personelin %10'unu işten çıkar"),
            ("🛑 Harcamaları Durdur", "🚫 Tüm gereksiz harcamaları dondur"),
            ("💸 Varlıkları Sat", "🏭 Kullanılmayan makineleri sat")
        ])
        return actions[:4]  # Return only crisis actions if in crisis
    
    # High Risk Scenario
    if risk > 65:
        actions.append(("🛡️ Güvenlik Denetimi", "👷 Kapsamlı İSG denetimi yap"))
        actions.append(("📉 Üretimi Yavaşlat", "⚠️ Riskleri azaltmak için hızı düşür"))
    
    # Low Satisfaction Scenario
    if satisfaction < 45:
        actions.append(("🎉 Moral Etkinliği", "🎈 Çalışanlar için etkinlik düzenle"))
        actions.append(("💰 Prim Dağıt", "💵 Herkese yarım maaş ikramiye ver"))
    
    # Low Production Scenario
    if production < 80:
        actions.append(("⚙️ Bakım Yap", "🔧 Makine bakımlarını hemen yap"))
        actions.append(("⚡ Fazla Mesai", "clock: Bu hafta sonu çalışması koy"))
    
    # High Budget Opportunity
    if budget > 5000000:
        actions.append(("🤖 Otomasyon Yatırımı", "🦾 Yeni robot kollar satın al"))
        actions.append(("🎓 Eğitim Programı", "📚 Tüm personele ileri eğitim ver"))
    
    # Standard Actions (Fill remaining slots)
    standard_actions = [
        ("🔧 Bakımı Ertele", "🔧 Preventif bakımları 3 ay ertele"),
        ("🏭 Vardiya Artır", "🏭 Vardiya sistemini 2'den 3'e çıkar"),
        ("👥 Yeni İşe Alım", "👥 10 yeni operatör işe al"),
        ("📊 Kalite Kontrol", "📊 Kalite kontrol süreçlerini sıkılaştır")
    ]
    
    # Add standard actions if we don't have enough
    for act in standard_actions:
        if len(actions) < 4 and act not in actions:
            actions.append(act)
            
    return actions[:4]  # Return top 4 relevant actions

def get_dynamic_quick_actions_placeholder(budget: float, satisfaction: float, risk: float, production: float) -> list:
    return []

# Pre-defined decision options

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
        },
        {
            "sector": "Gıda",
            "product": "Organik Atıştırmalık",
            "situations": [
                "Hasat verimi düşük",
                "Paketleme hijyen sorunu",
                "Yeni sağlık regülasyonları",
                "Soğuk zincir kırılması",
                "Organik sertifika denetimi"
            ]
        },
        {
            "sector": "Tekstil",
            "product": "Spor Giyim",
            "situations": [
                "Kumaş tedarikinde gecikme",
                "Moda trendi değişimi",
                "Dikiş makinesi arızaları",
                "İşçi sendikası talepleri",
                "Boya kalitesi sorunu"
            ]
        },
        {
            "sector": "Otomotiv Yan Sanayi",
            "product": "Fren Balatası",
            "situations": [
                "Ana üretici sipariş artışı",
                "Hammadde çelik fiyat artışı",
                "CNC tezgah kalibrasyon hatası",
                "Kalite kontrol reddi",
                "Lojistik grevi"
            ]
        },
        {
            "sector": "Kimya",
            "product": "Temizlik Ekipmanları",
            "situations": [
                "Tehlikeli madde sızıntı riski",
                "Plastik hammadde zammı",
                "Karışım formül hatası",
                "Depolama alanı yetersizliği",
                "Atık yönetimi cezası"
            ]
        },
        {
            "sector": "Elektronik",
            "product": "Akıllı Ev Sensörleri",
            "situations": [
                "Çip tedarik krizi",
                "Lehimleme hatası oranı yüksek",
                "Yazılım güncelleme sorunu",
                "Nadir toprak element eksikliği",
                "Test cihazı kalibrasyonu"
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
    
    
    # Convert string situations to detailed objects for initial profile
    initial_issues = []
    # Possible penalty types
    penalty_types = ['production', 'budget', 'satisfaction', 'risk']
    
    for issue_text in random.sample(selected_sector['situations'], 2):
        p_type = random.choice(penalty_types)
        p_val = 0
        consequence_text = ""
        
        if p_type == 'production':
            p_val = -random.randint(3, 8)
            consequence_text = f"Her ay Üretim {p_val}% azalır"
        elif p_type == 'budget':
            p_val = -random.randint(50000, 150000)
            consequence_text = f"Her ay Bütçe {p_val:,} TL azalır"
        elif p_type == 'satisfaction':
            p_val = -random.randint(2, 5)
            consequence_text = f"Her ay Memnuniyet {p_val}% azalır"
        elif p_type == 'risk':
            p_val = random.randint(3, 7)
            consequence_text = f"Her ay Risk {p_val}% artar"
            
        initial_issues.append({
            "title": issue_text,
            "description": "Sektörel bir zorluk yaşanıyor.",
            "consequence": consequence_text,
            "penalty": {"type": p_type, "value": p_val}
        })

    profile = {
        "sector": f"{selected_sector['sector']} - {selected_sector['product']}",
        "active_issues": initial_issues,
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
        "machine_count": int(blue_collar / 4) + random.randint(5, 15), # 1 machine per 4 workers + buffer
        "initial_budget": random.randint(2000000, 8000000),  # 2-8M TL
        "initial_satisfaction": random.randint(60, 85),  # %
        "initial_production_rate": random.randint(70, 90),  # %
        "initial_risk": random.randint(20, 50)  # %
    }
    
    return profile
