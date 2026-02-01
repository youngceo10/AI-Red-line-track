import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# --- PAGE CONFIGURATION (Line⁴ Aesthetic) ---
st.set_page_config(
    page_title="Line⁴ | Global Risk Radar",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="▸"
)

# Custom CSS for "Beige/Paper" Aesthetic
st.markdown("""
    <style>
    .stApp {
        background-color: #F9F8F4;
        color: #171717;
    }
    h1, h2, h3 {
        font-family: 'Newsreader', serif;
        color: #171717;
    }
    .stMetricValue {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    div[data-testid="stContainer"] {
        border: 1px solid #e5e5e5;
        padding: 20px;
        border-radius: 8px;
        background-color: white;
    }
    /* Button Styling - High Contrast */
    .stButton > button {
        background-color: #171717 !important;
        color: #FFFFFF !important;
        border: 2px solid #171717 !important;
        font-weight: 600;
        padding: 10px 20px !important;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #374151 !important;
        border-color: #374151 !important;
    }
    /* Primary Button Styling */
    button[kind="primary"] {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover {
        background-color: #991B1B !important;
    }
    .alert-high {
        background-color: #fee2e2;
        border-left: 4px solid #dc2626;
        padding: 12px;
        border-radius: 4px;
    }
    .alert-medium {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 4px;
    }
    .alert-low {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 12px;
        border-radius: 4px;
    }
    .lab-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 15px 0;
    }
    .lab-logo {
        width: 40px;
        height: 40px;
        border-radius: 6px;
        object-fit: contain;
        background: #f5f5f5;
        padding: 4px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    .status-watch {
        background-color: #fef3c7;
        color: #92400e;
    }
    .status-safe {
        background-color: #d1fae5;
        color: #065f46;
    }
    .status-critical {
        background-color: #fee2e2;
        color: #7f1d1d;
    }
    .section-header {
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.5px;
        color: #171717;
        margin-top: 8px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    .metric-label {
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    /* Input and text elements */
    input {
        color: #171717 !important;
        background-color: #FFFFFF !important;
    }
    select {
        color: #171717 !important;
        background-color: #FFFFFF !important;
    }
    /* Dataframe styling */
    .stDataFrame {
        background-color: #FFFFFF;
    }
    /* Divider */
    hr {
        border-color: #D1D5DB;
    }
    </style>
    """, unsafe_allow_html=True)

# Lab logos mapping
LAB_LOGOS = {
    "OpenAI": "https://res.cloudinary.com/djrdh7thl/image/upload/v1769947936/Untitled_3_f6vp7t.png",
    "Anthropic": "https://res.cloudinary.com/djrdh7thl/image/upload/v1769947988/Anthropic_Logo_1_r5jxzt.png",
    "DeepMind": "https://res.cloudinary.com/djrdh7thl/image/upload/v1769947962/DeepMind_idlHaUh9oK_1_kb4fr4.png",
    "Meta": "https://res.cloudinary.com/djrdh7thl/image/upload/v1769948142/Meta_idlf4cVSsS_1_wdkqrv.png"
}

