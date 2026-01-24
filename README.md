# What-If Factory 🏭

**Fabrika Karar Simülatörü - io.net Hackathon Projesi**

Endüstri mühendisliği öğrencileri ve fabrika yöneticileri için oyunlaştırılmış karar simülasyon aracı. **io Intelligence** altyapısını kullanarak gerçekçi fabrika yönetimi senaryolarını simüle eder ve sonuçlarını analiz eder.

---

## 🎯 Proje Hakkında (Proje Kapsamı)

What-If Factory, fabrika yöneticilerinin karşılaştığı kritik kararları sıfır maliyetle test etmelerine olanak sağlayan bir **Masaüstü/Web Uygulamasıdır** (Streamlit).

Bu proje ile:
- Fabrika yönetim kararlarının (atama, yatırım, kriz yönetimi) sonuçlarını **simüle edebilir**,
- Hatalı kararların maliyetini sanal ortamda **görebilir**,
- **io Intelligence** destekli analizler ile "Güvenli" veya "Riskli" yönetim stratejilerini öğrenebilirsiniz.

Değerlendirmeye alınacak **çalışır ürün**, Streamlit arayüzü ile eksiksiz bir deneyim sunmaktadır.

---

## � io Intelligence Kullanımı (Zorunlu)

Bu projenin beyni **io Intelligence** (io.net) üzerine kuruludur. Proje, sadece basit bir kural tabanlı sistem değil, bağlama duyarlı **Generative AI** kullanan bir simülatördür.

### Sistem Mimarisi İçerisindeki Rolü
Projede **3 farklı AI Ajanı**, zincirleme (Chain of Thought) bir mimari ile çalışır:

1.  **🏭 Custom Agent (Simülasyon Motoru)**:
    *   **Görevi:** Kullanıcının verdiği kararı (Örn: "Yeni robot al") ve fabrikanın o anki durumunu (Bütçe, Risk, Memnuniyet) analiz eder.
    *   **Çıktısı:** Kararın matematiksel sonuçlarını hesaplar (Üretim %10 artar, Bütçe -500k azalır vb.) ve JSON formatında döndürür.
2.  **⚖️ Classification Agent (Risk Analisti)**:
    *   **Görevi:** Simülasyon motorundan gelen sonuçları "Endüstri Mühendisliği" prensiplerine göre değerlendirir.
    *   **Çıktısı:** Kararı etiketler: **Optimal**, **Güvenli**, **Riskli** veya **Tehlikeli**.
3.  **📝 Summary Agent (Hikaye Anlatıcısı)**:
    *   **Görevi:** Dönem (ay) sonunda yapılan tüm hamleleri toplar.
    *   **Çıktısı:** Kullanıcıya bir "Yönetici Özeti" hazırlar, dönemin hikayesini ve gidişatını anlatır.

### Projeye Sağladığı Katkılar
*   **Gerçekçilik:** Sabit if-else kuralları yerine, AI her seferinde bağlama uygun, beklenmedik "yan etkiler" ve "krizler" üretebilir.
*   **Dinamiklik:** Fabrika durumu kötüye gittiğinde AI daha acımasız senaryolar (Grev, Makine Arızası) üretir.

---

## 🚀 Kurulum ve Çalıştırma (Adım Adım)

Teknik bilgisi olmayan bir kullanıcının dahi projeyi çalıştırabilmesi için adımlar aşağıdadır:

### 1. Gereksinimler
*   Bilgisayarınızda **Python** yüklü olmalıdır. (Yüklü değilse [python.org](https://www.python.org/downloads/) adresinden indirin).
*   Bir **io.net API Anahtarı** (veya test için OpenAI API anahtarı).

### 2. Projeyi İndirme (GitHub)
Bu sayfada sağ üstteki **"Code"** butonuna tıklayın ve **"Download ZIP"** seçeneğini seçin. İndirilen dosyayı masaüstünüze çıkarın (klasör olarak).

*Veya terminal kullanmayı biliyorsanız:*
```bash
git clone https://github.com/GoktugSaylam/what-if-factory.git
cd what-if-factory
```

### 3. Kurulum (Windows/Mac)
Proje klasörünün içine girin. Bir terminal/komut satırı açın ve şu komutu yazarak gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

### 4. Ayarların Yapılması (.env)
Proje klasöründe `.env.example` adında bir dosya göreceksiniz.
1.  Bu dosyanın adını `.env` olarak değiştirin (veya yeni bir `.env` dosyası oluşturun).
2.  Dosyayı Not Defteri ile açın ve anahtarınızı yapıştırın:

```ini
IO_API_KEY=sk-sizin-io-net-api-anahtariniz
IO_BASE_URL=https://api.io.net/v1
# Eğer OpenAI kullanacaksanız URL: https://api.openai.com/v1
```

## 🚀 Çalıştırma

Uygulamayı başlatmak için:

```bash
streamlit run Fabrika_Yönetimi.py
```

*veya eski komut sistemiyle uyumluluk için:*

```bash
streamlit run Simulasyon_Merkezi.py
```

Tarayıcınızda otomatik olarak **http://localhost:8501** adresi açılacak ve oyun başlayacaktır! 🎉

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
├── Fabrika_Yönetimi.py # Ana Streamlit uygulaması
├── agents.py           # io Intelligence ajan wrapper'ları
├── prompts.py          # AI ajan system prompt'ları
├── utils.py            # Yardımcı fonksiyonlar (dosya parse, gamification)
├── requirements.txt    # Python bağımlılıkları
├── .env.example        # API key şablonu
└── README.md           # Bu dosya
```

---

## 🎥 Video Tanıtım

*(Buraya proje tamamlandığında YouTube veya dosya linki eklenecek)*

---

## 📝 Değerlendirme & Geri Bildirim Formu Detayları

Hackathon teslim dosyasında yer alacak bilgiler:
*   **GitHub Repo:** (Bu sayfa)
*   **Tanıtım Videosu:** (Eklenecek)
*   **Kısa Açıklama:** What-If Factory, io Intelligence destekli bir fabrika yönetim simülasyonudur.
*   **io Intelligence Görüşü:** Platformun sağladığı OpenAI uyumlu API yapısı sayesinde mevcut LLM uygulamaları saniyeler içinde io.net ekosistemine taşınabilmiştir. Hız ve maliyet avantajı geliştirme sürecini hızlandırmıştır.

---

## 🎮 Oyun Özellikleri

### Oyunlaştırma
- 🏆 **Puan Sistemi**: Her karar puan kazandırır veya kaybettirir.
- ⭐ **Seviye Sistemi**: Stajyer -> Junior -> Senior Manager.
- 🏅 **Rozet Sistemi**: "Risk Avcısı", "Maliyet Ustası" gibi başarımlar kazanılabilir.

### Simülasyon Mekanikleri
- **Dinamik Piyasalar**: Her 3 ayda bir değişen dış koşullar (Mavi Kartlar).
- **Yüksek Risk**: Hata yapmanın bedeli ağırdır. Risk %70'i geçerse fabrika batabilir.

---

## 👥 Katkıda Bulunanlar
- **Göktuğ Saylam** - Geliştirici

## 📝 Lisans
Bu proje MIT lisansı altında lisanslanmıştır.
