import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import utils

st.set_page_config(page_title="Finansal Raporlar", page_icon="📊", layout="wide")

# Custom CSS for better aesthetics (Shared with Main App)
st.markdown("""
<style>
    /* Main Container Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 95% !important;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        font-weight: 700;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
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
    
    /* Button Styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 Detaylı Finansal Raporlar")
st.markdown("Fabrikanızın geçmiş dönem performans analizleri.")

if 'history' not in st.session_state or not st.session_state.history:
    st.warning("Henüz yeterli veri yok. Lütfen oyunu 'Fabrika Yönetimi' sayfasından başlatın ve birkaç karar alın.")
    st.stop()

# --- 1. KPI SUMMARY ---
st.markdown("### 📈 Genel Performans Özeti")

# Calculate deltas
budget_delta = st.session_state.budget - st.session_state.previous_budget
satisfaction_delta = st.session_state.satisfaction - st.session_state.previous_satisfaction
production_delta = st.session_state.production_rate - st.session_state.previous_production_rate
risk_delta = st.session_state.risk_level - st.session_state.previous_risk_level

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

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

st.markdown("---")

# --- 2. DETAILED INCOME STATEMENT (LAST MONTH) ---
if st.session_state.last_month_expenses:
    st.markdown("### 🧾 Geçen Ayın Gelir Tablosu Detayı")
    finance = st.session_state.last_month_expenses
    
    # Visualization using columns
    col_fin1, col_fin2 = st.columns([1, 2])
    
    with col_fin1:
        profit_color = "green" if finance['net_profit'] > 0 else "red"
        st.markdown(f"""
        ### Net Kâr: :{profit_color}[{finance['net_profit']:,.0f} TL]
        **Gelir:** {finance['revenue']:,.0f} TL
        **Gider:** {finance['total_expenses']:,.0f} TL
        """)
        
        # Donut Chart for Expenses
        expense_breakdown = {
            "Hammadde": finance.get('raw_material', 0),
            "Personel": finance['labor'],
            "Enerji": finance['energy'],
            "Bakım": finance.get('maintenance', 0),
            "Genel": finance['overhead'],
            "Kira": finance['rent']
        }
        
        fig_donut = go.Figure(data=[go.Pie(
            labels=list(expense_breakdown.keys()), 
            values=list(expense_breakdown.values()), 
            hole=.4
        )])
        fig_donut.update_layout(
             title="Gider Dağılımı",
             height=300,
             margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_fin2:
        # Table View
        df_expenses = pd.DataFrame([
            {"Kalem": "Hammadde (COGS)", "Tutar": finance.get('raw_material', 0)},
            {"Kalem": "Personel Giderleri", "Tutar": finance['labor']},
            {"Kalem": "Enerji Maliyetleri", "Tutar": finance['energy']},
            {"Kalem": "Bakım & Onarım", "Tutar": finance.get('maintenance', 0)},
            {"Kalem": "Genel İdari Giderler", "Tutar": finance['overhead']},
            {"Kalem": "Fabrika Kirası", "Tutar": finance['rent']},
            {"Kalem": "TOPLAM", "Tutar": finance['total_expenses']}
        ])
        st.dataframe(
            df_expenses.style.format({"Tutar": "{:,.0f} TL"}),
            use_container_width=True,
            hide_index=True
        )

st.markdown("---")

# --- 3. TREND CHARTS ---
st.markdown("### 📈 Performans Trendleri")

if st.session_state.history:
    # Prepare data
    decisions = ["Başlangıç"] + [f"Ay {e.get('month', '?')}: {e['decision'][:20]}..." for e in st.session_state.history]
    
    # We need to reconstruct the timeline more accurately if possible, 
    # but using the cumulative reconstruction from app.py is fine for now.
    # Better: Use 'financial_history' if available for exact month-end points.
    
    if 'financial_history' in st.session_state and st.session_state.financial_history:
        # Month-by-month financial view
        fin_hist_df = pd.DataFrame(st.session_state.financial_history)
        
        # Chart 1: Revenue vs Profit
        fig_fin = go.Figure()
        fig_fin.add_trace(go.Bar(name='Gelir', x=fin_hist_df['Ay'], y=fin_hist_df['Gelir'], marker_color='#48bb78'))
        fig_fin.add_trace(go.Bar(name='Gider', x=fin_hist_df['Ay'], y=fin_hist_df['Toplam Gider'], marker_color='#f56565'))
        fig_fin.add_trace(go.Scatter(name='Net Kâr', x=fin_hist_df['Ay'], y=fin_hist_df['Net Kâr'], line=dict(color='#4299e1', width=3)))
        
        fig_fin.update_layout(title="Aylık Gelir/Gider Dengesi", barmode='group')
        st.plotly_chart(fig_fin, use_container_width=True)
    
    # Chart 2: Operational Metrics (Budget, Satisfaction, Production)
    # Reusing the logic from app.py for continuity
    budget_values = [st.session_state.factory_profile['initial_budget']]
    satisfaction_values = [st.session_state.factory_profile['initial_satisfaction']]
    production_values = [st.session_state.factory_profile['initial_production_rate']]
    
    for i in range(len(st.session_state.history)):
        entry = st.session_state.history[i]
        
        # Simple additive logic from app.py
        # Note: This is an approximation since actual values might drift with complex events
        # Ideally, we should snapshot values in history. 
        # For now, let's use the current Snapshot if available, or just the reconstruction.
        
        res = entry.get('result', {})
        budget_values.append(max(0, budget_values[-1] + res.get('budget_impact', 0)))
        satisfaction_values.append(max(0, min(100, satisfaction_values[-1] + res.get('satisfaction_impact', 0))))
        production_values.append(max(0, min(150, production_values[-1] + res.get('production_rate_impact', 0))))

    # Create plotly figure
    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=decisions, y=budget_values, mode='lines+markers', name='Bütçe (TL)',
        line=dict(color='#667eea', width=3), yaxis="y1"
    ))

    fig_trend.add_trace(go.Scatter(
        x=decisions, y=satisfaction_values, mode='lines+markers', name='Memnuniyet (%)',
        line=dict(color='#764ba2', width=3), yaxis="y2"
    ))

    fig_trend.add_trace(go.Scatter(
        x=decisions, y=production_values, mode='lines+markers', name='Üretim Hızı (%)',
        line=dict(color='#f093fb', width=3), yaxis="y2"
    ))

    fig_trend.update_layout(
        title="Karar Bazlı Değişim Trendi",
        xaxis=dict(title="Zaman (Kararlar)", tickangle=45),
        yaxis=dict(title="Bütçe (TL)", side="left"),
        yaxis2=dict(title="Oranlar (%)", overlaying="y", side="right"),
        height=500
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")
if st.button("⬅️ Fabrikaya Dön"):
    st.switch_page("Fabrika_Yönetimi.py")
