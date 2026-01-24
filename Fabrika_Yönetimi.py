"""
What-If Factory - Fabrika Karar Simülatörü
io.net Hackathon Project
"""
import streamlit as st
import agents
import utils
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

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
    /* Main Container Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 95% !important;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        margin-top: -1rem;
    }
    
    /* TYPOGRAPHY STANDARDIZATION */
    html, body, .stMarkdown, p, li, div.stMarkdown, .stText {
        font-family: 'Inter', sans-serif;
        font-size: 16px !important;
        line-height: 1.6;
        color: #e2e8f0;
    }

    /* Strict Header Hierarchy */
    h1 {
        font-size: 2.5rem !important; 
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
    }
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        margin-bottom: 0.8rem !important;
    }
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.6rem !important;
    }
    h4, h5 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }
    
    /* Premium Dark Gradient Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        text-align: center;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Hover Effect - Subtle Glow */
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 0 15px rgba(59, 130, 246, 0.4);
        border-color: #3b82f6;
    }

    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 0%, rgba(255, 255, 255, 0.03) 50%, transparent 100%);
        pointer-events: none;
    }

    div[data-testid="stMetric"] > label {
        font-size: 1rem !important; /* Fixed to body size */
        font-weight: 500;
        color: #cbd5e1 !important;
        margin-bottom: 0.5rem;
    }
    div[data-testid="stMetric"] > div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #f8fafc !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    /* Expander Styling (Cards) */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border-radius: 6px;
        font-weight: 600;
        font-size: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Button Styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s;
        stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    /* Success/Info Message Compactness */
    .stAlert {
        padding: 0.5rem 1rem !important;
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

# New session states for enhanced features
if 'factory_profile' not in st.session_state:
    st.session_state.factory_profile = utils.generate_factory_profile()
if 'budget' not in st.session_state:
    st.session_state.budget = st.session_state.factory_profile['initial_budget']
if 'satisfaction' not in st.session_state:
    st.session_state.satisfaction = st.session_state.factory_profile['initial_satisfaction']
if 'production_rate' not in st.session_state:
    st.session_state.production_rate = st.session_state.factory_profile['initial_production_rate']
if 'risk_level' not in st.session_state:
    st.session_state.risk_level = st.session_state.factory_profile['initial_risk']
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'game_over_reason' not in st.session_state:
    st.session_state.game_over_reason = ""
if 'previous_budget' not in st.session_state:
    st.session_state.previous_budget = st.session_state.budget
if 'previous_satisfaction' not in st.session_state:
    st.session_state.previous_satisfaction = st.session_state.satisfaction
if 'previous_production_rate' not in st.session_state:
    st.session_state.previous_production_rate = st.session_state.production_rate
if 'previous_risk_level' not in st.session_state:
    st.session_state.previous_risk_level = st.session_state.risk_level

# Turn and event system
# Turn and event system
if 'month_number' not in st.session_state:
    st.session_state.month_number = 1
if 'decisions_this_month' not in st.session_state:
    st.session_state.decisions_this_month = 0
if 'pending_investments' not in st.session_state:
    st.session_state.pending_investments = []  # [{investment_data, activation_month}]
if 'current_event' not in st.session_state:
    st.session_state.current_event = None
if 'event_history' not in st.session_state:
    st.session_state.event_history = []
if 'last_month_expenses' not in st.session_state:
    st.session_state.last_month_expenses = None
if 'machine_count' not in st.session_state:
    # Initial machine count based on profile or default
    # If profile exists, estimate from blue collar
    if 'factory_profile' in st.session_state:
        blue = st.session_state.factory_profile['employee_count']['blue_collar']
        st.session_state.machine_count = int(blue / 4) + 10
    else:
        st.session_state.machine_count = 50

if 'modifiers' not in st.session_state:
    # {revenue_modifier: 1.0, cost_modifier: 1.0}
    st.session_state.modifiers = {"revenue": 1.0, "cost": 1.0}
if 'financial_history' not in st.session_state:
    st.session_state.financial_history = []
if 'resolved_issues_this_month' not in st.session_state:
    st.session_state.resolved_issues_this_month = []
if 'market_condition_timer' not in st.session_state:
    st.session_state.market_condition_timer = 0
if 'problem_cooldown' not in st.session_state:
    st.session_state.problem_cooldown = 0
    
# CLEAR RESOLVED ISSUES LOGIC (Robust)
if st.session_state.get('clear_resolved_next_run', False):
    st.session_state.resolved_issues_this_month = []
    st.session_state.clear_resolved_next_run = False

# Sidebar
with st.sidebar:
    st.markdown("### 🎮 Oyun Menüsü")
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
    
    # Expense Report moved to 'Finansal Raporlar' page
    
    # Reset button
    if st.button("🔄 Yeni Oyun"):
        st.session_state.modifiers = {"revenue": 1.0, "cost": 1.0}
        st.session_state.score = 0
        st.session_state.history = []
        st.session_state.badges = []
        st.session_state.current_result = None
        st.session_state.current_classification = None
        st.session_state.factory_profile = utils.generate_factory_profile()
        st.session_state.budget = st.session_state.factory_profile['initial_budget']
        st.session_state.satisfaction = st.session_state.factory_profile['initial_satisfaction']
        st.session_state.production_rate = st.session_state.factory_profile['initial_production_rate']
        st.session_state.risk_level = st.session_state.factory_profile['initial_risk']
        st.session_state.game_over = False
        st.session_state.game_over_reason = ""
        st.session_state.previous_budget = st.session_state.budget
        st.session_state.previous_satisfaction = st.session_state.satisfaction
        st.session_state.previous_production_rate = st.session_state.production_rate
        st.session_state.previous_risk_level = st.session_state.risk_level
        # Reset turn and event system
        st.session_state.month_number = 1
        st.session_state.market_condition_timer = 0 # NEW: Tracks 3-month market cycle
        st.session_state.problem_cooldown = 0
        st.session_state.resolved_issues_this_month = []
        st.session_state.decisions_this_month = 0
        st.session_state.pending_investments = []
        st.session_state.current_event = None
        st.session_state.current_event = None
        st.session_state.event_history = []
        st.session_state.financial_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ Hakkında")
    st.markdown("""
    **What-If Factory** - Fabrika yöneticileri için oyunlaştırılmış karar simülasyon aracı.
    
    🤖 **io Intelligence** kullanarak gerçekçi sonuçlar üretir.
    
    Made for **io.net Hackathon**
    """)

# HELPER: Check if issue is a market condition (Explicit or Heuristic)
def is_market_condition(issue):
    if not isinstance(issue, dict):
        return False
    
    # 1. Explicit Check
    if issue.get('category') == 'condition':
        return True
        
    # 2. Heuristic Check (for legacy issues)
    condition_keywords = ["Petrol", "Döviz", "Kur", "Enflasyon", "Piyasa", "Sektör", "Vergi", "Yasa", "Kriz", "Savaş", "Ambargo", "Enerji Maliyet", "Faiz", "Hammadde", "Fiyat", "Zam", "İthalat", "İhracat", "Rekabet", "Teknoloji", "Doğal Afet", "Pamuk", "Demir", "Çelik", "Plastik", "Maaş Zammı"]
    title = issue.get('title', '').lower()
    for kw in condition_keywords:
        if kw.lower() in title:
            return True
            
    return False

# HELPER: Smart Fallback System (Ensures stability without 'Backup' label)
def get_smart_fallback(issue_type):
    import random
    if issue_type == 'condition':
        options = [
            {'title': 'Küresel Çip Krizi', 'description': 'Yarı iletken tedariğinde global aksama var.', 'category': 'condition', 'consequence': 'Üretim maliyetleri ciddi oranda artar.', 'ongoing_penalty': {'type': 'budget', 'value': -180000}},
            {'title': 'Liman Grevi', 'description': 'İhracat limanlarında süresiz grev başladı.', 'category': 'condition', 'consequence': 'Lojistik durma noktasında.', 'ongoing_penalty': {'type': 'production', 'value': -10}},
            {'title': 'Yeni Karbon Vergisi', 'description': 'Hükümet sanayi için ağır karbon vergisi getirdi.', 'category': 'condition', 'consequence': 'Vergi yükü katlandı.', 'ongoing_penalty': {'type': 'budget', 'value': -350000}},
            {'title': 'Enerji Fiyatlarında Artış', 'description': 'Global enerji piyasasında %40 zam.', 'category': 'condition', 'consequence': 'Enerji faturaları kabardı.', 'ongoing_penalty': {'type': 'budget', 'value': -250000}},
            {'title': 'Döviz Kuru Şoku', 'description': 'Yerel para birimi sert değer kaybetti.', 'category': 'condition', 'consequence': 'İthal hammadde maliyeti fırladı.', 'ongoing_penalty': {'type': 'budget', 'value': -500000}}
        ]
        return random.choice(options)
    else:
        options = [
            {'title': 'CNC Tezgah Arızası', 'description': 'Ana üretim hattındaki CNC tezgahı motor yaktı.', 'category': 'problem', 'consequence': 'Üretim %15 düştü.', 'ongoing_penalty': {'type': 'production', 'value': -15}, 'resolution_cost': {'budget': 180000, 'resource': 'Bakım Ekibi'}},
            {'title': 'İşçi Sendikası Uyarısı', 'description': 'Sendika maaş iyileştirmesi talep ediyor.', 'category': 'problem', 'consequence': 'Memnuniyet hızla düşüyor.', 'ongoing_penalty': {'type': 'satisfaction', 'value': -8}, 'resolution_cost': {'budget': 120000, 'resource': 'İK Görüşmesi'}},
            {'title': 'Siber Güvenlik Açığı', 'description': 'IT departmanı sunucularda kritik açık tespit etti.', 'category': 'problem', 'consequence': 'Veri kaybı riski çok yüksek.', 'ongoing_penalty': {'type': 'risk', 'value': 25}, 'resolution_cost': {'budget': 250000, 'resource': 'IT Desteği'}},
            {'title': 'Hammadde Kalite Sorunu', 'description': 'Gelen son parti hammadde standart dışı çıktı.', 'category': 'problem', 'consequence': 'İade oranları artıyor.', 'ongoing_penalty': {'type': 'quality', 'value': -20}, 'resolution_cost': {'budget': 300000, 'resource': 'Tedarikçi Değişimi'}},
            {'title': 'Yazılım Lisans Sorunu', 'description': 'Üretim yazılımının lisansı doldu.', 'category': 'problem', 'consequence': 'Sistemler yavaşladı.', 'ongoing_penalty': {'type': 'production', 'value': -8}, 'resolution_cost': {'budget': 80000, 'resource': 'Lisans Yenileme'}}
        ]
        return random.choice(options)

# GAME BALANCE ENFORCER (Run on every render to guarantee rules)
def ensure_game_balance():
    if 'factory_profile' not in st.session_state:
        return

    profile = st.session_state.factory_profile
    if 'active_issues' not in profile:
        profile['active_issues'] = []

    # SEPARATE CONDITIONS AND PROBLEMS
    conditions_list = []
    problems_list = []
    
    current_issues = profile['active_issues']

    for issue in current_issues:
        if is_market_condition(issue):
            conditions_list.append(issue)
        else:
            problems_list.append(issue)
    
    # 1. ENFORCE LIMITS (Remove Excess)
    has_changes = False
    
    # Max 1 Market Condition
    if len(conditions_list) > 1:
        # Keep only the most recent one (last one)
        conditions_list = conditions_list[-1:]
        has_changes = True
    
    # Max 2 Active Problems
    if len(problems_list) > 2:
        # Keep only the recent 2
        problems_list = problems_list[-2:]
        has_changes = True
        
    if has_changes:
        profile['active_issues'] = conditions_list + problems_list
        conditions = len(conditions_list)
        problems = len(problems_list)
    else:
        conditions = len(conditions_list)
        problems = len(problems_list)
    
    # 2. FILL MISSING (Add if needed)
    
    # FIX: Ensure 1 Market Condition
    if conditions == 0:
        with st.spinner("🔄 Piyasa koşulları yapay zekadan çekiliyor..."):
            success = False
            for _ in range(5): # Retry 5 times for AI
                try:
                    evt = agents.generate_random_event(profile, st.session_state.risk_level, st.session_state.month_number, event_type="market_condition")
                    if evt and 'new_issue' in evt:
                        evt['new_issue']['category'] = 'condition'
                        profile['active_issues'].append(evt['new_issue'])
                        st.toast("🌎 Yeni Piyasa Durumu Tespit Edildi!", icon="📢")
                        success = True
                        break
                except Exception as e:
                    print(f"Balance Fix Error (Condition): {e}")

            if not success:
               # Smart Fallback (No label)
               profile['active_issues'].append(get_smart_fallback('condition'))

    # FIX: Ensure 2 Active Problems
    if problems < 2:
        # COOLDOWN CHECK: If a problem was recently solved, don't immediately fill the slot
        if st.session_state.get('problem_cooldown', 0) > 0:
            pass # Skip generation
        else:
            needed = 2 - problems
            with st.spinner(f"🚨 {needed} adet yeni sorun yapay zekadan çekiliyor..."):
                for _ in range(needed):
                    success = False
                    for _ in range(5): # Retry 5 times for AI
                        try:
                            evt = agents.generate_random_event(profile, st.session_state.risk_level, st.session_state.month_number, event_type="problem")
                            if evt and 'new_issue' in evt:
                                evt['new_issue']['category'] = 'problem'
                                profile['active_issues'].append(evt['new_issue'])
                                st.toast("🚨 Yeni Problem Algılandı!", icon="⚠️")
                                success = True
                                break
                        except Exception as e:
                            print(f"Balance Fix Error (Problem): {e}")
                    
                    if not success:
                        # Smart Fallback (No label)
                        profile['active_issues'].append(get_smart_fallback('problem'))

# Run enforcer
ensure_game_balance()

# Main content
st.markdown('<h1 class="main-header">🏭 What-If Factory</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Fabrika Karar Simülatörü - Deneyerek Öğren!</p>', unsafe_allow_html=True)

# Period Summary Modal
if st.session_state.get('show_summary') and st.session_state.get('period_summary'):
    with st.expander("📋 Dönem Raporu ve Özeti (Sizin İçin Hazırlandı)", expanded=True):
        st.markdown(st.session_state.period_summary)
        if st.button("Raporu Kapat"):
            st.session_state.show_summary = False
            st.rerun()
    st.markdown("---")

st.markdown("## 🏢 Fabrika Profili")
profile = st.session_state.factory_profile
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🏭 Sektör:** {profile['sector']}")
with col2:
    st.markdown(f"**👥 Çalışan:** {profile['employee_count']['total']} kişi")
with col3:
    # Quick count for the profile header
    if 'active_issues' not in profile:
        profile['active_issues'] = [profile.get('current_status', 'Bilinmiyor')]
    
    issue_count = len(profile['active_issues'])
    st.markdown(f"**🚨 Sorun Sayısı:** {issue_count}")
    
# --- ACTIVE ISSUES SECTION (Full Width) ---
# Separated from columns to avoid vertical gaps
st.markdown("### 🔦 Durum Analizi")

# Render issues as cards
if not profile['active_issues'] and not st.session_state.resolved_issues_this_month:
    st.success("✅ Tüm sorunlar çözüldü! Fabrika harika durumda.")
else:
    # 1. SHOW RESOLVED ISSUES FIRST (Visual feedback)
    for r_issue in st.session_state.resolved_issues_this_month:
        if isinstance(r_issue, dict):
                with st.expander(f"✅ [ÇÖZÜLDÜ] {r_issue['title']}", expanded=False):
                    st.markdown(f"~~{r_issue['description']}~~")
                    st.success("Bu sorun başarıyla çözüldü.")
        else:
                st.success(f"✅ [ÇÖZÜLDÜ] {r_issue}")

    # 2. SEPARATE ISSUES BY CATEGORY
    market_conditions = []
    actionable_problems = []
    
    for issue in profile['active_issues']:
        if isinstance(issue, dict):
            # Category Detection
            category = issue.get('category', 'problem')
            
            # Heuristic Detection
            condition_keywords = ["Petrol", "Döviz", "Kur", "Enflasyon", "Piyasa", "Sektör", "Vergi", "Yasa", "Kriz", "Savaş", "Ambargo", "Enerji Maliyet", "Faiz", "Hammadde", "Fiyat", "Zam", "İthalat", "İhracat", "Rekabet", "Teknoloji", "Doğal Afet", "Pamuk", "Demir", "Çelik", "Plastik", "Maaş Zammı"]
            if category == 'problem':
                for kw in condition_keywords:
                    if kw.lower() in issue['title'].lower():
                        category = 'condition'
                        break
                        
            if category == 'condition':
                market_conditions.append(issue)
            else:
                actionable_problems.append(issue)

    # Type Mapping for Display
    type_str = {
        'budget': 'TL (Bütçe)',
        'production': '% Üretim Kaybı', 
        'satisfaction': '% Memnuniyet Düşüşü',
        'risk': '% Risk Artışı',
        'quality': '% Kalite Düşüşü',
        'brand': '% Marka Değer Kaybı'
    }

    # 3. RENDER MARKET CONDITIONS (Blue Cards)
    if market_conditions:
        st.markdown("##### 🌎 Piyasa Koşulları")
        for cond in market_conditions:
            with st.expander(f"🔵 {cond['title']}", expanded=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                        st.markdown(f"**Durum:** {cond['description']}")
                        st.caption(f"**⚡ Etki:** {cond['consequence']}")
                with c2:
                    if 'ongoing_penalty' in cond:
                        p = cond['ongoing_penalty']
                        p_val = p.get('value')
                        val_str = f"{p_val:,}" if isinstance(p_val, (int, float)) else p_val
                        st.warning(f"📉 {val_str} {p.get('type','Etki')}")

    # 4. RENDER ACTIONABLE PROBLEMS (Red Cards)
    if actionable_problems:
        st.markdown("##### 🚨 Aksiyon Bekleyen Sorunlar")
        for prob in actionable_problems:
            with st.expander(f"🔴 {prob['title']}", expanded=True):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"{prob['description']}")
                    st.caption(f"**⚠️ Sonuç:** {prob['consequence']}")
                    if 'resolution_hint' in prob:
                            st.caption(f"💡 *İpucu: {prob['resolution_hint']}*")
                
                with c2:
                    # Display Penalty
                    if 'ongoing_penalty' in prob:
                        p = prob['ongoing_penalty']
                        p_val = p.get('value', 0)
                        p_type = p.get('type', 'generic')
                        val_str = f"{p_val:,}" if isinstance(p_val, (int, float)) else p_val
                        
                        if p_type == 'budget':
                                st.error(f"💸 **-{val_str} TL/ay**")
                        else:
                                st.error(f"⚠️ **{val_str} {p_type}**")

                    # Display Resolution Cost
                    if 'resolution_cost' in prob:
                        rc = prob['resolution_cost']
                        cost_txt = f"{rc.get('budget', 0):,} TL"
                        res_txt = rc.get('resource', '')
                        st.info(f"💰 **Çözüm:** {cost_txt}\n\n🛠️ {res_txt}")

st.markdown("---")

# BALANCED SCORECARD [NEW]
st.markdown("### ⚖️ Kurumsal Denge Karnesi")

# Ensure metrics exist
default_metrics = {
    'quality_score': 50, 
    'brand_score': 50, 
    'innovation_score': 50,
    'maintenance_health': 100,
    'maintenance_policy': 1.0
}
for k, v in default_metrics.items():
    if k not in profile:
        profile[k] = v

bal_col1, bal_col2, bal_col3, bal_col4 = st.columns(4)

with bal_col1:
    q_score = profile['quality_score']
    st.metric("💎 Kalite Puanı", f"{q_score}", help="Yüksek kalite = Yüksek fiyat toleransı & Düşük iade.")
    st.progress(q_score/100)

with bal_col2:
    b_score = profile['brand_score']
    st.metric("✨ Marka Değeri", f"{b_score}", help="Yüksek marka = Yüksek satış hacmi.")
    st.progress(b_score/100)

with bal_col3:
    i_score = profile['innovation_score']
    st.metric("🚀 İnovasyon", f"{i_score}", help="Yüksek inovasyon = Düşük hammadde/enerji maliyeti.")
    st.progress(i_score/100)

with bal_col4:
    m_health = profile['maintenance_health']
    m_policy = profile['maintenance_policy']
    st.metric("🔧 Bakım Sağlığı", f"{m_health}", f"Politika: {m_policy}x")
    
    # Progress color logic (visual only)
    st.progress(m_health/100)
    if m_health < 30:
        st.caption("⚠️ **KRİTİK!** Arıza riski çok yüksek.")

st.markdown("---")

# HR & EQUIPMENT DETAIL SECTION
st.markdown("### 👥 İnsan Kaynakları & Ekipman Detayı")

# Ensure breakdown exists
if 'employee_breakdown' not in profile:
    total = profile['employee_count']['total']
    profile['employee_breakdown'] = {
        "blue_collar": profile['employee_count']['blue_collar'],
        "white_collar": profile['employee_count']['white_collar'],
        "engineers": 0,
        "sales": 0,
        "management": 5
    }

hr_col1, hr_col2 = st.columns(2)

# Define breakdown & XP before using it
breakdown = profile['employee_breakdown']
if 'department_xp' not in profile:
    profile['department_xp'] = {
        "blue_collar": 10,
        "white_collar": 10,
        "engineers": 0,
        "sales": 5,
        "management": 20
    }
xp = profile['department_xp']

with hr_col1:
    st.info(f"**🏭 Toplam Makine:** {st.session_state.machine_count}")
    
    # Calculate Ratio (Using only Blue Collar as requested)
    blue_collar = breakdown.get('blue_collar', 1)
    if blue_collar > 0:
        machines_per_worker = st.session_state.machine_count / blue_collar
        worker_per_machine = blue_collar / max(1, st.session_state.machine_count)
        st.write(f"**🔧 Kişi Başına Makine:** {machines_per_worker:.2f}")
        st.caption(f"*(Makine başına {worker_per_machine:.1f} mavi yaka)*")
    else:
        st.write("**🔧 Kişi Başına Makine:** -")
    
    # Utilization (Simple logic)
    utilization = min(100, (profile['employee_breakdown']['blue_collar'] / (max(1, st.session_state.machine_count) * 4)) * 100)
    st.progress(utilization/100, text=f"Makine Kapasite Kullanımı: %{utilization:.0f}")

with hr_col2:
    st.write("**Departman Deneyimi & Dağılımı:**")
    
    dept_labels = {
        "blue_collar": "👷 Mavi Yaka",
        "white_collar": "👨‍💼 Beyaz Yaka",
        "engineers": "🔧 Mühendis",
        "sales": "📢 Satış",
        "management": "👔 Yönetim"
    }
    
    for key, label in dept_labels.items():
        count = breakdown.get(key, 0)
        current_xp = xp.get(key, 0)
        
        # HARDER PROGRESSION: Levels every 20 points
        level = current_xp // 20
        progress = (current_xp % 20) / 20.0
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.write(f"**{label}**")
            st.caption(f"{count} Kişi | Puan: {current_xp}")
        with c2:
            st.progress(progress, text=f"Kademe {level}")

st.markdown("---")

# KPI Dashboard moved to 'Finansal Raporlar' page

# Charts moved to 'Finansal Raporlar' page

# Game Over Check
if st.session_state.game_over:
    st.markdown("## 💀 OYUN BİTTİ")
    st.error(f"### {st.session_state.game_over_reason}")
    st.markdown("### 📊 Final Skorunuz")
    st.markdown(f"**Toplam Puan:** {st.session_state.score}")
    st.markdown(f"**Karar Sayısı:** {len(st.session_state.history)}")
    st.markdown(f"**Rozet Sayısı:** {len(st.session_state.badges)}")
    
    if st.button("🔄 Yeni Oyun Başlat", type="primary"):
        st.session_state.score = 0
        st.session_state.history = []
        st.session_state.badges = []
        st.session_state.current_result = None
        st.session_state.current_classification = None
        st.session_state.factory_profile = utils.generate_factory_profile()
        st.session_state.budget = st.session_state.factory_profile['initial_budget']
        st.session_state.satisfaction = st.session_state.factory_profile['initial_satisfaction']
        st.session_state.production_rate = st.session_state.factory_profile['initial_production_rate']
        st.session_state.risk_level = st.session_state.factory_profile['initial_risk']
        st.session_state.game_over = False
        st.session_state.game_over_reason = ""
        st.session_state.previous_budget = st.session_state.budget
        st.session_state.previous_satisfaction = st.session_state.satisfaction
        st.session_state.previous_production_rate = st.session_state.production_rate
        st.session_state.previous_risk_level = st.session_state.risk_level
        st.rerun()
else:
    # Event Display - Show current event before decision making
    if st.session_state.current_event and not st.session_state.current_event.get('resolved', False):
        event = st.session_state.current_event
        st.error(f"### 🚨 {event['event_name']}\n\n{event['event_description']}")
        
        # Show expected impacts
        st.markdown("**Beklenen Etkiler:**")
        impacts = event.get('event_impacts', {})
        impact_cols = st.columns(4)
        with impact_cols[0]:
            budget_impact = impacts.get('budget', 0)
            st.metric("Bütçe", f"{budget_impact:+,} TL")
        with impact_cols[1]:
            prod_impact = impacts.get('production_rate', 0)
            st.metric("Üretim", f"{prod_impact:+}%")
        with impact_cols[2]:
            sat_impact = impacts.get('satisfaction', 0)
            st.metric("Memnuniyet", f"{sat_impact:+}%")
        with impact_cols[3]:
            risk_impact = impacts.get('risk', 0)
            st.metric("Risk", f"{risk_impact:+}%")
        
        st.markdown("---")
        
        # Check if player can respond
        if event.get('player_can_respond', False):
            st.markdown("**💡 Bu event'e nasıl yanıt vermek istersiniz?**")
            response_options = event.get('response_options', [])
            
            response_cols = st.columns(len(response_options))
            for i, option in enumerate(response_options):
                with response_cols[i]:
                    if st.button(option, key=f"event_response_{i}", use_container_width=True):
                        # Apply mitigated impacts (50% reduction for taking action)
                        st.session_state.budget += impacts.get('budget', 0) * 0.5
                        st.session_state.production_rate = max(0, min(150, st.session_state.production_rate + impacts.get('production_rate', 0) * 0.5))
                        st.session_state.satisfaction = max(0, min(100, st.session_state.satisfaction + impacts.get('satisfaction', 0) * 0.5))
                        st.session_state.risk_level = min(100, st.session_state.risk_level + impacts.get('risk', 0) * 0.5)
                        
                        # Mark as resolved
                        st.session_state.current_event['resolved'] = True
                        st.session_state.event_history.append({
                            'month': st.session_state.month_number,
                            'event': event,
                            'response': option
                        })
                        st.success(f"✅ Event'e yanıt verildi: {option}")
                        st.rerun()
        else:
            # Event cannot be responded to - forced accept
            st.warning("⚠️ **Bu event'e müdahale edilemiyor. Etkileri kabul etmelisiniz.**")
            if st.button("Kabul Et ve Devam", type="primary"):
                # Apply full negative impacts
                st.session_state.budget += impacts.get('budget', 0)
                st.session_state.production_rate = max(0, min(150, st.session_state.production_rate + impacts.get('production_rate', 0)))
                st.session_state.satisfaction = max(0, min(100, st.session_state.satisfaction + impacts.get('satisfaction', 0)))
                st.session_state.risk_level = min(100, st.session_state.risk_level + impacts.get('risk', 0))
                
                # Mark as resolved
                st.session_state.current_event['resolved'] = True
                st.session_state.event_history.append({
                    'month': st.session_state.month_number,
                    'event': event,
                    'response': 'Forced Accept'
                })
                st.rerun()
        
        st.markdown("---")
        st.info("ℹ️ Event'i çözdükten sonra karar alabilirsiniz.")
    else:
        # No active event - show pending investments info
        if st.session_state.pending_investments:
            st.info(f"⏳ **Bekleyen Yatırımlar**: {len(st.session_state.pending_investments)} adet yatırım tamamlanmayı bekliyor...")
    
    # Main decision area
    st.markdown("## 🎯 Karar Zamanı")
    
    # Calculate Decision Limit
    total_employees = st.session_state.factory_profile['employee_count']['total']
    # Rule: 1 decision per 100 employees, min 3, max 8
    max_decisions = max(3, min(8, total_employees // 100))
    remaining_decisions = max_decisions - st.session_state.decisions_this_month
    
    # Display Limit Info
    limit_col1, limit_col2 = st.columns([3, 1])
    with limit_col1:
        st.markdown("Fabrika yöneticisi olarak kararınızı yazın. AI ajanları gerçekçi sonuçları simüle edecek.")
    with limit_col2:
        st.metric("Kalan Karar Hakkı", f"{remaining_decisions}/{max_decisions}")
        st.progress(remaining_decisions / max_decisions)

    # Decision selection
    decision_col1, decision_col2 = st.columns([2, 1])

    with decision_col1:
        decision_input = st.text_area(
            "Kararınızı yazın:",
            placeholder="Örn: Vardiya sayısını 2'den 3'e çıkar, Makine bakım bütçesini %20 artır, 50 yeni çalışan işe al...",
            height=100,
            key="decision_input",
            disabled=(remaining_decisions <= 0)
        )
        
        # Quick Action Buttons
        st.markdown("### ⚡ Hızlı Aksiyonlar")
        quick_col1, quick_col2, quick_col3, quick_col4, = st.columns(4)
        
        # Get dynamic actions based on current state
        quick_actions = utils.get_dynamic_quick_actions(
            st.session_state.budget,
            st.session_state.satisfaction,
            st.session_state.risk_level,
            st.session_state.production_rate
        )
        
        quick_buttons = []
        with quick_col1:
            if st.button(quick_actions[0][0], key="quick1", disabled=(remaining_decisions <= 0)):
                quick_buttons.append(quick_actions[0][1])
        with quick_col2:
            if st.button(quick_actions[1][0], key="quick2", disabled=(remaining_decisions <= 0)):
                quick_buttons.append(quick_actions[1][1])
        with quick_col3:
            if st.button(quick_actions[2][0], key="quick3", disabled=(remaining_decisions <= 0)):
                quick_buttons.append(quick_actions[2][1])
        with quick_col4:
            if st.button(quick_actions[3][0], key="quick4", disabled=(remaining_decisions <= 0)):
                quick_buttons.append(quick_actions[3][1])
        
        # Use quick action if selected
        final_decision = decision_input
        if quick_buttons:
            final_decision = quick_buttons[0]  # Use the first clicked quick action
        
        # Action Buttons Row
        action_col1, action_col2 = st.columns([1, 1])
        
        with action_col1:
            apply_clicked = st.button(
                "🚀 Kararı Uygula", 
                type="primary", 
                use_container_width=True,
                disabled=(remaining_decisions <= 0)
            )
        
        with action_col2:
            end_month_clicked = st.button(
                "📅 Ayı Bitir ve İlerle",
                type="secondary",
                use_container_width=True,
                help="Kalan karar haklarını kullanmadan bir sonraki aya geçer."
            )

        if end_month_clicked:
            # Advance Month Logic
            st.session_state.month_number += 1
            st.session_state.decisions_this_month = 0
            st.session_state.resolved_issues_this_month = [] # Clear resolved issues for new month
            
            # Decrement Cooldown
            if st.session_state.get('problem_cooldown', 0) > 0:
                st.session_state.problem_cooldown -= 1
            
            # MONTHLY COST & REVENUE CALCULATION
            total_employees = st.session_state.factory_profile['employee_count']['total']
            
            # Ensure machine_count is in session state
            if 'machine_count' not in st.session_state:
                 blue_collar = st.session_state.factory_profile['employee_count']['blue_collar']
                 st.session_state.machine_count = int(blue_collar / 4) + 10
                 
            machine_count = st.session_state.machine_count
            current_production = st.session_state.production_rate
            risk = st.session_state.risk_level
            satisfaction = st.session_state.satisfaction
            sector = st.session_state.factory_profile.get('sector', 'Genel Üretim')
            
            # --- REALISTIC FINANCIAL FORMULAS ---
            
            # SECTOR SPECIFIC MULTIPLIERS
            # Format: {Sector: (COGS_Rate, Energy_Base, Rev_Base)}
            # COGS_Rate: % of Revenue that goes to Raw Materials (0.30 - 0.60)
            # Energy_Base: Usage per active machine
            # Rev_Base: Revenue per machine capacity
            
            sector_financials = {
                "Otomotiv Yan Sanayi": (0.50, 15000, 400000), # High material, High energy, High Revenue
                "Gıda": (0.45, 12000, 300000),              # High material (perishables), Medium Energy
                "Tekstil": (0.35, 8000, 250000),            # Medium material, Low Energy (labor intensive)
                "Kimya": (0.40, 18000, 350000),             # Medium material, High Energy
                "Elektronik": (0.40, 10000, 450000),        # Medium material (chips), Low Energy, High Revenue
                "Genel Üretim": (0.40, 10000, 300000)       # Average defaults
            }
            
            # Get multipliers with fallback
            cogs_rate, energy_base, base_rev_per_machine = sector_financials.get(
                sector, sector_financials["Genel Üretim"]
            )
            
            # 1. ABSENTEEISM
            absenteeism_rate = max(0, (100 - satisfaction) / 2 + (risk / 10))
            active_workforce_ratio = (100 - absenteeism_rate) / 100
            
            # 2. EFFECTIVE PRODUCTION (Constraint Logic)
            blue_collar = st.session_state.factory_profile['employee_count']['blue_collar']
            available_workers = blue_collar * active_workforce_ratio
            
            # 1 Machine needs ~4 workers
            max_operable_machines = int(available_workers / 4)
            active_machines = min(machine_count, max_operable_machines)
            
            # --- REVENUE CALCULATION FIRST (Needed for COGS) ---
            revenue_mod = st.session_state.modifiers['revenue']
            
            # Revenue = Active Machines * SectorBase * ProdRate * Modifiers
            # Production Rate affects VOLUME sold
            # total_revenue = (active_machines * base_rev_per_machine * (current_production / 100)) * revenue_mod
            
            # --- EXPENSES ---
            cost_mod = st.session_state.modifiers['cost']
            # FINANCIAL FORMULAS (BALANCED) [NEW]
            q = st.session_state.factory_profile.get('quality_score', 50)
            b = st.session_state.factory_profile.get('brand_score', 50)
            i = st.session_state.factory_profile.get('innovation_score', 50)
            
            # Calculate actual production volume based on active machines and production rate
            # Assuming base_rev_per_machine represents the max revenue capacity per machine
            # and current_production / 100 is the utilization rate.
            # Let's define a 'product_price' and 'actual_production' for clarity,
            # or adapt the existing base_rev_per_machine to be 'max_revenue_per_machine_at_100_prod_rate'
            # For now, let's assume base_rev_per_machine * (current_production / 100) is 'revenue_per_active_machine'
            
            # Let's assume 'product_price' is implicitly included in 'base_rev_per_machine'
            # and 'actual_production' is proportional to 'active_machines * (current_production / 100)'
            
            # To align with the new formula structure, we need a 'product_price' and 'actual_production'
            # Let's derive them from existing variables for consistency.
            # If base_rev_per_machine is total revenue at 100% production for ONE machine,
            # then actual_production could be active_machines * (current_production / 100) units
            # and product_price could be base_rev_per_machine / (some_unit_count)
            # For simplicity, let's assume 'base_rev_per_machine' is 'product_price * units_per_machine_at_100_prod'
            # And 'actual_production' is 'active_machines * (current_production / 100)'
            
            # Let's define a conceptual 'unit_production_capacity' for a machine
            # and a 'unit_price' to make the formula work.
            # For now, let's use a simplified approach where:
            # actual_production_volume = active_machines * (current_production / 100) * (some_base_units_per_machine)
            # product_price = base_rev_per_machine / (some_base_units_per_machine)
            # This means (actual_production_volume * product_price) = active_machines * (current_production / 100) * base_rev_per_machine
            
            # So, the original `total_revenue` calculation already represents `actual_production * product_price`
            # Let's rename it for clarity in the new formula.
            base_production_revenue = (active_machines * base_rev_per_machine * (current_production / 100)) * revenue_mod
            
            # REVENUE: Impacted by Brand
            brand_mult = 0.8 + (b / 250) # 0.8x to 1.2x multiplier
            total_revenue = base_production_revenue * brand_mult
            
            # Refunds (Quality Penalty)
            refund_cost = 0
            if q < 40:
                refund_cost = (40 - q) * 2000 * cost_mod # Apply cost_mod to refund cost
                total_revenue = max(0, total_revenue - refund_cost)

            # CRISIS IMPACT (Active Issues Penalty) [NEW]
            active_issues_count = len(st.session_state.factory_profile.get('active_issues', []))
            crisis_revenue_hit = 0
            crisis_cost_add = 0
            
            if active_issues_count > 0:
                # 8% Revenue hit per issue (Disruption)
                crisis_penalty_rate = 0.08 * active_issues_count
                crisis_revenue_hit = total_revenue * crisis_penalty_rate
                total_revenue = max(0, total_revenue - crisis_revenue_hit)
                
                # 5% Extra cost per issue (Emergency fixes)
                crisis_cost_add = (total_revenue * 0.05 * active_issues_count)
                
                st.error(f"⚠️ Kriz Etkisi ({active_issues_count} Sorun): -{crisis_revenue_hit:,.0f} TL Gelir Kaybı / +{crisis_cost_add:,.0f} TL Ekstra Maliyet")

            # 1. COGS: Impacted by Innovation (Save) & Quality (Waste)
            innovation_discount = (i / 500) # Max 20% discount (0 to 0.2)
            waste_penalty = (100 - q) / 400 # Max 25% penalty (0 to 0.25)
            
            cogs_multiplier = (1.0 - innovation_discount + waste_penalty)
            # Ensure cogs_multiplier doesn't go too low or too high
            cogs_multiplier = max(0.5, min(1.5, cogs_multiplier)) # Example bounds
            
            # COGS base is % of Revenue + Crisis Cost
            raw_material_cost = ((total_revenue + crisis_revenue_hit) * cogs_rate) * cogs_multiplier * cost_mod
            raw_material_cost += crisis_cost_add
            
            # 2. LABOR: Dynamic based on XP and Role [NEW]
            base_salaries = {
                "blue_collar": 25000,
                "white_collar": 35000,
                "engineers": 45000,
                "sales": 30000,
                "management": 60000
            }
            
            labor_cost = 0
            breakdown = st.session_state.factory_profile.get('employee_breakdown', {})
            xp_levels = st.session_state.factory_profile.get('department_xp', {})
            
            # Fallback if breakdown empty (shouldn't happen due to init)
            if not breakdown:
                 labor_cost = (total_employees * 25000) * cost_mod
            else:
                for role, count in breakdown.items():
                    base = base_salaries.get(role, 25000)
                    xp = xp_levels.get(role, 0)
                    # Salary Multiplier: +0.5% per XP point
                    # 100 XP -> 1.5x salary
                    multiplier = 1 + (xp * 0.005)
                    labor_cost += (count * base * multiplier)
            
            labor_cost *= cost_mod
            
            # 3. MAINTENANCE: Physics & Policy Based [NEW]
            m_health = st.session_state.factory_profile.get('maintenance_health', 100)
            m_policy = st.session_state.factory_profile.get('maintenance_policy', 1.0)
            
            # Decay Logic
            decay = 5 # Natural decay
            if current_production > 110:
                decay += 5 # Overwork penalty
            
            # Repair Logic
            repair = 5 * m_policy
            
            # Apply Change
            new_health = max(0, min(100, m_health - decay + repair))
            st.session_state.factory_profile['maintenance_health'] = new_health
            
            # Cost Logic
            # 2000 TL per machine per month (Standard) * Policy
            maintenance_cost = (active_machines * 2000 * m_policy) * cost_mod
            
            # Critical Failure Check
            if new_health < 20:
                 st.error(f"🚨 KRİTİK ARIZA: Bakım Sağlığı %{new_health} seviyesine düştü!")
                 # Trigger severe breakdown issue
                 breakdown_issue = {
                     "title": "Kritik Makine Arızası",
                     "description": "Bakımsızlık nedeniyle ana üretim hattı çöktü.",
                     "consequence": "Her ay ciddi üretim kaybı.",
                     "impact": {"production": -30, "cost": 50000}
                 }
                 if 'active_issues' not in st.session_state.factory_profile:
                      st.session_state.factory_profile['active_issues'] = []
                 # Check if issue already exists to avoid duplicates
                 issue_titles = [issue['title'] for issue in st.session_state.factory_profile['active_issues'] if isinstance(issue, dict)]
                 if breakdown_issue['title'] not in issue_titles:
                      st.session_state.factory_profile['active_issues'].append(breakdown_issue)
            
            # 4. ENERGY: Sector specific base * Active Machines
            energy_cost = (active_machines * energy_base * (current_production / 100)) * cost_mod
            
            # 5. OVERHEAD: Fixed per employee (Software, insurance, meals)
            overhead_cost = (total_employees * 3000) * cost_mod
            
            # 6. RENT: Linked to space (Employees + Machines) [NEW]
            # Approx 10sqm per employee/machine unit at 200TL/sqm
            # 400 employees -> 800k-1M Rent
            params = (total_employees + (machine_count * 2)) 
            rent_cost = 100000 + (params * 2000)
            
            total_monthly_expenses = labor_cost + energy_cost + overhead_cost + rent_cost + maintenance_cost + raw_material_cost
            
            # Net Profit
            net_profit = total_revenue - total_monthly_expenses
            
            # Update Budget
            st.session_state.budget += net_profit
            
            # Store for report
            st.session_state.last_month_expenses = {
                "revenue": total_revenue,
                "raw_material": raw_material_cost, # NEW
                "labor": labor_cost,
                "energy": energy_cost,
                "maintenance": maintenance_cost,
                "overhead": overhead_cost,
                "rent": rent_cost,
                "total_expenses": total_monthly_expenses,
                "net_profit": net_profit,
                "absenteeism": absenteeism_rate, 
                "active_machines": active_machines
            }
            
            # Add to history
            st.session_state.financial_history.append({
                "Ay": st.session_state.month_number, 
                "Gelir": total_revenue,
                "Hammadde": raw_material_cost, # NEW
                "Personel": labor_cost,
                "Enerji": energy_cost,
                "Bakım": maintenance_cost,
                "Genel": overhead_cost,
                "Kira": rent_cost,
                "Toplam Gider": total_monthly_expenses,
                "Net Kâr": net_profit
            })
            
            if net_profit > 0:
                st.toast(f"💰 Net Kâr: +{net_profit:,.0f} TL", icon="📈")
            
            # Trigger Rerun to show new month
            # TRIGGER RECURRING GAME MECHANICS (Market Cycle & Issue Replenishment)
            st.session_state.market_condition_timer += 1
            
            # 1. Market Cycle (Every 3 Months) -> Rotate 'condition' issues
            if st.session_state.market_condition_timer >= 3:
                # Remove old market conditions
                st.session_state.factory_profile['active_issues'] = [
                    i for i in st.session_state.factory_profile['active_issues'] 
                    if not is_market_condition(i)
                ]
                
                # Generate ONE new market condition
                # We reuse generate_random_event but will force it to be a Condition in prompts or post-processing?
                # Ideally we rely on the prompt instructing "New Issues"
                # For now, let's inject a specialized prompt call or rely on standard event gen but filter for condition.
                # Simplification: We will just call standard generator and hope?
                # BETTER: Explicitly ask agent for a "Market Condition" event.
                try:
                    # Quick hack: Generate event and force category 'condition' if it's an issue
                    market_event = agents.generate_random_event(st.session_state.factory_profile, st.session_state.risk_level, event_type="market_condition")
                    if 'new_issue' in market_event and market_event['new_issue']:
                        market_event['new_issue']['category'] = 'condition'
                        st.session_state.factory_profile['active_issues'].append(market_event['new_issue'])
                        st.toast(f"🌎 Yeni Piyasa Durumu: {market_event['new_issue']['title']}", icon="📢")
                except Exception as e:
                    print(f"Market Event Error: {e}")
                
                st.session_state.market_condition_timer = 0

            # 2. Problem Replenishment (Always 2 Active Problems)
            active_problems = [i for i in st.session_state.factory_profile['active_issues'] if isinstance(i, dict) and i.get('category', 'problem') == 'problem']
            missing_problems = 2 - len(active_problems)
            
            if missing_problems > 0:
                for _ in range(missing_problems):
                    try:
                        new_prob = agents.generate_random_event(st.session_state.factory_profile, st.session_state.risk_level, event_type="problem")
                        if 'new_issue' in new_prob and new_prob['new_issue']:
                            new_prob['new_issue']['category'] = 'problem'
                            st.session_state.factory_profile['active_issues'].append(new_prob['new_issue'])
                            st.toast(f"🚨 Yeni Sorun Belirdi: {new_prob['new_issue']['title']}", icon="💥")
                    except Exception as e:
                        print(f"Problem Gen Error: {e}")

            # 3. ESCALATION & PENALTY APPLICATION
            if 'active_issues' in st.session_state.factory_profile:
                total_penalty_budget = 0
                for issue in st.session_state.factory_profile['active_issues']:
                    if isinstance(issue, dict):
                        # ESCALATION (If problem, increase penalty)
                        if issue.get('category', 'problem') == 'problem':
                             # Increase penalty by ~10%
                             if 'ongoing_penalty' in issue:
                                 val = issue['ongoing_penalty'].get('value', 0)
                                 # Penalties are often negative numbers, so multiply by 1.1 makes them more negative (bigger penalty)
                                 # Or if positive value meant something else... assume usually negative for budget/prod
                                 # If budget penalty is -10000 -> -11000
                                 new_val = int(val * 1.1)
                                 if val == new_val: # Avoid stagnation if low number
                                     new_val += (-10 if val < 0 else 10)
                                 issue['ongoing_penalty']['value'] = new_val
                        
                        # Support both old 'penalty' and new 'ongoing_penalty' keys
                        p = issue.get('ongoing_penalty') or issue.get('penalty')
                        
                        if p:
                            p_val = p.get('value', 0)
                            p_type = p.get('type')
                            
                            if p_type == 'production':
                                st.session_state.production_rate = max(0, st.session_state.production_rate + p_val)
                                st.toast(f"📉 {issue['title']} Cezası: Üretim {p_val}%", icon="⚠️")
                            elif p_type == 'budget':
                                st.session_state.budget += p_val
                                total_penalty_budget += p_val
                                st.toast(f"💸 {issue['title']} Cezası: {p_val:,} TL", icon="📉")
                            elif p_type == 'satisfaction':
                                st.session_state.satisfaction = max(0, st.session_state.satisfaction + p_val)
                                st.toast(f"😡 {issue['title']} Cezası: Memnuniyet {p_val}", icon="📉")
                            elif p_type == 'risk':
                                st.session_state.risk_level = min(100, st.session_state.risk_level + p_val)
                                st.toast(f"⚠️ {issue['title']} Cezası: Risk +%{p_val}", icon="🔺")
                            elif p_type == 'brand':
                                current_score = st.session_state.factory_profile.get('brand_score', 50)
                                st.session_state.factory_profile['brand_score'] = max(0, current_score + p_val)
                                st.toast(f"📉 {issue['title']} Cezası: Marka {p_val}", icon="✨")
                            elif p_type == 'quality':
                                current_score = st.session_state.factory_profile.get('quality_score', 50)
                                st.session_state.factory_profile['quality_score'] = max(0, current_score + p_val)
                                st.toast(f"📉 {issue['title']} Cezası: Kalite {p_val}", icon="💎")
                            elif p_type == 'innovation':
                                current_score = st.session_state.factory_profile.get('innovation_score', 50)
                                st.session_state.factory_profile['innovation_score'] = max(0, current_score + p_val)
                                st.toast(f"📉 {issue['title']} Cezası: İnovasyon {p_val}", icon="🚀")
                
                if total_penalty_budget < 0:
                     st.error(f"⚠️ Aktif sorunlar bu ay toplam {total_penalty_budget:,} TL zarara yol açtı!")

            # GENERATE PERIOD SUMMARY
            try:
                # Get recent history (decisions made this month)
                # Filter history where 'month' matches current (or just last N items)
                # But since we clear vars, let's just send the last few items
                recent_history = st.session_state.history[-st.session_state.decisions_this_month:] if st.session_state.decisions_this_month > 0 else []
                
                if recent_history:
                    with st.spinner("📋 Dönem raporu hazırlanıyor..."):
                        summary_text = agents.generate_summary(recent_history, model=model_choice)
                        st.session_state.period_summary = summary_text
                        st.session_state.show_summary = True
            except Exception as e:
                print(f"Summary Error: {e}")
            
            st.rerun()
            
            # GENERATE MONTHLY EVENT (Guaranteed)
            with st.spinner("🤖 Gelecek ayın senaryosu simüle ediliyor..."):
                # Handle active_issues for event generator
                if 'active_issues' not in st.session_state.factory_profile:
                     st.session_state.factory_profile['active_issues'] = [st.session_state.factory_profile.get('current_status', '')]
                
                event_data = agents.generate_random_event(
                     st.session_state.factory_profile,
                     st.session_state.risk_level,
                     st.session_state.month_number,
                     model=model_choice
                )
                
                # Check for NEW ISSUES caused by event
                new_issue = event_data.get('new_issue')
                # If it's a dict (new format), check title for uniqueness
                # If it's a string (old format fallback), check string
                
                if new_issue:
                    current_titles = []
                    for existing in st.session_state.factory_profile['active_issues']:
                        if isinstance(existing, dict):
                            current_titles.append(existing['title'])
                        else:
                            current_titles.append(str(existing))
                    
                    new_title = new_issue['title'] if isinstance(new_issue, dict) else str(new_issue)
                    
                    if new_title not in current_titles:
                        st.session_state.factory_profile['active_issues'].append(new_issue)
                        st.toast(f"⚠️ Yeni Sorun Çıktı: {new_title}", icon="🚨")
                
                # Apply Event Modifiers
                new_rev_mod = event_data.get('revenue_modifier_impact', 1.0)
                new_cost_mod = event_data.get('cost_modifier_impact', 1.0)
                
                # Decay old modifiers (Effect fades over time, moving 50% closer to 1.0)
                current_rev = st.session_state.modifiers['revenue']
                current_cost = st.session_state.modifiers['cost']
                
                st.session_state.modifiers['revenue'] = 1.0 + ((current_rev - 1.0) * 0.5)
                st.session_state.modifiers['cost'] = 1.0 + ((current_cost - 1.0) * 0.5)
                
                # Apply NEW modifiers (Multiplicative or additive? Let's replace or multiply. 
                # For simplicity, if event has impact, it OVERRIDES. If 1.0, it keeps decayed old value? 
                # Let's multiply to chain effects).
                if new_rev_mod != 1.0:
                    st.session_state.modifiers['revenue'] *= new_rev_mod
                if new_cost_mod != 1.0:
                    st.session_state.modifiers['cost'] *= new_cost_mod
                
                st.session_state.current_event = event_data
                st.session_state.event_history.append({"month": st.session_state.month_number, "event": event_data})
                
            
            # PENDING INVESTMENTS ACTIVATION: Monthly Tracking (Reverted)
            activated_investments = []
            for investment in st.session_state.pending_investments:
                if investment.get('activation_month', 0) <= st.session_state.month_number:
                    # Apply delayed effects
                    st.session_state.production_rate = max(0, min(150, st.session_state.production_rate + investment.get('delayed_production_impact', 0)))
                    st.session_state.budget += investment.get('delayed_budget_impact', 0)
                    st.session_state.satisfaction = max(0, min(100, st.session_state.satisfaction + investment.get('delayed_satisfaction_impact', 0)))
                    
                    activated_investments.append(investment)
                    st.success(f"✅ **Yatırım tamamlandı!** {investment['description']}")
            
            # Remove activated investments
            for investment in activated_investments:
                st.session_state.pending_investments.remove(investment)

            # GENERATE NEW EVENT for next month (AI-generated)
            try:
                # Event Probability Logic
                import random
                roll = random.random()
                if roll < 0.30:
                    sentiment = "Positive" # 30% Good
                elif roll < 0.70:
                    sentiment = "Negative" # 40% Bad (0.30 to 0.70)
                else:
                    sentiment = "Neutral"  # 30% Neutral/Mixed
                
                print(f"Generating event with sentiment: {sentiment}")
                
                new_event = agents.generate_random_event(
                    st.session_state.factory_profile,
                    st.session_state.risk_level,
                    st.session_state.month_number,  # Current month
                    model=st.session_state.model,
                    sentiment=sentiment
                )
                if new_event:
                    st.session_state.current_event = new_event
                    st.session_state.current_event['resolved'] = False
            except Exception as e:
                print(f"Event generation error: {e}")
            
            # Trigger Rerun to show new month
            st.session_state.clear_resolved_next_run = True # Ensure clearing happens on next render
            st.rerun()


        if apply_clicked or quick_buttons:
            if not final_decision or final_decision.strip() == "":
                st.error("Lütfen bir karar yazın veya hızlı aksiyon seçin!")
            else:
                with st.spinner("🤖 AI ajanları sonuçları hesaplıyor..."):
                    # Step 1: Custom Agent - Simulate decision
                    # Pass active_issues to context for agent
                    profile_with_issues = st.session_state.factory_profile.copy()
                    if 'active_issues' not in profile_with_issues:
                         profile_with_issues['active_issues'] = [profile_with_issues.get('current_status', '')]
                    
                    # QUARTERLY EVENT LOGIC [NEW]
                    decision_context = st.session_state.context
                    if st.session_state.month_number % 3 == 0:
                        decision_context += "\n\n[SYSTEM ALERT]: This is month " + str(st.session_state.month_number) + ". It is a QUARTERLY EVENT MONTH. You MUST trigger a Major Strategic Event (Crisis or Opportunity) in active_issues or results according to Rule 14. Make it impactful."
                        st.toast(f"📅 {st.session_state.month_number}. Ay: Çeyrek Dönem Olayı Tetikleniyor!", icon="⚡")
                          
                    result = agents.simulate_decision(
                        final_decision,
                        decision_context,
                        profile_with_issues,
                        model=st.session_state.model
                    )
                    st.session_state.current_result = result
                    
                    # --- RESEARCH REPORT DISPLAY [NEW] ---
                    # If this is a research action, show the report clearly
                    research_data = result.get('research_analysis')
                    if research_data:
                        # Append to history for specialized display or handling
                        # (Optional: specialized toast or alert)
                        st.toast("🕵️ Araştırma tamamlandı!", icon="📊")
                    # -------------------------------------
                    
                # Step 2: Classification Agent - Classify risk
                    classification = agents.classify_risk(
                        final_decision,
                        result,
                        model=st.session_state.model
                    )
                    st.session_state.current_classification = classification
                    
                    """
                    # DETERMINISTIC MULTI-ACTION BLOCKER [DISABLED]
                    # Reason: Caused issues with complex events where AI returned multiple logic updates.
                    # We rely on prompts.py logic rules instead.
                    
                    if 'resource_updates' in result:
                        active_changes = [k for k, v in result['resource_updates'].items() if v != 0]
                        # Block if more than 1 distinct resource type is modified (e.g. Machines AND Workers)
                        if len(active_changes) > 1:
                            pass 
                            # result['is_allowed'] = False
                            # formatted_changes = [c.replace('_', ' ').title() for c in active_changes]
                            # result['refusal_reason'] = f"Aynı anda birden fazla kaynağı ({', '.join(formatted_changes)}) değiştiremezsiniz. Lütfen odaklanın ve sırayla yapın."
                    """

                    # CHECK IF ALLOWED
                    if not result.get('is_allowed', True):
                        # DECISION BLOCKED
                        st.error(f"🚫 **Karar Uygulanamadı:** {result.get('refusal_reason', 'Bilinmeyen sebep')}")
                        
                        missing = result.get('missing_requirements', [])
                        if missing:
                            st.warning("**⚠️ Eksik Gereksinimler:**")
                            for req in missing:
                                st.markdown(f"- {req}")
                        
                        # Stop processing, do not update KPIs
                        st.session_state.current_result = None # Hide result view
                        st.stop() # Stop execution here
                    
                    # Update KPIs (Only if allowed)
                    st.session_state.previous_budget = st.session_state.budget
                    st.session_state.previous_satisfaction = st.session_state.satisfaction
                    st.session_state.previous_production_rate = st.session_state.production_rate
                    st.session_state.previous_risk_level = st.session_state.risk_level
                    
                    st.session_state.budget += result.get('budget_impact', 0)
                    st.session_state.satisfaction = max(0, min(100, st.session_state.satisfaction + result.get('satisfaction_impact', 0)))
                    st.session_state.production_rate = max(0, min(150, st.session_state.production_rate + result.get('production_rate_impact', 0)))
                    
                    # Update risk level based on decision
                    risk_mapping = {"Düşük": 20, "Orta": 50, "Yüksek": 80}
                    base_risk = risk_mapping.get(result.get('risk_level', 'Orta'), 50)
                    st.session_state.risk_level = min(100, base_risk + (len(st.session_state.history) * 2))  # Risk accumulates
                    
                    # Update score
                    score_change = result.get('score_impact', 0)
                    st.session_state.score += score_change
                    
                    # RESOURCE UPDATES
                    if 'resource_updates' in result:
                        updates = result['resource_updates']
                        for res_key, res_val in updates.items():
                            if res_key == 'machines':
                                st.session_state.machine_count = max(0, st.session_state.machine_count + res_val)
                                st.toast(f"⚙️ Makine Sayısı: {res_val:+}", icon="🏭")
                            
                            elif res_key in st.session_state.factory_profile.get('employee_breakdown', {}):
                                # Update specific department
                                current_val = st.session_state.factory_profile['employee_breakdown'][res_key]
                                st.session_state.factory_profile['employee_breakdown'][res_key] = max(0, current_val + res_val)
                                st.toast(f"👥 {res_key.title()}: {res_val:+}", icon="👤")
                        
                        # Sync Total Employees
                        breakdown = st.session_state.factory_profile['employee_breakdown']
                        new_total = sum(breakdown.values())
                        st.session_state.factory_profile['employee_count']['total'] = new_total
                        
                        # Update other aggregates
                        st.session_state.factory_profile['employee_count']['blue_collar'] = breakdown['blue_collar']
                        st.session_state.factory_profile['employee_count']['white_collar'] = breakdown['white_collar']

                    # XP GAINS [Independent Block]
                    if 'xp_gains' in result:
                        # Init XP if missing
                        if 'department_xp' not in st.session_state.factory_profile:
                                st.session_state.factory_profile['department_xp'] = {}
                                
                        for dept, gain in result['xp_gains'].items():
                            current_xp = st.session_state.factory_profile['department_xp'].get(dept, 0)
                            new_xp = min(100, current_xp + gain)
                            st.session_state.factory_profile['department_xp'][dept] = new_xp
                            st.toast(f"🏅 {dept.title()} Yetkinliği: {gain:+} (Kademe {new_xp//20})", icon="📈")

                    # METRICS UPDATES [Independent Block]
                    if 'metrics_updates' in result:
                         # Init metrics if missing
                        for m_key in ['quality_score', 'brand_score', 'innovation_score']:
                            if m_key not in st.session_state.factory_profile:
                                    st.session_state.factory_profile[m_key] = 50

                        m_updates = result['metrics_updates']
                        for m_key, m_val in m_updates.items():
                            full_key = f"{m_key}_score"
                            if full_key in st.session_state.factory_profile:
                                current_m = st.session_state.factory_profile[full_key]
                                new_m = max(0, min(100, current_m + m_val))
                                st.session_state.factory_profile[full_key] = new_m
                                
                                icon_map = {'quality': '💎', 'brand': '✨', 'innovation': '🚀'}
                                st.toast(f"{icon_map.get(m_key, '📈')} {m_key.title()}: {m_val:+}", icon=icon_map.get(m_key, '📈'))

                    # MAINTENANCE POLICY UPDATE [NEW]
                    # MAINTENANCE POLICY UPDATE [NEW]
                    if result.get('maintenance_policy') is not None:
                        try:
                            val = float(result['maintenance_policy'])
                            st.session_state.factory_profile['maintenance_policy'] = val
                            
                            policy_map = {0.5: "Ucuz Bakım", 1.0: "Standart", 1.5: "Önleyici (Pahalı)"}
                            st.toast(f"🔧 Bakım Politikası: {policy_map.get(val, str(val))} ({val}x)", icon="🛠️")
                        except (ValueError, TypeError):
                            pass

                    # Save to history
                    st.session_state.history.append({
                        'decision': final_decision,
                        'result': result,
                        'classification': classification,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    # Parse and Update State
                    try:
                        import json
                        # Ensure result contains is_allowed check
                        if isinstance(result, str):
                            # Fallback if agent returned string (should generally be dict from process_decision)
                            pass 
                        
                        # Update History & Badges
                        # Increment counter ONLY if allowed
                        if result.get('is_allowed', True):
                            st.session_state.decisions_this_month += 1
                            
                            # Check badges
                            new_badges = utils.check_badges(st.session_state.event_history)
                            for badge in new_badges:
                                if badge not in st.session_state.badges:
                                    st.session_state.badges.append(badge)
                                    st.toast(f"🏆 Yeni Rozet: {badge['name']}", icon="🎉")
                                    
                            # ISSUE RESOLUTION LOGIC
                            resolved_list = result.get('resolved_issues', [])
                            if resolved_list:
                                current_issues = st.session_state.factory_profile.get('active_issues', [])
                                remaining_issues = []
                                
                                for existing in current_issues:
                                    is_resolved = False
                                    existing_title = existing['title'] if isinstance(existing, dict) else str(existing)
                                    
                                    found_match = False
                                    
                                    # Normalize strings
                                    e_title = existing_title.lower()
                                    e_desc = existing.get('description', '').lower() if isinstance(existing, dict) else ''
                                    
                                    for r in resolved_list:
                                        r_clean = r.lower()
                                        # Match Logic:
                                        # 1. Exact title match (fuzzy)
                                        # 2. Resolution matches title
                                        # 3. Resolution matches distinct words in title
                                        
                                        if r_clean in e_title or e_title in r_clean:
                                            found_match = True
                                        elif e_desc and (r_clean in e_desc):
                                            found_match = True
                                        
                                        # Word overlap check (if > 1 chars, match intersection)
                                        # Helps if AI says "ISO" and issue is "ISO 16949"
                                        if not found_match:
                                            r_words = set(w for w in r_clean.split() if len(w) > 1)
                                            e_words = set(w for w in e_title.split() if len(w) > 1)
                                            if r_words and e_words:
                                                common = r_words.intersection(e_words)
                                                if len(common) >= 1: # At least 1 significant word overlap
                                                    found_match = True
                                        
                                        if found_match:
                                            break
                                    
                                    if found_match:
                                        is_resolved = True
                                        st.toast(f"✅ Sorun Çözüldü: {existing_title}", icon="🛠️")
                                        
                                        # Add to "Resolved This Month" list for display
                                        if 'resolved_issues_this_month' not in st.session_state:
                                            st.session_state.resolved_issues_this_month = []
                                        
                                        st.session_state.resolved_issues_this_month.append(existing)
                                        # Set Cooldown (No new problems for 1 month)
                                        st.session_state.problem_cooldown = 1
                                    
                                    if not is_resolved:
                                        remaining_issues.append(existing)
                                        
                                st.session_state.factory_profile['active_issues'] = remaining_issues
                                
                    except Exception as e:
                        st.error(f"Hata: {e}")
                        
                    # DEBUG UI
                    with st.expander("🕵️ AI Debug (Geliştirici)"):
                        st.json(result)
                        st.write("Resolved List from AI:", result.get('resolved_issues'))
                        st.write("Active Issues Before:", [i['title'] if isinstance(i, dict) else str(i) for i in profile_with_issues.get('active_issues', [])])

                    
                    # INVESTMENT DETECTION: Check if decision is an investment
                    if result.get('is_investment', False) and result.get('investment_delay_weeks', 0) > 0:
                        weeks = result['investment_delay_weeks']
                        
                        st.session_state.pending_investments.append({
                            'decision': final_decision,
                            'remaining_weeks': weeks,
                            'description': result.get('investment_description', ''),
                            'delayed_production_impact': result.get('delayed_production_impact', 0),
                            'delayed_budget_impact': result.get('delayed_budget_impact', 0),
                            'delayed_satisfaction_impact': result.get('delayed_satisfaction_impact', 0)
                        })
                        st.info(f"⏳ **Yatırım Takvime Eklendi!** {result.get('investment_description', 'Yatırım')} - Tahmini süre: {weeks} hafta.")
                    
                    # REMOVED: Automatic time advancement and investment check here.
                    # It is now handled by the "Ayı Bitir" button.
                    
                    # Game Over Check
                    if st.session_state.budget <= 0:
                        st.session_state.game_over = True
                        st.session_state.game_over_reason = "İFLAS ETTİNİZ! Bütçe tükendi."
                    elif st.session_state.risk_level >= 90:
                        st.session_state.game_over = True
                        st.session_state.game_over_reason = "FABRİKA KAPATILDI! Risk seviyesi çok yüksek."
                    
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
    
    # Impact Visualization Table
    st.markdown("### 🗓️ Gelecek Etkiler Tablosu")
    if st.session_state.pending_investments:
        import pandas as pd
        
        table_data = []
        for inv in st.session_state.pending_investments:
            weeks_left = max(0, inv.get('remaining_weeks', 0))
            table_data.append({
                "Yatırım/Karar": inv['description'] or inv['decision'],
                "Kalan Süre": f"⏳ {weeks_left} Hafta",
                "Beklenen Etki": f"Üretim: {inv['delayed_production_impact']:+}% | Bütçe: {inv['delayed_budget_impact']:+,} TL"
            })
        
        df = pd.DataFrame(table_data)
        df.index = range(1, len(df) + 1)
        st.table(df)
    else:
        st.text("Henüz bekleyen yatırım veya süreli etki yok.")


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
        # CHECK FOR RESEARCH REPORT FIRST
        research_data = result.get('research_analysis')
        if research_data:
            st.markdown("### 📄 Araştırma & İstihbarat Raporu")
            with st.container():
                st.info(f"**📌 {research_data.get('title', 'Rapor')}**")
                
                st.markdown("**Bulgular:**")
                # Ensure findings is iterable even if API returns null
                findings = research_data.get('findings') or []
                if findings:
                    for finding in findings:
                        st.markdown(f"- {finding}")
                else:
                    st.markdown("_Bulgu yok._")
                
                if research_data.get('recommendation'):
                    st.markdown(f"**💡 Stratejik Öneri:** {research_data.get('recommendation')}")
            st.markdown("---")

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
        
        if classification.get('risk_score', 0) > 7:
             st.warning("⚠️ **Yüksek riskli karar!** Dikkatli ilerleyin.")
             
        # Side effects
        side_effects = st.session_state.current_result.get('side_effects', [])
        if side_effects:
            st.markdown("### ⚙️ Yan Etkiler")
            for effect in side_effects:
                st.markdown(f"- {effect}")
        
        # Risk explanation
        st.markdown("### 📝 Detaylı Açıklama")
        st.write(st.session_state.current_result.get('risk_explanation', 'Açıklama yok'))
             
# Financial Reports Tab
# Legacy finance tab removed
    
# Summary section
# (Side effects moved to game tab)
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