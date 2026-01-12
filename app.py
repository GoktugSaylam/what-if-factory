"""
What-If Factory - Fabrika Karar Simülatörü
io.net Hackathon Project
"""
import streamlit as st
import agents
import utils
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="What-If Factory 🏭",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .decision-button {
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        background: #ffd700;
        border-radius: 20px;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'context' not in st.session_state:
    st.session_state.context = ""
if 'badges' not in st.session_state:
    st.session_state.badges = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None
if 'current_classification' not in st.session_state:
    st.session_state.current_classification = None
if 'model' not in st.session_state:
    st.session_state.model = "gpt-4"

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    
    # API Model selection
    model_choice = st.selectbox(
        "Model Seçimi",
        ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
        help="io.net üzerinden çalışacak model"
    )
    st.session_state.model = model_choice
    
    st.markdown("---")
    
    # File upload section
    st.markdown("### 📁 Şirket Verisi Yükle")
    uploaded_file = st.file_uploader(
        "Fabrika verilerinizi yükleyin",
        type=['txt', 'pdf', 'csv', 'xlsx', 'json', 'md'],
        help="Verileriniz ajanların kararlarını daha gerçekçi yapmasını sağlar"
    )
    
    if uploaded_file:
        with st.spinner("Dosya işleniyor..."):
            context = utils.parse_file(uploaded_file)
            st.session_state.context = context
            st.success(f"✅ {uploaded_file.name} yüklendi!")
            with st.expander("📄 İçeriği Gör"):
                st.text(context[:500] + "..." if len(context) > 500 else context)
    
    st.markdown("---")
    
    # Summary generation
    if st.button("📊 Dönem Özeti Oluştur"):
        if st.session_state.history:
            with st.spinner("Özet hazırlanıyor..."):
                summary = agents.generate_summary(
                    st.session_state.history,
                    model=st.session_state.model
                )
                st.session_state.summary = summary
        else:
            st.warning("Henüz karar almadınız!")
    
    # Reset button
    if st.button("🔄 Yeni Oyun"):
        st.session_state.score = 0
        st.session_state.history = []
        st.session_state.badges = []
        st.session_state.current_result = None
        st.session_state.current_classification = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ Hakkında")
    st.markdown("""
    **What-If Factory** - Fabrika yöneticileri için oyunlaştırılmış karar simülasyon aracı.
    
    🤖 **io Intelligence** kullanarak gerçekçi sonuçlar üretir.
    
    Made for **io.net Hackathon**
    """)

# Main content
st.markdown('<h1 class="main-header">🏭 What-If Factory</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Fabrika Karar Simülatörü - Deneyerek Öğren!</p>', unsafe_allow_html=True)

# Metrics row
level_name, level_num, progress = utils.calculate_level(st.session_state.score)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💯 Puan", st.session_state.score)
with col2:
    st.metric("⭐ Seviye", level_name)
with col3:
    st.metric("📈 Toplam Karar", len(st.session_state.history))
with col4:
    st.metric("🏅 Rozet", len(st.session_state.badges))

# Progress bar
st.progress(progress, text=f"Sonraki seviyeye: %{int(progress*100)}")

# Badges display
if st.session_state.badges:
    st.markdown("### 🏆 Rozetleriniz")
    badge_cols = st.columns(min(len(st.session_state.badges), 4))
    for idx, badge in enumerate(st.session_state.badges):
        with badge_cols[idx % 4]:
            st.markdown(f"""
            <div class="badge">
                {badge['name']}<br>
                <small>{badge['desc']}</small>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# Main decision area
st.markdown("## 🎯 Karar Zamanı")
st.markdown("Fabrika yöneticisi olarak bir karar seçin. AI ajanları gerçekçi sonuçları simüle edecek.")

# Decision selection
decision_col1, decision_col2 = st.columns([2, 1])

with decision_col1:
    selected_decision = st.selectbox(
        "Kararınızı seçin:",
        utils.DECISION_OPTIONS,
        key="decision_select"
    )
    
    if st.button("🚀 Kararı Uygula", type="primary", use_container_width=True):
        with st.spinner("🤖 AI ajanları sonuçları hesaplıyor..."):
            # Step 1: Custom Agent - Simulate decision
            result = agents.simulate_decision(
                selected_decision,
                st.session_state.context,
                model=st.session_state.model
            )
            st.session_state.current_result = result
            
            # Step 2: Classification Agent - Classify risk
            classification = agents.classify_risk(
                selected_decision,
                result,
                model=st.session_state.model
            )
            st.session_state.current_classification = classification
            
            # Update score
            score_change = result.get('score_impact', 0)
            st.session_state.score += score_change
            
            # Save to history
            st.session_state.history.append({
                'decision': selected_decision,
                'result': result,
                'classification': classification,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            
            # Check for new badges
            new_badges = utils.check_badges(st.session_state.history)
            for badge in new_badges:
                if badge not in st.session_state.badges:
                    st.session_state.badges.append(badge)
            
            st.rerun()

with decision_col2:
    st.info("""
    **💡 İpucu**
    
    Her kararın:
    - ✅ Faydaları
    - ⚠️ Riskleri
    - 💰 Maliyeti
    vardır.
    
    Dengeli düşünün!
    """)

# Results display
if st.session_state.current_result:
    st.markdown("---")
    st.markdown("## 📊 Sonuçlar")
    
    result = st.session_state.current_result
    classification = st.session_state.current_classification
    
    # Metrics display
    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    
    with res_col1:
        prod_change = result.get('production_change_percent', 0)
        st.metric(
            "🏭 Üretim Değişimi",
            f"{prod_change:+.1f}%",
            delta=f"{prod_change:+.1f}%",
            delta_color="normal"
        )
    
    with res_col2:
        cost_change = result.get('cost_change_percent', 0)
        st.metric(
            "💵 Maliyet Değişimi",
            f"{cost_change:+.1f}%",
            delta=f"{cost_change:+.1f}%",
            delta_color="inverse"
        )
    
    with res_col3:
        risk_level = result.get('risk_level', 'Orta')
        risk_colors = {"Düşük": "🟢", "Orta": "🟡", "Yüksek": "🔴"}
        st.metric(
            "⚠️ Risk Seviyesi",
            f"{risk_colors.get(risk_level, '🟡')} {risk_level}"
        )
    
    with res_col4:
        score_impact = result.get('score_impact', 0)
        st.metric(
            "🎯 Puan Değişimi",
            f"{score_impact:+d}",
            delta=f"{score_impact:+d}",
            delta_color="normal"
        )
    
    # Classification
    if classification:
        category = classification.get('category', 'Güvenli')
        category_colors = {
            "Optimal": "success",
            "Güvenli": "info",
            "Riskli": "warning",
            "Tehlikeli": "error"
        }
        
        st.markdown(f"### Karar Kategorisi: **{category}**")
        getattr(st, category_colors.get(category, "info"))(
            classification.get('explanation', '')
        )
        
        if classification.get('recommendation'):
            st.info(f"💡 **Öneri:** {classification['recommendation']}")
    
    # Side effects
    side_effects = result.get('side_effects', [])
    if side_effects:
        st.markdown("### ⚙️ Yan Etkiler")
        for effect in side_effects:
            st.markdown(f"- {effect}")
    
    # Risk explanation
    st.markdown("### 📝 Detaylı Açıklama")
    st.write(result.get('risk_explanation', 'Açıklama yok'))

# Summary section
if 'summary' in st.session_state and st.session_state.summary:
    st.markdown("---")
    st.markdown("## 📋 Dönem Özet Raporu")
    st.markdown(st.session_state.summary)
    
    # Download button for summary
    st.download_button(
        label="📥 Raporu İndir",
        data=st.session_state.summary,
        file_name=f"donem_raporu_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )

# History section
if st.session_state.history:
    with st.expander("📜 Karar Geçmişi"):
        for idx, entry in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"""
            **{len(st.session_state.history) - idx + 1}.** {entry['decision']}  
            ⏰ {entry['timestamp']} | 
            📊 Üretim: {entry['result'].get('production_change_percent', 0):+.1f}% | 
            💰 Maliyet: {entry['result'].get('cost_change_percent', 0):+.1f}% | 
            ⚠️ {entry['result'].get('risk_level', 'Orta')} | 
            🎯 {entry['result'].get('score_impact', 0):+d} puan
            """)
            st.markdown("---")