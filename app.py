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
if 'week_number' not in st.session_state:
    st.session_state.week_number = 1
if 'pending_investments' not in st.session_state:
    st.session_state.pending_investments = []  # [{investment_data, activation_week}]
if 'current_event' not in st.session_state:
    st.session_state.current_event = None
if 'event_history' not in st.session_state:
    st.session_state.event_history = []

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")
    
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
        st.session_state.week_number = 1
        st.session_state.pending_investments = []
        st.session_state.current_event = None
        st.session_state.event_history = []
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

# Factory Profile Display
st.markdown("---")
st.markdown("## 🏢 Fabrika Profili")
profile = st.session_state.factory_profile
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**🏭 Sektör:** {profile['sector']}")
with col2:
    st.markdown(f"**👥 Çalışan:** {profile['employee_count']['total']} kişi")
with col3:
    st.markdown(f"**📊 Durum:** {profile['current_status']}")

st.markdown("---")

# Professional KPI Dashboard
st.markdown("## 📊 KPI Dashboard")

# Calculate deltas
budget_delta = st.session_state.budget - st.session_state.previous_budget
satisfaction_delta = st.session_state.satisfaction - st.session_state.previous_satisfaction
production_delta = st.session_state.production_rate - st.session_state.previous_production_rate
risk_delta = st.session_state.risk_level - st.session_state.previous_risk_level

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.metric(
        "💰 Bütçe (TL)",
        f"{st.session_state.budget:,.0f}",
        delta=f"{budget_delta:+,.0f}" if budget_delta != 0 else None,
        delta_color="inverse"
    )

with kpi_col2:
    st.metric(
        "😊 Memnuniyet (%)",
        f"{st.session_state.satisfaction:.1f}",
        delta=f"{satisfaction_delta:+.1f}" if satisfaction_delta != 0 else None
    )

with kpi_col3:
    st.metric(
        "⚙️ Üretim Hızı (%)",
        f"{st.session_state.production_rate:.1f}",
        delta=f"{production_delta:+.1f}" if production_delta != 0 else None
    )

with kpi_col4:
    st.metric(
        "⚠️ Risk Seviyesi (%)",
        f"{st.session_state.risk_level:.1f}",
        delta=f"{risk_delta:+.1f}" if risk_delta != 0 else None,
        delta_color="inverse"
    )

with kpi_col5:
    level_name, level_num, progress = utils.calculate_level(st.session_state.score)
    st.metric("⭐ Yönetici Seviyesi", level_name)

with kpi_col6:
    st.metric("📅 Hafta", f"#{st.session_state.week_number}")

# Progress bar for level
st.progress(progress, text=f"Sonraki seviyeye: %{int(progress*100)}")

# Badges display
if st.session_state.badges:
    st.markdown("### 🏆 Başarı Rozetleri")
    badge_cols = st.columns(min(len(st.session_state.badges), 4))
    for idx, badge in enumerate(st.session_state.badges):
        with badge_cols[idx % 4]:
            st.success(f"**{badge['name']}**\n\n{badge['desc']}")

st.markdown("---")

# Live Charts with Plotly
st.markdown("## 📈 Performans Grafikleri")

# Prepare data for charts - safely handle empty history
if st.session_state.history:
    decisions = ["Başlangıç"] + [
        entry['decision'][:30] + "..." if len(entry['decision']) > 30 else entry['decision']
        for entry in st.session_state.history
    ]
    
    budget_values = [st.session_state.factory_profile['initial_budget']]
    satisfaction_values = [st.session_state.factory_profile['initial_satisfaction']]
    production_values = [st.session_state.factory_profile['initial_production_rate']]
    
    for i in range(len(st.session_state.history)):
        # Calculate cumulative values
        budget_change = sum(
            entry['result'].get('budget_impact', 0) 
            for entry in st.session_state.history[:i+1]
        )
        satisfaction_change = sum(
            entry['result'].get('satisfaction_impact', 0) 
            for entry in st.session_state.history[:i+1]
        )
        production_change = sum(
            entry['result'].get('production_rate_impact', 0) 
            for entry in st.session_state.history[:i+1]
        )
        
        budget_values.append(max(0, st.session_state.factory_profile['initial_budget'] + budget_change))
        satisfaction_values.append(max(0, min(100, st.session_state.factory_profile['initial_satisfaction'] + satisfaction_change)))
        production_values.append(max(0, min(150, st.session_state.factory_profile['initial_production_rate'] + production_change)))
else:
    # No history yet - show initial values only
    decisions = ["Başlangıç"]
    budget_values = [st.session_state.factory_profile['initial_budget']]
    satisfaction_values = [st.session_state.factory_profile['initial_satisfaction']]
    production_values = [st.session_state.factory_profile['initial_production_rate']]

# Create plotly figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=decisions,
    y=budget_values,
    mode='lines+markers',
    name='Bütçe (TL)',
    line=dict(color='#667eea', width=3),
    yaxis="y1"
))

fig.add_trace(go.Scatter(
    x=decisions,
    y=satisfaction_values,
    mode='lines+markers',
    name='Memnuniyet (%)',
    line=dict(color='#764ba2', width=3),
    yaxis="y2"
))

fig.add_trace(go.Scatter(
    x=decisions,
    y=production_values,
    mode='lines+markers',
    name='Üretim Hızı (%)',
    line=dict(color='#f093fb', width=3),
    yaxis="y2"
))