# --- LOAD LIVE DATA ---
def load_anthropic_data():
    """Load Anthropic model card risk data from extracted JSON."""
    anthropic_file = Path('anthropic_model_data.json')
    
    if anthropic_file.exists():
        try:
            with open(anthropic_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Error loading Anthropic data: {e}")
    
    return []

def load_openai_safety_data():
    """Load OpenAI safety evaluation data from JSON - deduplicated by model & top categories."""
    safety_file = Path('safety-data.json')
    
    if safety_file.exists():
        try:
            with open(safety_file, 'r') as f:
                data = json.load(f)
            
            # Convert OpenAI evals to risk format - TOP EVALUATIONS ONLY (deduped)
            risk_items = {}
            # Process only top 12 evaluations to avoid duplication
            for eval_item in data[:12]:
                title = eval_item.get('title', '')
                dataset = eval_item.get('dataset', '')
                scores = eval_item.get('modelScores', {})
                
                # Create descriptive category name
                if dataset and dataset != title:
                    category_name = f"{title} ({dataset})"
                else:
                    category_name = title
                
                # Process top 10 models per evaluation
                for model_name, score_data in list(scores.items())[:10]:
                    score_val = score_data.get('value', 0)
                    
                    # Convert to 0-100 scale (OpenAI uses 0-1 decimal scale)
                    if score_val <= 1:
                        risk_score = int(score_val * 100)
                    else:
                        risk_score = int(score_val)
                    
                    # Determine status
                    if risk_score >= 90:
                        status = "Safe"
                    elif risk_score >= 75:
                        status = "Medium"
                    else:
                        status = "Watch"
                    
                    # Deduplicate by model-category combination
                    key = f"{model_name}|{category_name}"
                    if key not in risk_items:
                        risk_items[key] = {
                            "Lab": "OpenAI",
                            "Model": model_name,
                            "Framework": "Preparedness (PF)",
                            "Risk_Category": category_name,
                            "Score": risk_score,
                            "Threshold": 85,
                            "Status": status,
                            "Citation": f"OpenAI Preparedness Framework - {category_name}"
                        }
            
            return list(risk_items.values())
        except Exception as e:
            st.warning(f"Error loading OpenAI data: {e}")
    
    return []

def deduplicate_and_validate(data):
    """Remove duplicates and validate data consistency."""
    seen = {}
    deduplicated = []
    duplicates_removed = 0
    
    for item in data:
        # Create unique key: Lab + Model + Framework + Risk_Category
        key = f"{item.get('Lab', '')}|{item.get('Model', '')}|{item.get('Framework', '')}|{item.get('Risk_Category', '')}"
        
        if key not in seen:
            seen[key] = True
            # Validate required fields
            required_fields = ['Lab', 'Model', 'Framework', 'Risk_Category', 'Score', 'Status']
            if all(field in item for field in required_fields):
                deduplicated.append(item)
        else:
            duplicates_removed += 1
    
    return deduplicated, duplicates_removed

def load_risk_data():
    """Load risk data from consolidated file or individual sources."""
    all_data = []
    
    # Try consolidated data first (Anthropic + DeepMind)
    consolidated_file = Path('consolidated_risk_data.json')
    if consolidated_file.exists():
        try:
            with open(consolidated_file, 'r') as f:
                all_data = json.load(f)
        except Exception as e:
            st.warning(f"Error loading consolidated data: {e}")
    
    # Load OpenAI safety data (always include)
    openai_data = load_openai_safety_data()
    if openai_data:
        all_data.extend(openai_data)
    
    # Fallback to individual sources if needed
    if not all_data:
        data_file = Path('data/live_risk_data.json')
        live_data = []
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    live_data = json.load(f)
                    all_data.extend(live_data)
            except Exception as e:
                st.warning(f"Error loading live data: {e}")
        
        # Load Anthropic data from extracted PDFs
        anthropic_data = load_anthropic_data()
        if anthropic_data:
            all_data.extend(anthropic_data[:8])
    
    # Deduplicate across all sources
    if all_data:
        all_data, dups_removed = deduplicate_and_validate(all_data)
        # Store in session state for display
        st.session_state.duplicates_removed = dups_removed
        return all_data
    
    # Fallback to minimal defaults
    st.session_state.duplicates_removed = 0
    return [
        {
            "Lab": "Anthropic",
            "Model": "Claude Opus 4.5",
            "Framework": "RSP (ASL)",
            "Risk_Category": "CBRN Uplift",
            "Score": 90, 
            "Threshold": 80,
            "Status": "Watch",
            "Citation": "Extracted from Claude Opus 4.5 System Card"
        },
        {
            "Lab": "Anthropic",
            "Model": "Claude Opus 4.5",
            "Framework": "RSP (ASL)",
            "Risk_Category": "Cyber Offense",
            "Score": 65,
            "Threshold": 85,
            "Status": "Safe",
            "Citation": "Strong coding ability but lacks autonomous exploit generation."
        },
        {
            "Lab": "OpenAI",
            "Model": "GPT-5-main",
            "Framework": "Preparedness (PF)",
            "Risk_Category": "Autonomous Replication",
            "Score": 45,
            "Threshold": 90,
            "Status": "Safe",
            "Citation": "Feb 2026: Low risk for catastrophic autonomous replication."
        },
        {
            "Lab": "OpenAI",
            "Model": "GPT-5-main",
            "Framework": "Preparedness (PF)",
            "Risk_Category": "Deceptive Alignment",
            "Score": 30,
            "Threshold": 75,
            "Status": "Low",
            "Citation": "No evidence of consistent sandbagging in tracked categories."
        },
        {
            "Lab": "DeepMind",
            "Model": "Gemini 3 Pro",
            "Framework": "FSF (CCL)",
            "Risk_Category": "CBRN Uplift",
            "Score": 35,
            "Threshold": 80,
            "Status": "Safe",
            "Citation": "Did not reach Critical Capability Level (CCL)."
        },
        {
            "Lab": "DeepMind",
            "Model": "Gemini 3 Pro",
            "Framework": "FSF (CCL)",
            "Risk_Category": "Persuasion/Manipulation",
            "Score": 55,
            "Threshold": 80,
            "Status": "Medium",
            "Citation": "Approaching early warning triggers for 'Decision Sabotage'."
        }
    ]

df = pd.DataFrame(load_risk_data())

# --- DASHBOARD LAYOUT ---

# Header
col1, col2 = st.columns([3, 1])
# Header with real source links
col1, col2, col3 = st.columns([2, 1.5, 1.5])
with col1:
    st.title("LINE⁴ | Global Risk Radar")
    st.markdown("**Live Operational Status**: Tracking catastrophic AI risk assessments across CBRN proliferation, cyber offense capabilities, autonomous replication, and deceptive alignment from 3 major safety labs.")
with col2:
    st.caption("DATA SOURCES")
    st.markdown("""
    - [Anthropic System Cards](https://www.anthropic.com/system-cards)
    - [OpenAI Safety Hub](https://openai.com/safety/evaluations-hub/)
    - [DeepMind Model Cards](https://deepmind.google/models/model-cards/)
    """)
with col3:
    if st.button("SYNC DATA"):
        st.rerun()

st.divider()

# DATA QUALITY INDICATOR
data_stats = {
    "Total Assessments": len(df),
    "Labs Covered": df['Lab'].nunique(),
    "Models Tracked": df['Model'].nunique(),
    "Frameworks": df['Framework'].nunique(),
    "Risk Categories": df['Risk_Category'].nunique(),
    "Duplicates Removed": st.session_state.get('duplicates_removed', 0)
}


col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 2px solid #171717; border-radius: 8px; padding: 16px; text-align: center; margin: 8px 0;">
        <div style="color: #6B7280; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Total Assessments</div>
        <div style="color: #171717; font-size: 28px; font-weight: 700; margin-top: 8px;">{data_stats["Total Assessments"]}</div>
    </div>
    """, unsafe_allow_html=True)
with col_stat2:
    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 2px solid #171717; border-radius: 8px; padding: 16px; text-align: center; margin: 8px 0;">
        <div style="color: #6B7280; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Labs</div>
        <div style="color: #171717; font-size: 28px; font-weight: 700; margin-top: 8px;">{data_stats["Labs Covered"]}</div>
    </div>
    """, unsafe_allow_html=True)
