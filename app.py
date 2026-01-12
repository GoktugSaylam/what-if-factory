import streamlit as st

# Sayfa Ayarları
st.set_page_config(page_title="What-If Factory", page_icon="🏭", layout="wide")

# Başlık
st.title("🏭 What-If Factory: Karar Simülatörü")
st.markdown("---") # Çizgi çeker

# İki Sütunlu Yapı
sol_kolon, sag_kolon = st.columns([1, 2]) # Sol dar, sağ geniş olsun

with sol_kolon:
    st.header("Yönetici Paneli")
    st.info("Hoş geldin, Fabrika Müdürü!")
    
    # Basit bir puan göstergesi
    st.metric(label="Mevcut Puan", value="100", delta="Başlangıç")
    
    secim = st.radio("Bir aksiyon seç:", ["Bakım Yap", "Üretimi Hızlandır", "Personel Al"])

with sag_kolon:
    st.header("Simülasyon Ekranı")
    st.write(f"Şu an seçilen aksiyon: **{secim}**")
    
    if st.button("Kararı Uygula 🚀"):
        st.success("Karar sisteme gönderildi! (Henüz AI bağlı değil)")