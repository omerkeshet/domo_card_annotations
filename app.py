"""
Domo Card Annotations Manager
A Streamlit app to add and delete annotations on Domo cards.
Configured for Streamlit Cloud deployment.
"""

import streamlit as st
import requests
import pandas as pd
from typing import Any, Dict, List
from datetime import datetime, date

# ==========================
# PAGE CONFIG & STYLING
# ==========================
st.set_page_config(
    page_title="Annotations Manager",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for corporate minimalist design
st.markdown("""
<style>
    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f3f4f6;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom header */
    .main-header {
        font-size: 2.25rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
        letter-spacing: -0.03em;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Section container */
    .section-container {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Section headers */
    .section-header {
        font-size: 0.9rem;
        font-weight: 700;
        color: #111827;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Card styling */
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .card-dark {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-success {
        background: #ecfdf5;
        color: #059669;
    }
    
    .status-info {
        background: #eff6ff;
        color: #2563eb;
    }
    
    /* Card title display */
    .card-info-box {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
    }
    
    .card-id {
        font-size: 0.875rem;
        color: #6b7280;
        font-family: 'SF Mono', 'Monaco', monospace;
    }
    
    /* Stats */
    .stat-value {
        font-size: 2rem;
        font-weight: 600;
        color: #111827;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        padding: 0.625rem 0.875rem;
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        font-size: 0.875rem;
    }
    
    .stSelectbox > div > div {
        border-radius: 6px;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        transition: all 0.15s ease;
    }
    
    .stButton > button[kind="primary"] {
        background: #111827;
        color: white;
        border: none;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #1f2937;
    }
    
    .stButton > button[kind="secondary"] {
        background: white;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    
    /* Table styling */
    .stDataFrame {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        border: none;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
    
    /* Form styling */
    [data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Vertical block styling */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background: transparent;
    }
    
    /* Column containers */
    [data-testid="column"] > div {
        background: transparent;
    }
    
    /* Color preview */
    .color-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #6b7280;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    .empty-state-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Delete section container */
    .delete-section {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        min-height: 200px;
    }
    
    /* Table container */
    .table-container {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    /* Annotation row */
    .annotation-item {
        padding: 1rem;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .annotation-item:last-child {
        border-bottom: none;
    }
    
    /* Additional form cleanup */
    section[data-testid="stForm"] > div:first-child {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================
# CONFIGURATION FROM SECRETS
# ==========================
DOMO_INSTANCE = st.secrets["domo"]["instance"]
DOMO_DEVELOPER_TOKEN = st.secrets["domo"]["developer_token"]

# Available colors for annotations
ANNOTATION_COLORS = {
    "Blue": "#72B0D7",
    "Green": "#80C25D",
    "Red": "#FD7F76",
    "Yellow": "#F5C43D",
    "Purple": "#9B5EE3",
}


# ==========================
# API FUNCTIONS
# ==========================
def product_headers(token: str) -> Dict[str, str]:
    return {
        "X-DOMO-Developer-Token": token,
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "application/json; charset=utf-8",
    }


def fetch_kpi_definition(instance: str, token: str, card_id: str) -> Dict[str, Any]:
    """Fetch the full card definition including annotations."""
    url = f"https://{instance}.domo.com/api/content/v3/cards/kpi/definition"
    payload = {"urn": str(card_id)}

    r = requests.put(url, headers=product_headers(token), json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")

    r.encoding = "utf-8"
    fetched = r.json()
    
    data_source_id = None
    columns = fetched.get("columns", [])
    if columns and len(columns) > 0:
        data_source_id = columns[0].get("sourceId")
    
    if data_source_id:
        subscriptions = fetched.get("definition", {}).get("subscriptions", {})
        for sub_name, sub_def in subscriptions.items():
            if "dataSourceId" not in sub_def:
                sub_def["dataSourceId"] = data_source_id
    
    fetched["_dataSourceId"] = data_source_id
    
    return fetched


def save_card_definition(
    instance: str, 
    token: str, 
    card_id: str, 
    card_def: Dict[str, Any], 
    new_annotations: List[Dict[str, Any]] = None,
    deleted_annotation_ids: List[int] = None
) -> Dict[str, Any]:
    """Save the updated card definition back to Domo."""
    url = f"https://{instance}.domo.com/api/content/v3/cards/kpi/{card_id}"
    
    data_source_id = card_def.get("_dataSourceId")
    if not data_source_id:
        columns = card_def.get("columns", [])
        if columns and len(columns) > 0:
            data_source_id = columns[0].get("sourceId")
    
    definition = card_def.get("definition", {})
    title = definition.get("title", "")
    
    if "dynamicTitle" not in definition:
        definition["dynamicTitle"] = {
            "text": [{"text": title, "type": "TEXT"}] if title else []
        }
    
    if "dynamicDescription" not in definition:
        definition["dynamicDescription"] = {
            "text": [],
            "displayOnCardDetails": True
        }
    
    if "description" not in definition:
        definition["description"] = ""
    
    if "controls" not in definition:
        definition["controls"] = []
    
    if new_annotations is None:
        new_annotations = []
    if deleted_annotation_ids is None:
        deleted_annotation_ids = []
    
    formatted_new = []
    for ann in new_annotations:
        formatted_new.append({
            "content": ann.get("content", ""),
            "dataPoint": ann.get("dataPoint", {}),
            "color": ann.get("color", "#72B0D7"),
        })
    
    definition["annotations"] = {
        "new": formatted_new,
        "modified": [],
        "deleted": deleted_annotation_ids
    }
    
    definition["formulas"] = {
        "dsUpdated": [],
        "dsDeleted": [],
        "card": []
    }
    
    definition["conditionalFormats"] = {
        "card": [],
        "datasource": []
    }
    
    if "segments" in definition:
        segments = definition["segments"]
        if isinstance(segments, dict) and "active" in segments and "definitions" in segments:
            definition["segments"] = {
                "active": segments.get("active", []),
                "create": [],
                "update": [],
                "delete": []
            }
    
    save_payload = {
        "definition": definition,
        "dataProvider": {
            "dataSourceId": data_source_id
        },
        "variables": True
    }
    
    r = requests.put(url, headers=product_headers(token), json=save_payload, timeout=60)
    
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    
    r.encoding = "utf-8"
    return r.json() if r.text else {"status": "success"}


def get_annotations(card_def: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract annotations from card definition."""
    return card_def.get("definition", {}).get("annotations", [])


def get_card_title(card_def: Dict[str, Any]) -> str:
    """Get the card title."""
    return card_def.get("definition", {}).get("title", "Untitled Card")


# ==========================
# STREAMLIT APP
# ==========================

# Header
st.markdown('<p class="main-header">◆ Annotations Manager</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Manage annotations on Domo cards</p>', unsafe_allow_html=True)

# Card Loader Section
if "card_def" not in st.session_state:
    st.markdown('<p class="section-header">Load Card</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        card_id = st.text_input(
            "Card ID",
            placeholder="Enter card ID (e.g., 19344562)",
            label_visibility="collapsed"
        )
    with col2:
        load_button = st.button("Load Card", type="primary", use_container_width=True)
    
    if load_button:
        if not card_id:
            st.error("Please enter a Card ID")
        else:
            with st.spinner("Loading..."):
                try:
                    card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
                    st.session_state.card_def = card_def
                    st.session_state.card_id = card_id
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading card: {str(e)}")

# Main Interface (when card is loaded)
if "card_def" in st.session_state and "card_id" in st.session_state:
    card_def = st.session_state.card_def
    card_id = st.session_state.card_id
    annotations = get_annotations(card_def)
    
    # Card Info Header
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        st.markdown(f'<p class="card-title">{get_card_title(card_def)}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="card-id">ID: {card_id}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<p class="stat-value">{len(annotations)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="stat-label">Annotations</p>', unsafe_allow_html=True)
    
    with col3:
        if st.button("✕ Close", type="secondary"):
            del st.session_state.card_def
            del st.session_state.card_id
            st.rerun()
    
    st.divider()
    
    # Two column layout
    col_add, col_delete = st.columns(2, gap="large")
    
    # ADD ANNOTATION
    with col_add:
        st.markdown('<p class="section-header">Add Annotation</p>', unsafe_allow_html=True)
        
        with st.form("add_form", clear_on_submit=True):
            annotation_text = st.text_area(
                "Text",
                placeholder="Enter annotation text...",
                height=100
            )
            
            col_date, col_color = st.columns(2)
            with col_date:
                annotation_date = st.date_input("Date", value=date.today())
            with col_color:
                color_name = st.selectbox("Color", options=list(ANNOTATION_COLORS.keys()))
            
            submitted = st.form_submit_button("Add Annotation", type="primary", use_container_width=True)
            
            if submitted:
                if not annotation_text:
                    st.error("Please enter annotation text")
                else:
                    with st.spinner("Adding..."):
                        try:
                            new_annotation = {
                                "content": annotation_text,
                                "dataPoint": {"point1": annotation_date.strftime("%Y-%m-%d")},
                                "color": ANNOTATION_COLORS[color_name],
                            }
                            
                            save_card_definition(
                                DOMO_INSTANCE, 
                                DOMO_DEVELOPER_TOKEN, 
                                card_id, 
                                card_def,
                                new_annotations=[new_annotation]
                            )
                            
                            st.session_state.card_def = fetch_kpi_definition(
                                DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id
                            )
                            st.success("Annotation added")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
    
    # DELETE ANNOTATION
    with col_delete:
        st.markdown('<p class="section-header">Delete Annotation</p>', unsafe_allow_html=True)
        
        if annotations:
            annotation_options = {}
            for ann in annotations:
                content_preview = ann['content'][:40] + ('...' if len(ann['content']) > 40 else '')
                date_str = ann['dataPoint'].get('point1', 'N/A')
                label = f"{content_preview} • {date_str}"
                annotation_options[label] = ann['id']
            
            selected = st.selectbox(
                "Select annotation",
                options=list(annotation_options.keys()),
                label_visibility="collapsed"
            )
            
            if st.button("Delete Selected", type="secondary", use_container_width=True):
                annotation_id = annotation_options[selected]
                with st.spinner("Deleting..."):
                    try:
                        save_card_definition(
                            DOMO_INSTANCE, 
                            DOMO_DEVELOPER_TOKEN, 
                            card_id, 
                            card_def,
                            deleted_annotation_ids=[annotation_id]
                        )
                        
                        st.session_state.card_def = fetch_kpi_definition(
                            DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id
                        )
                        st.success("Annotation deleted")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <p>No annotations to delete</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # ANNOTATIONS TABLE
    col_header, col_refresh = st.columns([4, 1])
    with col_header:
        st.markdown('<p class="section-header">All Annotations</p>', unsafe_allow_html=True)
    with col_refresh:
        if st.button("↻ Refresh", type="secondary"):
            with st.spinner(""):
                st.session_state.card_def = fetch_kpi_definition(
                    DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id
                )
                st.rerun()
    
    annotations = get_annotations(st.session_state.card_def)
    
    if annotations:
        df_data = []
        for ann in annotations:
            created_ts = ann.get("createdDate", 0)
            created_str = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d %H:%M") if created_ts else "—"
            
            df_data.append({
                "Content": ann.get("content"),
                "Date": ann.get("dataPoint", {}).get("point1", "—"),
                "Color": ann.get("color", "—"),
                "Created By": ann.get("userName", "—"),
                "Created": created_str,
                "ID": ann.get("id"),
            })
        
        df = pd.DataFrame(df_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Content": st.column_config.TextColumn("Content", width="large"),
                "Date": st.column_config.TextColumn("Date", width="small"),
                "Color": st.column_config.TextColumn("Color", width="small"),
                "Created By": st.column_config.TextColumn("Created By", width="medium"),
                "Created": st.column_config.TextColumn("Created", width="medium"),
                "ID": st.column_config.NumberColumn("ID", width="small", format="%d"),
            }
        )
    else:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <p>No annotations on this card yet</p>
            </div>
        """, unsafe_allow_html=True)