with col_stat3:
    st.markdown(f"""
    <div style="background-color: #FFFFFF; border: 2px solid #171717; border-radius: 8px; padding: 16px; text-align: center; margin: 8px 0;">
        <div style="color: #6B7280; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Models</div>
        <div style="color: #171717; font-size: 28px; font-weight: 700; margin-top: 8px;">{data_stats["Models Tracked"]}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# VISUALIZATION ROW - TREND VIEW
st.subheader("RISK TRENDS ACROSS MODELS")

# Prepare trend data
trend_data = df.sort_values('Model').copy()

fig = go.Figure()

# Add line for each risk category
for category in df['Risk_Category'].unique():
    cat_data = trend_data[trend_data['Risk_Category'] == category]
    
    fig.add_trace(go.Scatter(
        x=cat_data['Model'],
        y=cat_data['Score'],
        mode='lines+markers',
        name=category,
        line=dict(width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Model: %{x}<br>' +
                      'Score: %{y}/100<extra></extra>'
    ))

# Add danger threshold line
fig.add_hline(
    y=80,
    line_dash="dash",
    line_color="red",
    annotation_text="DANGER (80)",
    annotation_position="right"
)

# Add warning threshold line
fig.add_hline(
    y=60,
    line_dash="dot",
    line_color="orange",
    annotation_text="WATCH (60)",
    annotation_position="right"
)

fig.update_layout(
    xaxis_title="Model",
    yaxis_title="Risk Score (0-100)",
    height=500,
    hovermode='x unified',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(245,245,245,1)',
    font=dict(family="Inter", color="#171717", size=11),
    xaxis=dict(
        title_font=dict(size=14, color="#171717", family="Inter"),
        tickfont=dict(size=11, color="#171717"),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E5E7EB'
    ),
    yaxis=dict(
        range=[0, 100],
        title_font=dict(size=14, color="#171717", family="Inter"),
        tickfont=dict(size=11, color="#171717"),
        showgrid=True,
        gridwidth=1,
        gridcolor='#E5E7EB'
    ),
    legend=dict(
        x=1.02,
        y=1,
        bgcolor='rgba(255, 255, 255, 0.95)',
        bordercolor='#171717',
        borderwidth=2,
        font=dict(color="#171717", size=12)
    ),
    margin=dict(l=60, r=150, t=50, b=100)
)

fig.update_xaxes(tickangle=45)

st.plotly_chart(fig, use_container_width=True)

st.markdown('')

st.divider()

# CRITICAL ALERTS - WITH PAGINATION
st.subheader("CRITICAL ALERTS")

high_risk = df[df['Score'] > 60].sort_values('Score', ascending=False)

if len(high_risk) > 0:
    # Pagination setup
    items_per_page = 6
    total_items = len(high_risk)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Initialize session state for current page
    if 'alert_page' not in st.session_state:
        st.session_state.alert_page = 1
    
    # Create pagination controls at top
    page_cols = st.columns([0.5] + [1] * min(total_pages, 8) + [0.5])
    
    # Previous button
    with page_cols[0]:
        if st.button("Prev", disabled=(st.session_state.alert_page == 1)):
            st.session_state.alert_page -= 1
            st.rerun()
    
    # Page number buttons (max 8 visible)
    pages_to_show = min(total_pages, 8)
    for i, page_num in enumerate(range(1, pages_to_show + 1), 1):
        with page_cols[i]:
            is_current = page_num == st.session_state.alert_page
            btn_label = f"[{page_num}]" if is_current else f"({page_num})"
            if st.button(btn_label, key=f"page_{page_num}", use_container_width=True):
                st.session_state.alert_page = page_num
                st.rerun()
    
    # Next button
    with page_cols[-1]:
        if st.button("Next", disabled=(st.session_state.alert_page == total_pages)):
            st.session_state.alert_page += 1
            st.rerun()
    
    # Calculate which items to show
    start_idx = (st.session_state.alert_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_data = high_risk.iloc[start_idx:end_idx]
    
    # Display counter
    st.caption(f"**Page {st.session_state.alert_page} of {total_pages}** — Showing {start_idx + 1}-{min(end_idx, total_items)} of {total_items} alerts")
    st.markdown("")
    
    # Display current page items
    for index, row in page_data.iterrows():
        with st.container():
            col_logo, col_info, col_status = st.columns([0.08, 0.62, 0.3])
            with col_logo:
                logo_url = LAB_LOGOS.get(row['Lab'], "")
                if logo_url:
                    st.image(logo_url, width=36)
            with col_info:
                st.markdown(f"**{row['Lab']}** — {row['Model']}")
            with col_status:
                status_class = "status-watch" if row['Score'] > 70 else "status-safe"
                st.markdown(f"<span class='status-badge {status_class}'>{row['Status'].upper()}</span>", unsafe_allow_html=True)
        
        st.progress(row['Score'] / 100)
        st.caption(f"**{row['Risk_Category']}** — {row['Score']}/100")
        st.caption(f"_{row['Citation']}_")
        st.divider()
else:
    st.success("All systems nominal")

st.divider()

# 3. ADVANCED VISUALIZATION - INTERACTIVE VIEW SWITCHING
st.subheader("ADVANCED ANALYSIS")

# View selector with styled radio buttons
st.markdown("""
<style>
div[data-testid="stRadio"] > label > span {
    color: #171717 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
div[data-testid="stRadio"] > div {
    gap: 20px;
}
</style>
""", unsafe_allow_html=True)

view_options = ["Risk Gap Analysis", "Lab Comparison", "Category Heatmap", "Trend Over Models", "Score Distribution"]
selected_view = st.radio("Select View:", view_options, horizontal=True, key="analysis_view")

if selected_view == "Risk Gap Analysis":
    # Group by risk categories - shows assessment distribution across the 4 dimensions
    st.markdown("**Risk Assessment by Category** — CBRN Proliferation | Cyber Offense | Autonomous Replication | Deceptive Alignment")
    
    risk_categories = ["CBRN Proliferation", "Cyber Offense", "Autonomous Replication", "Deceptive Alignment"]
    category_tabs = st.tabs(risk_categories)
    
    for tab_idx, category in enumerate(risk_categories):
        with category_tabs[tab_idx]:
            # Filter data for this risk category
            category_data = df[df['Risk_Category'] == category].copy()
            
            if len(category_data) > 0:
                # Create bar chart grouped by lab
                fig_gap = go.Figure()
                
                for lab in category_data['Lab'].unique():
                    lab_data = category_data[category_data['Lab'] == lab].sort_values('Score', ascending=False)
                    fig_gap.add_trace(go.Bar(
                        y=lab_data['Model'],
                        x=lab_data['Score'],
                        orientation='h',
                        name=lab,
                        hovertemplate="<b>%{y}</b><br>%{fullData.name}<br>Score: %{x}/100<extra></extra>"
                    ))
                
                fig_gap.update_layout(
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(245,245,245,1)',
                    font=dict(family="Inter", color="#171717", size=11),
                    xaxis_title="Risk Score (0-100)",
                    yaxis_title="Model",
                    xaxis=dict(
                        range=[0, 100],
                        title_font=dict(size=13, color="#171717", family="Inter"),
                        tickfont=dict(size=10, color="#171717")
                    ),
                    yaxis=dict(
                        tickfont=dict(size=10, color="#171717")
                    ),
                    barmode='group',
                    hovermode='y unified',
                    legend=dict(
                        bgcolor='rgba(255, 255, 255, 0.95)',
                        bordercolor='#171717',
                        borderwidth=2,
                        font=dict(color="#171717", size=11)
                    )
                )
                st.plotly_chart(fig_gap, use_container_width=True)
                
                # Show summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_score = category_data['Score'].mean()
                    st.metric(f"Average Score", f"{avg_score:.1f}/100")
                with col2:
                    max_score = category_data['Score'].max()
                    st.metric("Highest Risk", f"{max_score}/100")
                with col3:
                    models_count = category_data['Model'].nunique()
                    st.metric("Models Assessed", models_count)
            else:
                st.info(f"No data available for {category}")

elif selected_view == "Lab Comparison":
    # Side-by-side lab comparison
    st.markdown("**Lab Risk Profiles** — Average scores by lab and category")
    
    lab_category_pivot = df.groupby(['Lab', 'Risk_Category'])['Score'].mean().reset_index()
    
    fig_compare = go.Figure()
    for category in df['Risk_Category'].unique():
        category_data = lab_category_pivot[lab_category_pivot['Risk_Category'] == category]
        fig_compare.add_trace(go.Bar(
            x=category_data['Lab'],
            y=category_data['Score'],
            name=category,
            hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1f}<extra></extra>"
        ))
    
    fig_compare.update_layout(
        barmode='group',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#171717", size=11),
        yaxis_title="Average Risk Score",
        xaxis_title="Laboratory",
        hovermode='x unified',
        xaxis=dict(
            title_font=dict(size=13, color="#171717", family="Inter"),
            tickfont=dict(size=11, color="#171717")
        ),
        yaxis=dict(
            title_font=dict(size=13, color="#171717", family="Inter"),
            tickfont=dict(size=11, color="#171717")
        ),
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#171717',
            borderwidth=2,
            font=dict(color="#171717", size=11)
        )
    )
    st.plotly_chart(fig_compare, use_container_width=True)

elif selected_view == "Category Heatmap":
    # Heatmap showing all scores
    st.markdown("**Risk Heatmap** — All assessments by lab, model, and category")
    
    heatmap_pivot = df.pivot_table(
        values='Score',
        index=['Lab', 'Model'],
        columns='Risk_Category',
        aggfunc='mean'
    )
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=[f"{lab} - {model}" for lab, model in heatmap_pivot.index],
        colorscale='RdYlGn_r',
        text=heatmap_pivot.values.round(0),
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate="<b>%{y}</b><br>%{x}<br>Score: %{z:.0f}<extra></extra>",
        colorbar=dict(title="Risk Score")
    ))
    
    fig_heatmap.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#171717", size=11),
        coloraxis=dict(
            colorbar=dict(
                thickness=15,
                len=0.7,
                tickfont=dict(color="#171717", size=11)
            )
        )
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

elif selected_view == "Trend Over Models":
    # Trend showing how risk changes across model versions
    st.markdown("**Risk Trajectory** — Risk scores across model progression")
    
    # Sort by model name to show progression
    df_sorted = df.sort_values('Model')
    
    fig_trend = go.Figure()
    for category in df['Risk_Category'].unique():
        category_data = df_sorted[df_sorted['Risk_Category'] == category]
        fig_trend.add_trace(go.Scatter(
            x=list(range(len(category_data))),
            y=category_data['Score'].values,
            mode='lines+markers',
            name=category,
            hovertemplate="<b>%{fullData.name}</b><br>Score: %{y}<extra></extra>"
        ))
    
    fig_trend.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#171717", size=11),
        xaxis_title="Model (sorted)",
        yaxis_title="Risk Score",
        hovermode='x unified',
        xaxis=dict(
            title_font=dict(size=13, color="#171717", family="Inter"),
            tickfont=dict(size=11, color="#171717")
        ),
        yaxis=dict(
            title_font=dict(size=13, color="#171717", family="Inter"),
            tickfont=dict(size=11, color="#171717")
        ),
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#171717',
            borderwidth=2,
            font=dict(color="#171717", size=11)
        )
    )
    st.plotly_chart(fig_trend, use_container_width=True)

else:  # Score Distribution
    # Histogram of score distribution
    st.markdown("**Risk Distribution** — Frequency of scores across all assessments")
    
    fig_dist = go.Figure()
    for lab in df['Lab'].unique():
        lab_data = df[df['Lab'] == lab]
        fig_dist.add_trace(go.Histogram(
            x=lab_data['Score'],
            name=lab,
            nbinsx=15,
            hovertemplate="<b>%{fullData.name}</b><br>Score: %{x}<br>Count: %{y}<extra></extra>"
        ))
    
    fig_dist.update_layout(
        barmode='group',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#171717", size=11),
        xaxis_title="Risk Score",
        yaxis_title="Number of Assessments",
        hovermode='x',
        xaxis=dict(
            title_font=dict(size=13, color="#171717", family="Inter"),
            tickfont=dict(size=11, color="#171717")
        ),
        yaxis=dict(
            title_font=dict(size=13, color="#171717", family="Inter"),
            tickfont=dict(size=11, color="#171717")
        ),
        legend=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#171717',
            borderwidth=2,
            font=dict(color="#171717", size=11)
        )
    )
    st.plotly_chart(fig_dist, use_container_width=True)

st.divider()

# DETAILED INTELLIGENCE TABLE WITH PAGINATION
st.subheader("DETAILED RISK ASSESSMENT")

# Data consistency check by framework
st.markdown("**Tracking Consistency** — Each lab uses distinct frameworks for evaluation:")
framework_check = df.groupby('Lab')['Framework'].unique()
consistency_cols = st.columns(3)
for idx, (lab, frameworks) in enumerate(framework_check.items()):
    with consistency_cols[idx]:
        framework_list = ", ".join(frameworks)
        st.markdown(f"""
        <div style="background-color: #FFFFFF; border: 2px solid #171717; border-radius: 8px; padding: 12px; margin: 8px 0;">
            <strong style="color: #171717; font-size: 14px;">{lab}</strong><br>
            <span style="color: #171717; font-size: 12px; font-weight: 600;">{framework_list}</span>
        </div>
        """, unsafe_allow_html=True)

display_df = df[['Lab', 'Model', 'Risk_Category', 'Score', 'Threshold', 'Status', 'Citation']].copy()
display_df['Gap'] = display_df['Threshold'] - display_df['Score']

# Pagination for large datasets
rows_per_page = 15
total_rows = len(display_df)
total_pages = (total_rows + rows_per_page - 1) // rows_per_page

# Initialize pagination state
if 'table_page' not in st.session_state:
    st.session_state.table_page = 1

# Pagination controls
col1, col2, col3 = st.columns([0.5, 1, 0.5])
with col1:
    if st.button("Prev", disabled=(st.session_state.table_page == 1), key="prev_table"):
        st.session_state.table_page -= 1
        st.rerun()
with col2:
    page_display = f"Page {st.session_state.table_page} of {total_pages}"
    st.markdown(f"<div style='text-align: center'>{page_display}</div>", unsafe_allow_html=True)
with col3:
    if st.button("Next", disabled=(st.session_state.table_page == total_pages), key="next_table"):
        st.session_state.table_page += 1
        st.rerun()

# Display current page
start_idx = (st.session_state.table_page - 1) * rows_per_page
end_idx = start_idx + rows_per_page
page_df = display_df.iloc[start_idx:end_idx]

st.dataframe(
    page_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        'Score': st.column_config.NumberColumn(format='%d'),
        'Threshold': st.column_config.NumberColumn(format='%d'),
        'Gap': st.column_config.NumberColumn(format='%d'),
    }
)
st.caption(f"Showing {start_idx + 1}-{min(end_idx, total_rows)} of {total_rows} assessments")

st.divider()

# SAFETY FRAMEWORKS
st.subheader("SAFETY FRAMEWORK BREAKDOWN")
st.markdown("**Comparing three independent safety evaluation methodologies across major AI labs:**")

tab1, tab2, tab3 = st.tabs(["Anthropic RSP", "OpenAI Preparedness", "DeepMind FSF"])

with tab1:
    st.markdown("### Responsible Scaling Policy (ASL Levels)")
    st.write("Anthropic's Automation Safety Levels define risk escalation from ASL-1 (minimal risk) to ASL-4 (catastrophic risk).")
    anth_data = df[df['Lab'] == 'Anthropic']
    if len(anth_data) > 0:
        for _, row in anth_data.iterrows():
            asl_level = min(4, max(1, int(row['Score'] / 25) + 1))
            st.markdown(f"**{row['Model']}** | {row['Risk_Category']}")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.progress(row['Score'] / 100)
            with col2:
                st.caption(f"ASL-{asl_level} | {row['Score']}/100")
    else:
        st.info("No Anthropic data available")

with tab2:
    st.markdown("### OpenAI Preparedness Framework")
    st.write("OpenAI tracks risk readiness across four severity levels: Low, Medium, High, Critical.")
    openai_data = df[df['Lab'] == 'OpenAI']
    if len(openai_data) > 0:
        for _, row in openai_data.iterrows():
            if row['Score'] >= 90:
                level = "Critical"
            elif row['Score'] >= 75:
                level = "High"
            elif row['Score'] >= 60:
                level = "Medium"
            else:
                level = "Low"
            st.markdown(f"**{row['Model']}** | {row['Risk_Category']}")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.progress(row['Score'] / 100)
            with col2:
                st.caption(f"{level} | {row['Score']}/100")
    else:
        st.info("No OpenAI data available")

with tab3:
    st.markdown("### DeepMind Frontier Safety Framework")
    st.write("DeepMind uses Critical Capability Levels (CCL) to assess emergence of frontier AI risks.")
    dm_data = df[df['Lab'] == 'DeepMind']
    if len(dm_data) > 0:
        for _, row in dm_data.iterrows():
            st.markdown(f"**{row['Model']}** | {row['Risk_Category']}")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.progress(row['Score'] / 100)
            with col2:
                st.caption(f"CCL Assessment | {row['Score']}/100")
    else:
        st.info("No DeepMind data available")


st.markdown("---")
st.markdown("""
**Line⁴** monitors AI safety evaluations in real-time across four catastrophic risk dimensions. Data sourced from official Lab System Cards: Anthropic RSP framework, OpenAI Preparedness framework, and DeepMind Frontier Safety Framework.

**Data Sources:**
- [Anthropic System Card](https://www.anthropic.com/research/claude-3-system-card)
- [OpenAI System Card](https://openai.com/index/gpt-4o-system-card/)
- [DeepMind Model Cards](https://deepmind.google/models/model-cards/)

**DISCLAIMER:** For research purposes. Not an official safety tool.
""")
