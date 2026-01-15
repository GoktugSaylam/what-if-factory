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
    
    # Expense Report Display
    if st.session_state.last_month_expenses:
        st.markdown("---")
        st.markdown("### 💰 Geçen Ayın Gelir Tablosu")
        finance = st.session_state.last_month_expenses
        
        # Create a dataframe for cleaner display
        import pandas as pd
        
        # Determine color for Net Profit
        profit_color = "green" if finance['net_profit'] > 0 else "red"
        profit_icon = "📈" if finance['net_profit'] > 0 else "📉"
        
        # Show active modifiers
        revenue_mod_display = ""
        if st.session_state.modifiers['revenue'] != 1.0:
            diff = (st.session_state.modifiers['revenue'] - 1.0) * 100
            revenue_mod_display = f" (Etki: %{diff:+.0f})"
            
        cost_mod_display = ""
        if st.session_state.modifiers['cost'] != 1.0:
            diff = (st.session_state.modifiers['cost'] - 1.0) * 100
            cost_mod_display = f" (Etki: %{diff:+.0f})"
            
        st.markdown(f"""
        | Kalem | Tutar |
        |---|---|
        | **Gelir** {revenue_mod_display} | **{finance['revenue']:,.0f} TL** |
        | - Hammadde (COGS) | {finance.get('raw_material', 0):,.0f} TL |
        | - Maaşlar {cost_mod_display} | {finance['labor']:,.0f} TL |
        | - Enerji {cost_mod_display} | {finance['energy']:,.0f} TL |
        | - Bakım | {finance.get('maintenance', 0):,.0f} TL |
        | - Genel Gider {cost_mod_display} | {finance['overhead']:,.0f} TL |
        | - Kira | {finance['rent']:,.0f} TL |
        | **TOPLAM GİDER** | **{finance['total_expenses']:,.0f} TL** |
        | | |
        | **NET KÂR** | :{profit_color}[**{finance['net_profit']:,.0f} TL**] {profit_icon} |
        """)
    
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

# Main content
st.markdown('<h1 class="main-header">🏭 What-If Factory</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Fabrika Karar Simülatörü - Deneyerek Öğren!</p>', unsafe_allow_html=True)

# Create Tabs
tab_game, tab_finance = st.tabs(["🏭 Fabrika Yönetimi", "📊 Finansal Raporlar"])

