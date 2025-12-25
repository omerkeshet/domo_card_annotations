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
from pathlib import Path

# ==========================
# PAGE CONFIG & STYLING
# ==========================
st.set_page_config(
    page_title="Annotations Manager",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching View Reports Processor design
st.markdown("""
<style>
    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* App background with gradient */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1200px 600px at 20% -10%, rgba(31,79,216,0.10), rgba(255,255,255,0) 60%),
            radial-gradient(1000px 700px at 90% 10%, rgba(34,197,94,0.08), rgba(255,255,255,0) 55%),
            linear-gradient(180deg, rgba(250,250,252,1), rgba(255,255,255,1));
    }

    /* Page container */
    .block-container {
        padding-top: 2.0rem;
        padding-bottom: 2.0rem;
        max-width: 980px;
    }

    /* Normalize spacing */
    .stMarkdown {margin: 0 !important;}
    .stMarkdown p {margin: 0.25rem 0 0 0 !important;}

    /* Title */
    h1 {
        font-size: 2.05rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin: 0 0 0.2rem 0;
    }

    .muted { color: rgba(49, 51, 63, 0.72); }
    .tiny  { font-size: 0.82rem; color: rgba(49, 51, 63, 0.65); }

    /* Card containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(49, 51, 63, 0.14) !important;
        border-radius: 18px !important;
        background: rgba(255,255,255,0.86) !important;
        box-shadow: 0 6px 22px rgba(0,0,0,0.04) !important;
        padding: 14px 16px !important;
    }

    /* Section label */
    .label {
        font-size: 0.96rem;
        font-weight: 850;
        line-height: 1.15;
        margin: 0 0 0.35rem 0;
    }

    .desc {
        color: rgba(49, 51, 63, 0.72);
        font-size: 0.95rem;
        margin: 0 0 0.9rem 0;
    }

    /* Primary button */
    .stButton button[kind="primary"] {
        background: linear-gradient(180deg, #1f4fd8, #1a3fa8);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.66rem 1rem;
        font-weight: 800;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(180deg, #245ef5, #1f4fd8);
        color: white;
    }

    /* Secondary button */
    .stButton button[kind="secondary"] {
        border-radius: 14px;
        font-weight: 700;
        padding: 0.66rem 1rem;
        border: 1px solid rgba(49, 51, 63, 0.2);
        background: rgba(255,255,255,0.8);
    }
    .stButton button[kind="secondary"]:hover {
        background: rgba(255,255,255,1);
        border-color: rgba(49, 51, 63, 0.3);
    }

    /* Status chip */
    .chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(49,51,63,0.16);
        background: rgba(255,255,255,0.70);
        font-size: 0.85rem;
        font-weight: 750;
    }
    
    .chip-success {
        background: rgba(34,197,94,0.12);
        border-color: rgba(34,197,94,0.3);
        color: #15803d;
    }

    /* Form styling */
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }
    
    section[data-testid="stForm"] > div:first-child {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        background: rgba(255,255,255,0.9) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1f4fd8 !important;
        box-shadow: 0 0 0 3px rgba(31,79,216,0.1) !important;
    }

    .stSelectbox > div > div {
        border-radius: 12px !important;
    }

    .stDateInput > div > div > input {
        border-radius: 12px !important;
    }

    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid rgba(49, 51, 63, 0.1);
        margin: 1.5rem 0;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 2.5rem 1rem;
        color: rgba(49, 51, 63, 0.6);
    }

    .empty-state-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        opacity: 0.5;
    }

    /* Stat display */
    .stat-box {
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #111827;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: rgba(49, 51, 63, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Card info header */
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    
    .card-id {
        font-size: 0.82rem;
        color: rgba(49, 51, 63, 0.6);
        font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    }

    /* Footer */
    .app-footer {
        position: fixed;
        bottom: 8px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 0.72rem;
        color: rgba(49, 51, 63, 0.35);
        pointer-events: none;
        letter-spacing: 0.02em;
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

# Domo users who can create annotations
DOMO_USERS = [
    (185253795, "Ariel Ron"),
    (461573038, "Liron Akuny"),
    (552394961, "Lital Tatuani"),
    (1077384251, "Niv Shir"),
    (385958743, "Omer Yarchi"),
    (935904394, "Roi Green"),
    (1430837746, "Sagiv Naor"),
    (1377140685, "Shirly Laufer Harpo"),
    (554866866, "Tal ugashi"),
    (272049214, "Viki Livshits"),
    (77632399, "Yakir Cohen"),
    (270037743, "Yarden Sabadra"),
    (424727770, "Yotam Abt"),
]


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
        new_ann = {
            "content": ann.get("content", ""),
            "dataPoint": ann.get("dataPoint", {}),
            "color": ann.get("color", "#72B0D7"),
        }
        # Include userId and userName if provided
        if "userId" in ann:
            new_ann["userId"] = ann["userId"]
        if "userName" in ann:
            new_ann["userName"] = ann["userName"]
        formatted_new.append(new_ann)
    
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
st.title("◆ Annotations Manager")
st.markdown(
    "<div class='muted'>Add and delete annotations on Domo cards. "
    "Enter a card ID to get started.</div>",
    unsafe_allow_html=True,
)

st.write("")

# Card Loader Section
if "card_def" not in st.session_state:
    with st.container(border=True):
        st.markdown("<div class='label'>Load Card</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='desc'>Enter the Domo card ID to load its annotations.</div>",
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            card_id = st.text_input(
                "Card ID",
                placeholder="e.g., 19344562",
                label_visibility="collapsed"
            )
        with col2:
            load_button = st.button("Load", type="primary", use_container_width=True)
        
        if load_button:
            if not card_id:
                st.error("Please enter a Card ID")
            else:
                with st.spinner("Loading card..."):
                    try:
                        card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
                        st.session_state.card_def = card_def
                        st.session_state.card_id = card_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading card: {str(e)}")

    st.write("")
    st.info("Enter a card ID above to manage its annotations.")

# Main Interface (when card is loaded)
if "card_def" in st.session_state and "card_id" in st.session_state:
    card_def = st.session_state.card_def
    card_id = st.session_state.card_id
    annotations = get_annotations(card_def)
    
    # Card Info Header
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"<div class='label'>Loaded Card</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-title'>{get_card_title(card_def)}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-id'>ID: {card_id}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='stat-box'>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-value'>{len(annotations)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='stat-label'>Annotations</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.write("")
            if st.button("✕ Close", type="secondary", use_container_width=True):
                del st.session_state.card_def
                del st.session_state.card_id
                st.rerun()
    
    st.write("")
    
    # Two column layout for Add and Delete
    col_add, col_delete = st.columns(2, gap="medium")
    
    # ADD ANNOTATION
    with col_add:
        with st.container(border=True):
            st.markdown("<div class='label'>Add Annotation</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='desc'>Create a new annotation on this card.</div>",
                unsafe_allow_html=True,
            )
            
            with st.form("add_form", clear_on_submit=True):
                annotation_text = st.text_area(
                    "Text",
                    placeholder="Enter annotation text...",
                    height=80,
                    label_visibility="collapsed"
                )
                
                col_date, col_color = st.columns(2)
                with col_date:
                    st.markdown("<div class='tiny'>Date</div>", unsafe_allow_html=True)
                    annotation_date = st.date_input("Date", value=date.today(), label_visibility="collapsed")
                with col_color:
                    st.markdown("<div class='tiny'>Color</div>", unsafe_allow_html=True)
                    color_name = st.selectbox("Color", options=list(ANNOTATION_COLORS.keys()), label_visibility="collapsed")
                
                st.markdown("<div class='tiny'>Created By</div>", unsafe_allow_html=True)
                user_names = [name for (_, name) in DOMO_USERS]
                selected_user_name = st.selectbox("User", options=user_names, label_visibility="collapsed")
                # Get user ID from selected name
                selected_user_id = next(uid for uid, name in DOMO_USERS if name == selected_user_name)
                
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
                                    "userId": selected_user_id,
                                    "userName": selected_user_name,
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
                                st.success("Annotation added!")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
    
    # DELETE ANNOTATION
    with col_delete:
        with st.container(border=True):
            st.markdown("<div class='label'>Delete Annotation</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='desc'>Remove an existing annotation.</div>",
                unsafe_allow_html=True,
            )
            
            if annotations:
                annotation_options = {}
                for ann in annotations:
                    content_preview = ann['content'][:35] + ('...' if len(ann['content']) > 35 else '')
                    date_str = ann['dataPoint'].get('point1', 'N/A')
                    label = f"{content_preview} • {date_str}"
                    annotation_options[label] = ann['id']
                
                selected = st.selectbox(
                    "Select annotation",
                    options=list(annotation_options.keys()),
                    label_visibility="collapsed"
                )
                
                st.write("")
                
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
                            st.success("Annotation deleted!")
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
    
    st.write("")
    
    # ANNOTATIONS TABLE
    with st.container(border=True):
        col_header, col_refresh = st.columns([4, 1])
        with col_header:
            st.markdown("<div class='label'>All Annotations</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='desc'>Showing {len(annotations)} annotation{'s' if len(annotations) != 1 else ''} on this card.</div>",
                unsafe_allow_html=True,
            )
        with col_refresh:
            if st.button("↻ Refresh", type="secondary", use_container_width=True):
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

# Footer
st.markdown(
    """
    <div class="app-footer">
        © Keshet Digital Data Team
    </div>
    """,
    unsafe_allow_html=True,
)