# Update layout
fig.update_layout(
    title="Fabrika Performans Trendleri",
    xaxis=dict(title="Kararlar", tickangle=45),
    yaxis=dict(
        title=dict(text="Bütçe (TL)", font=dict(color="#667eea")),
        tickfont=dict(color="#667eea"),
        side="left"
    ),
    yaxis2=dict(
        title=dict(text="Memnuniyet & Üretim (%)", font=dict(color="#764ba2")),
        tickfont=dict(color="#764ba2"),
        anchor="x",
        overlaying="y",
        side="right"
    ),
    legend=dict(x=0.01, y=0.99),
    height=400,
    margin=dict(l=50, r=50, t=50, b=100)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

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
                            'week': st.session_state.week_number,
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
                    'week': st.session_state.week_number,
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
    st.markdown("Fabrika yöneticisi olarak kararınızı yazın. AI ajanları gerçekçi sonuçları simüle edecek.")

    # Decision selection
    decision_col1, decision_col2 = st.columns([2, 1])

    with decision_col1:
        decision_input = st.text_area(
            "Kararınızı yazın:",
            placeholder="Örn: Vardiya sayısını 2'den 3'e çıkar, Makine bakım bütçesini %20 artır, 50 yeni çalışan işe al...",
            height=100,
            key="decision_input"
        )
        
        # Quick Action Buttons
        st.markdown("### ⚡ Hızlı Aksiyonlar")
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
        
        quick_actions = [
            ("Bakımı Ertele", "🔧 Preventif bakımları 3 ay ertele"),
            ("Çift Vardiyaya Geç", "🏭 Vardiya sistemini 2'den 3'e çıkar"),
            ("%10 Zam Yap", "💵 Tüm personele %10 maaş zammı ver"),
            ("Kalite Kontrolü Artır", "📊 Kalite kontrol süreçlerini sıkılaştır")
        ]
        
        quick_buttons = []
        with quick_col1:
            if st.button(quick_actions[0][0], key="quick1"):
                quick_buttons.append(quick_actions[0][1])
        with quick_col2:
            if st.button(quick_actions[1][0], key="quick2"):
                quick_buttons.append(quick_actions[1][1])
        with quick_col3:
            if st.button(quick_actions[2][0], key="quick3"):
                quick_buttons.append(quick_actions[2][1])
        with quick_col4:
            if st.button(quick_actions[3][0], key="quick4"):
                quick_buttons.append(quick_actions[3][1])
        
        # Use quick action if selected
        final_decision = decision_input
        if quick_buttons:
            final_decision = quick_buttons[0]  # Use the first clicked quick action
        
        if st.button("🚀 Kararı Uygula", type="primary", use_container_width=True) or quick_buttons:
            if not final_decision or final_decision.strip() == "":
                st.error("Lütfen bir karar yazın veya hızlı aksiyon seçin!")
            else:
                with st.spinner("🤖 AI ajanları sonuçları hesaplıyor..."):
                    # Step 1: Custom Agent - Simulate decision
                    result = agents.simulate_decision(
                        final_decision,
                        st.session_state.context,
                        st.session_state.factory_profile,
                        model=st.session_state.model
                    )
                    st.session_state.current_result = result
                    
                    # Step 2: Classification Agent - Classify risk
                    classification = agents.classify_risk(
                        final_decision,
                        result,
                        model=st.session_state.model
                    )
                    st.session_state.current_classification = classification
                    
                    # Update KPIs
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
                    
                    # Save to history
                    st.session_state.history.append({
                        'decision': final_decision,
                        'result': result,
                        'classification': classification,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    # Check for new badges
                    new_badges = utils.check_badges(st.session_state.history)
                    for badge in new_badges:
                        if badge not in st.session_state.badges:
                            st.session_state.badges.append(badge)
                    
                    # INVESTMENT DETECTION: Check if decision is an investment
                    if result.get('is_investment', False) and result.get('investment_delay_weeks', 0) > 0:
                        activation_week = st.session_state.week_number + result['investment_delay_weeks']
                        st.session_state.pending_investments.append({
                            'decision': final_decision,
                            'activation_week': activation_week,
                            'description': result.get('investment_description', ''),
                            'delayed_production_impact': result.get('delayed_production_impact', 0),
                            'delayed_budget_impact': result.get('delayed_budget_impact', 0),
                            'delayed_satisfaction_impact': result.get('delayed_satisfaction_impact', 0)
                        })
                        st.info(f"⏳ **Yatırım tespit edildi!** {result.get('investment_description', 'Yatırım')} - {result['investment_delay_weeks']} hafta sonra tamamlanacak.")
                    
                    # PENDING INVESTMENTS ACTIVATION: Check if any investments should activate this week
                    activated_investments = []
                    for investment in st.session_state.pending_investments:
                        if investment['activation_week'] == st.session_state.week_number:
                            # Apply delayed effects
                            st.session_state.production_rate = max(0, min(150, st.session_state.production_rate + investment['delayed_production_impact']))
                            st.session_state.budget += investment['delayed_budget_impact']
                            st.session_state.satisfaction = max(0, min(100, st.session_state.satisfaction + investment['delayed_satisfaction_impact']))
                            
                            activated_investments.append(investment)
                            st.success(f"✅ **Yatırım tamamlandı!** {investment['description']}")
                    
                    # Remove activated investments
                    for investment in activated_investments:
                        st.session_state.pending_investments.remove(investment)
                    
                    # GENERATE NEW EVENT for next turn (AI-generated)
                    try:
                        new_event = agents.generate_random_event(
                            st.session_state.factory_profile,
                            st.session_state.risk_level,
                            st.session_state.week_number + 1,  # For next week
                            model=st.session_state.model
                        )
                        if new_event:
                            st.session_state.current_event = new_event
                            st.session_state.current_event['resolved'] = False
                    except Exception as e:
                        print(f"Event generation error: {e}")
                        # No event this turn
                    
                    # INCREMENT WEEK
                    st.session_state.week_number += 1
                    
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