with tab_game:
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
    st.markdown("**🚨 Aktif Sorunlar:**")
    # Backward compatibility: Convert older 'current_status' string to list if needed
    if 'active_issues' not in profile:
        profile['active_issues'] = [profile.get('current_status', 'Bilinmiyor')]
    
    # Render issues as cards
    if not profile['active_issues']:
        st.success("✅ Tüm sorunlar çözüldü!")
    else:
        for issue in profile['active_issues']:
            if isinstance(issue, dict):
                # New detailed issue object
                with st.expander(f"🔴 {issue['title']}", expanded=True):
                    st.markdown(issue['description'])
                    st.markdown(f"**⚠️ Çözülmezse:** {issue['consequence']}")
            else:
                # Fallback for old string-based issues
                st.error(f"- {issue}")

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
    st.metric("📅 Ay", f"#{st.session_state.month_number}")

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
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
        
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
            total_revenue = (active_machines * base_rev_per_machine * (current_production / 100)) * revenue_mod
            
            # --- EXPENSES ---
            cost_mod = st.session_state.modifiers['cost']
            
            # 1. RAW MATERIALS (COGS) - [NEW]
            # Directly linked to Revenue (Production Volume)
            # If production matches sales, COGS is % of Revenue
            raw_material_cost = (total_revenue * cogs_rate) * cost_mod
            
            # 2. LABOR: Fixed (Avg 25k/mo)
            labor_cost = (total_employees * 25000) * cost_mod
            
            # 3. MAINTENANCE: Linked to Risk
            maintenance_base = 2000
            maintenance_cost = (machine_count * maintenance_base * (1 + risk / 100)) * cost_mod
            
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
            # APPLY ACTIVE ISSUE PENALTIES (If resolved this month, they were removed before this)
            if 'active_issues' in st.session_state.factory_profile:
                for issue in st.session_state.factory_profile['active_issues']:
                    if isinstance(issue, dict) and 'penalty' in issue:
                        # Apply penalty
                        p = issue['penalty']
                        p_val = p['value']
                        p_type = p['type']
                        
                        if p_type == 'production':
                            st.session_state.production_rate = max(0, st.session_state.production_rate + p_val)
                            st.toast(f"📉 {issue['title']} yüzünden Üretim {p_val}%", icon="🔻")
                        elif p_type == 'budget':
                            st.session_state.budget += p_val
                            st.toast(f"💸 {issue['title']} yüzünden Bütçe {p_val} TL", icon="🔻")
                        elif p_type == 'satisfaction':
                            st.session_state.satisfaction = max(0, st.session_state.satisfaction + p_val)
                            st.toast(f"😡 {issue['title']} yüzünden Memnuniyet {p_val}%", icon="🔻")
                        elif p_type == 'risk':
                            st.session_state.risk_level = min(100, st.session_state.risk_level + p_val)
                            st.toast(f"⚠️ {issue['title']} yüzünden Risk +%{p_val}", icon="🔺")
            
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
                
            
            # PENDING INVESTMENTS ACTIVATION: Check if any investments should activate this month
            activated_investments = []
            for investment in st.session_state.pending_investments:
                if investment['activation_month'] == st.session_state.month_number:
                    # Apply delayed effects
                    st.session_state.production_rate = max(0, min(150, st.session_state.production_rate + investment['delayed_production_impact']))
                    st.session_state.budget += investment['delayed_budget_impact']
                    st.session_state.satisfaction = max(0, min(100, st.session_state.satisfaction + investment['delayed_satisfaction_impact']))
                    
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
                         
                    result = agents.simulate_decision(
                        final_decision,
                        st.session_state.context,
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
                                    
                                    # Check if this existing issue is in the resolved list
                                    # Since AI might return exact string or partial
                                    if existing_title in resolved_list:
                                        is_resolved = True
                                        st.toast(f"✅ Sorun Çözüldü: {existing_title}", icon="🛠️")
                                    
                                    if not is_resolved:
                                        remaining_issues.append(existing)
                                        
                                st.session_state.factory_profile['active_issues'] = remaining_issues
                                
                    except Exception as e:
                        st.error(f"Hata: {e}")
                    
                    # INVESTMENT DETECTION: Check if decision is an investment
                    if result.get('is_investment', False) and result.get('investment_delay_weeks', 0) > 0:
                        # Convert delay weeks to months approximation (1 month = 4 weeks)
                        delay_months = max(1, result['investment_delay_weeks'] // 4)
                        activation_month = st.session_state.month_number + delay_months
                        
                        st.session_state.pending_investments.append({
                            'decision': final_decision,
                            'activation_month': activation_month,
                            'description': result.get('investment_description', ''),
                            'delayed_production_impact': result.get('delayed_production_impact', 0),
                            'delayed_budget_impact': result.get('delayed_budget_impact', 0),
                            'delayed_satisfaction_impact': result.get('delayed_satisfaction_impact', 0)
                        })
                        st.info(f"⏳ **Yatırım tespit edildi!** {result.get('investment_description', 'Yatırım')} - {delay_months} ay sonra tamamlanacak.")
                    
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
            table_data.append({
                "Yatırım/Karar": inv['description'] or inv['decision'],
                "Tamamlanma Ayı": f"#{inv['activation_month']}",
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
with tab_finance:
    st.markdown("## 📈 Finansal Performans Raporu")
    
    if not st.session_state.financial_history:
        st.info("Henüz finansal veri oluşmadı. Oyunu oynamaya başlayın.")
    else:
        import pandas as pd
        df_history = pd.DataFrame(st.session_state.financial_history)
        
        # Determine metrics
        total_months = len(df_history)
        total_profit = df_history['Net Kâr'].sum()
        avg_profit = df_history['Net Kâr'].mean()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam Dönem", f"{total_months} Ay")
        m2.metric("Toplam Net Kâr", f"{total_profit:,.0f} TL")
        m3.metric("Ortalama Aylık Kâr", f"{avg_profit:,.0f} TL")
        
        st.markdown("### 🗓️ Aylık Gelir/Gider Tablosu")
        # Format for display
        st.dataframe(
            df_history.style.format({
                "Gelir": "{:,.0f} TL",
                "Hammadde": "{:,.0f} TL",
                "Personel": "{:,.0f} TL",
                "Enerji": "{:,.0f} TL",
                "Bakım": "{:,.0f} TL",
                "Genel": "{:,.0f} TL",
                "Kira": "{:,.0f} TL",
                "Toplam Gider": "{:,.0f} TL",
                "Net Kâr": "{:,.0f} TL"
            }),
            use_container_width=True
        )
        
        st.markdown("### 📊 Kârlılık Grafiği")
        st.line_chart(df_history, x="Ay", y="Net Kâr")
        
        st.markdown("### 📉 Gider Dağılımı (Son Ay)")
        last_month = df_history.iloc[-1]
        expenses = {
            "Hammadde": last_month.get('Hammadde', 0),
            "Personel": last_month['Personel'],
            "Enerji": last_month['Enerji'],
            "Bakım": last_month.get('Bakım', 0),
            "Genel": last_month['Genel'],
            "Kira": last_month['Kira']
        }
        st.bar_chart(expenses)
    
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