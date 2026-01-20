# What-If Factory 🏭

**Fabrika Karar Simülatörü - io.net Hackathon Projesi**

Endüstri mühendisliği öğrencileri ve fabrika yöneticileri için oyunlaştırılmış karar simülasyon aracı. AI ajanları kullanarak gerçekçi fabrika yönetimi senaryolarını simüle eder.

## 🎯 Proje Hakkında

What-If Factory, fabrika yöneticilerinin karşılaştığı kritik kararları sıfır maliyetle test etmelerine olanak sağlayan bir simülasyon platformudur. **io Intelligence** ajanları kullanarak:

- ✅ Üretim değişimlerini hesaplar
- 💰 Maliyet etkilerini analiz eder
- ⚠️ Risk seviyelerini değerlendirir
- 🎯 Kararları kategorize eder (Optimal/Güvenli/Riskli/Tehlikeli)
- 📊 Dönemsel özet raporlar oluşturur

## 🤖 io Intelligence Kullanımı

Proje **3 AI ajanını zincirleme şekilde** kullanır:

1. **Custom Agent**: Kararın simülasyonunu yapar, üretim/maliyet/risk etkilerini hesaplar
2. **Classification Agent**: Kararı kategorize eder ve öneri sunar
3. **Summary Agent**: Dönem sonunda tüm kararları özetleyen rapor üretir

Bu ajanlar **io.net** üzerinden çalışır ve OpenAI uyumlu API kullanır.

## 🎮 Özellikler

### Oyunlaştırma
- 🏆 **Puan Sistemi**: Her karar puan kazandırır veya kaybettirir
- ⭐ **Seviye Sistemi**: Junior → Middle → Senior Manager
- 🏅 **Rozet Sistemi**: Risk Avcısı, Maliyet Ustası, Verim Şampiyonu gibi rozetler
- 📈 **İlerleme Takibi**: Gerçek zamanlı puan ve seviye gösterimi

### Simülasyon
- 10 farklı kritik fabrika kararı
- Gerçekçi sonuç hesaplamaları
- Yan etki analizi
- Risk değerlendirmesi
- **📉 Dinamik & Acımasız Piyasalar**: Her 3 ayda bir değişen ve fabrikayı sarsan dış koşullar (Mavi Kartlar).
- **🚨 Yüksek Riskli Ekonomi**: Hata yapmanın bedeli ağırdır (Örn: -500k TL). Sorunlar görmezden gelinemez, çözülmezse fabrika batar.
- **Detaylı Raporlama**: Her ay sonunda AI destekli "Yönetici Özeti" modalı
- **Kurumsal Denge Karnesi**: Kalite, Marka ve İnovasyon puanları
- **Sistematik Bakım**: Bakım politikası ve fabrika yıpranma simülasyonu
- **Veri Entegrasyonu**: Kendi fabrika verilerinizi yükleyin ve analiz edin

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- io.net API Key (veya OpenAI API Key test için)

### Adımlar

1. **Repoyu klonlayın**
```bash
git clone https://github.com/YOUR_USERNAME/what-if-factory.git
cd what-if-factory
```

2. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

3. **API Key ayarlayın**
```bash
# .env dosyası oluşturun (gitignore'da olduğu için manuel oluşturmanız gerekir)
# Aşağıdaki içeriği .env dosyasına yapıştırın:

IO_API_KEY=your_actual_io_net_api_key_here
IO_BASE_URL=https://api.io.net/v1

# veya OpenAI ile test için:
# OPENAI_API_KEY=your_openai_key
# IO_BASE_URL=https://api.openai.com/v1
```

4. **Uygulamayı çalıştırın**
```bash
streamlit run Fabrika_Yönetimi.py
```

## 📖 Kullanım

1. **Model Seçimi**: Sidebar'dan kullanmak istediğiniz modeli seçin
2. **Veri Yükleme** (Opsiyonel): Fabrika verilerinizi yükleyin
3. **Karar Seçimi**: Ana ekrandan bir karar seçin
4. **Simülasyon**: "Kararı Uygula" butonuna basın
5. **Sonuçları İnceleyin**: AI ajanları sonuçları analiz edecek
6. **Rapor**: Dönem sonunda özet rapor oluşturun

## 🏗️ Proje Yapısı

```
what-if-factory/
├── app.py              # Ana Streamlit uygulaması
├── agents.py           # io Intelligence ajan wrapper'ları
├── prompts.py          # AI ajan system prompt'ları
├── utils.py            # Yardımcı fonksiyonlar (dosya parse, gamification)
├── requirements.txt    # Python bağımlılıkları
├── .env.example        # API key şablonu
└── README.md           # Bu dosya
```

## 🧠 Teknik Detaylar

### Agent Chain
```
Kullanıcı Kararı
    ↓
Custom Agent (Simülasyon)
    ↓
Classification Agent (Kategorizasyon)
    ↓
[Dönem Sonu] → Summary Agent (Rapor)
```

### Teknoloji Stack
- **Frontend**: Streamlit
- **AI Backend**: io.net Intelligence API (OpenAI compatible)
- **Veri İşleme**: pandas, PyMuPDF, openpyxl
- **Dil**: Python 3.8+

## 🎨 Ekran Görüntüleri

*(Demo videosu için yer ayrılmıştır)*

## 🏆 io.net Hackathon Kriterleri

✅ **IO Intelligence kullanımı**: 3 ajan zincirleme şekilde kullanılıyor  
✅ **Çalışır demo**: Streamlit ile tam fonksiyonel uygulama  
✅ **Gerçek problem çözümü**: Fabrika yönetimi eğitimi maliyeti düşürülüyor  
✅ **Dokümantasyon**: Detaylı README ve kod açıklamaları  
✅ **Video**: Demo videosu hazırlanacak  

## 👥 Katkıda Bulunanlar

- **Göktuğ Saylam** - Geliştirici

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🔗 Bağlantılar

- [io.net](https://io.net)
- [Streamlit](https://streamlit.io)

---

**Made with ❤️ for io.net Hackathon**
