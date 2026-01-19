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
        return "Stajyer", 0, 0
    elif score < 200:
        return "Genç Yönetici", 1, score / 200
    elif score < 500:
        return "Orta Düzey Yönetici", 2, (score - 200) / 300
    else:
        return "Kıdemli Yönetici", 3, 1.0

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
            "product": "Fren Diskleri & Balata",
            "situations": [
                {"title": "Ana üretici siparişleri %20 artırdı, kapasite yetersiz", "desc": "Tofaş/Ford gibi ana üreticiler acil ek üretim talep ediyor, mevcut hatlar yetmiyor."},
                {"title": "Çelik hammadde fiyatlarında ani artış", "desc": "Global çelik borsasındaki dalgalanma maliyetleri direkt vurdu."},
                {"title": "CNC tezgahlarında kalibrasyon sorunları var", "desc": "Hassas işleme yapan robotlarda mikron seviyesinde sapmalar tespit edildi."},
                {"title": "ISO 16949 denetimi yaklaşıyor, belge eksikleri var", "desc": "Kalite departmanı denetim öncesi panik halinde, prosedürler güncel değil."}
            ]
        },
        {
            "sector": "Tekstil & Konfeksiyon",
            "product": "Denim Pantolon Üretimi",
            "situations": [
                {"title": "Boya kalitesinde dalgalanmalar var, iade oranı arttı", "desc": "Son parti kumaşlarda renk solması şikayetleri geliyor, yıkama hanede sorun var."},
                {"title": "İhracat müşterisi 'Sürdürülebilirlik Belgesi' istiyor", "desc": "Avrupalı müşteri karbon ayak izi raporu olmadan alımı durduracağını belirtti."},
                {"title": "Mevsimsel işçi bulmakta zorlanılıyor", "desc": "Hasat zamanı geldiği için operatörlerin çoğu işi bırakıp memlekete gidiyor."},
                {"title": "Pamuk fiyatları global pazarda yükselişte", "desc": "Hindistan'daki kuraklık nedeniyle iplik fiyatlarına %15 zam geldi."}
            ]
        },
        {
            "sector": "Metal İşleme",
            "product": "Endüstriyel Raf Sistemleri",
            "situations": [
                {"title": "Kaynak robotlarında sık arıza yaşanıyor", "desc": "Otomatik kaynak hattında duruşlar arttı, bakım ekibi yetersiz kalıyor."},
                {"title": "Lojistik maliyetleri kar marjını eritiyor", "desc": "Nakliye fiyatları arttığı için karlılık %5 seviyesine kadar düştü."},
                {"title": "İş güvenliği uzmanı havalandırma sistemi uyarısı yaptı", "desc": "Atölye içindeki duman seviyesi yasal sınırın üzerinde, acil yatırım lazım."},
                {"title": "Büyük bir depo projesi için acil teklif isteniyor", "desc": "Getir/Amazon deposu için devasa bir ihale var ama mühendislik ekibi dolu."}
            ]
        },
        {
            "sector": "Plastik Enjeksiyon",
            "product": "Beyaz Eşya Parçaları",
            "situations": [
                {"title": "Enjeksiyon kalıplarının bakımı gecikti", "desc": "Kalıplarda çapaklanma başladı, parça kalitesi düşüyor."},
                {"title": "Petrol fiyatları arttığı için granül hammadde pahalandı", "desc": "Plastik hammaddesi petrole endeksli olduğu için maliyetler fırladı."},
                {"title": "Enerji maliyetleri üretimi kârsız hale getiriyor", "desc": "Elektrik faturası geçen aya göre 2 katına çıktı, makinalar çok yakıyor."},
                {"title": "Geri dönüştürülmüş hammadde kullanımı zorunluluğu geldi", "desc": "AB yasaları gereği üretimde %30 recyle malzeme şartı getirildi."}
            ]
        },
        {
            "sector": "Gıda Ambalaj",
            "product": "Oluklu Mukavva Kutu",
            "situations": [
                {"title": "Kağıt tedarikinde global kıtlık var", "desc": "Kağıt fabrikaları siparişlere yetişemiyor, stoklar sadece 3 günlük kaldı."},
                {"title": "Müşteriler daha hızlı teslimat talep ediyor", "desc": "E-ticaret patlaması nedeniyle müşteriler 'dün sipariş verdim bugün gelsin' modunda."},
                {"title": "Matbaa makinesinde renk tutmuyor", "desc": "Baskı makinesinin silindirleri aşınmış, logolar yanlış renk çıkıyor."},
                {"title": "Depoda nem sorunu oluştu, stoklar risk altında", "desc": "Son yağmurlarda depo çatısı aktı, mukavvalar yumuşamaya başladı."}
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
    
    for issue_data in random.sample(selected_sector['situations'], 2):
        p_type = random.choice(penalty_types)
        p_val = 0
        consequence_text = ""
        resolution_cost = {}
        
        if p_type == 'production':
            p_val = -random.randint(8, 15)
            consequence_text = f"Her ay Üretim {p_val}% azalır"
            cost_amount = random.randrange(150000, 400000, 10000)
            resolution_cost = {'budget': cost_amount, 'resource': 'Teknik Servis'}
            
        elif p_type == 'budget':
            # Major financial hit
            p_val = -random.randrange(150000, 600000, 10000)
            consequence_text = f"Her ay Bütçe {p_val:,} TL azalır"
            # Resolution cost is heavy investment
            cost_amount = abs(p_val) * random.choice([2, 3])
            resolution_cost = {'budget': cost_amount, 'resource': 'Finansal Yapılandırma'}
            
        elif p_type == 'satisfaction':
            p_val = -random.randint(5, 12)
            consequence_text = f"Her ay Memnuniyet {p_val}% azalır"
            cost_amount = random.randrange(100000, 300000, 10000)
            resolution_cost = {'budget': cost_amount, 'resource': 'İK Desteği'}
            
        elif p_type == 'risk':
            p_val = random.randint(10, 25)
            consequence_text = f"Her ay Risk {p_val}% artar"
            cost_amount = random.randrange(150000, 450000, 10000)
            resolution_cost = {'budget': cost_amount, 'resource': 'Denetim'}
            
        initial_issues.append({
            "title": issue_data['title'],
            "description": issue_data['desc'],
            "category": "problem", # Explicitly set as problem
            "consequence": consequence_text,
            "ongoing_penalty": {"type": p_type, "value": p_val},
            "resolution_cost": resolution_cost
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
