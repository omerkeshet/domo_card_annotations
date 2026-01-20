"""
Domo Card Annotations Manager
A Streamlit app to add and delete annotations on Domo cards.
Configured for Streamlit Cloud deployment.
"""

import streamlit as st
import requests
import pandas as pd
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import snowflake.connector

# ==========================
# PAGE CONFIG & STYLING
# ==========================
st.set_page_config(
    page_title="Annotations Manager",
    page_icon=Path("assets/logo.png"),
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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

    /* Card ID tags */
    .card-tag {
        display: inline-flex;
        align-items: center;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #15803d;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }
    
    .card-tags-container {
        display: flex;
        flex-wrap: wrap;
        margin-top: 8px;
        min-height: 20px;
    }
    
    /* Green tag buttons (for removable card IDs) */
    button[data-testid="stBaseButton-secondary"][kind="secondary"]:has(> div > p:first-child) {
        background: rgba(34, 197, 94, 0.15) !important;
        border: 1px solid rgba(34, 197, 94, 0.4) !important;
        color: #15803d !important;
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    
    button[data-testid="stBaseButton-secondary"][kind="secondary"]:has(> div > p:first-child):hover {
        background: rgba(239, 68, 68, 0.15) !important;
        border-color: rgba(239, 68, 68, 0.4) !important;
        color: #dc2626 !important;
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

    /* Tooltip */
    .info-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        margin-left: 6px;
        font-size: 0.8rem;
        color: rgba(49, 51, 63, 0.4);
        transition: color 0.2s;
    }
    .info-tooltip:hover {
        color: #1f4fd8;
    }
    .info-tooltip .tooltiptext {
        visibility: hidden;
        width: 260px;
        background-color: rgba(30, 30, 30, 0.95);
        color: #fff;
        text-align: right;
        direction: rtl;
        border-radius: 10px;
        padding: 12px 14px;
        position: absolute;
        z-index: 1000;
        top: 130%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.2s, visibility 0.2s;
        font-size: 0.82rem;
        font-weight: 400;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .info-tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        bottom: 100%;
        left: 50%;
        margin-left: -6px;
        border-width: 6px;
        border-style: solid;
        border-color: transparent transparent rgba(30, 30, 30, 0.95) transparent;
    }
    .info-tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# ==========================
# CONFIGURATION FROM SECRETS
# ==========================
DOMO_INSTANCE = st.secrets["domo"]["instance"]
DOMO_DEVELOPER_TOKEN = st.secrets["domo"]["developer_token"]

# Snowflake configuration
SNOWFLAKE_CONFIG = {
    "account": st.secrets["snowflake"]["account"],
    "user": st.secrets["snowflake"]["user"],
    "private_key": st.secrets["snowflake"]["private_key"],
    "database": st.secrets["snowflake"]["database"],
    "schema": st.secrets["snowflake"]["schema"],
    "warehouse": st.secrets["snowflake"]["warehouse"],
    "role": st.secrets["snowflake"]["role"],
}
SNOWFLAKE_TABLE = st.secrets["snowflake"]["table"]

# Available colors for annotations
ANNOTATION_COLORS = {
    "Blue": "#72B0D7",
    "Green": "#80C25D",
    "Red": "#FD7F76",
    "Yellow": "#F5C43D",
    "Purple": "#9B5EE3",
}

COLOR_NAME_MAP = {v: k for k, v in ANNOTATION_COLORS.items()}

# Preset card IDs (add more as needed)
PRESET_CARD_IDS = [
    "954563232",
]


# ==========================
# DOMO API FUNCTIONS
# ==========================
def product_headers(token: str) -> Dict[str, str]:
    return {
        "X-DOMO-Developer-Token": token,
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "application/json; charset=utf-8",
    }


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_card_name(card_id: str) -> str:
    """Fetch card name from Domo API."""
    try:
        card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
        title = card_def.get("definition", {}).get("title", f"Card {card_id}")
        return title
    except:
        return f"Card {card_id}"


def get_preset_cards() -> Dict[str, str]:
    """Get preset cards with their names. Returns {id: name}"""
    preset_cards = {}
    for card_id in PRESET_CARD_IDS:
        name = get_card_name(card_id)
        preset_cards[card_id] = name
    return preset_cards


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


def get_domo_annotations(card_def: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract annotations from card definition."""
    return card_def.get("definition", {}).get("annotations", [])


def add_annotation_to_domo(card_id: str, content: str, entry_date: str, color: str) -> Optional[Dict[str, Any]]:
    """Add annotation to a Domo card and return the created annotation."""
    try:
        card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
        
        new_annotation = {
            "content": content,
            "dataPoint": {"point1": entry_date},
            "color": color,
        }
        
        save_card_definition(
            DOMO_INSTANCE,
            DOMO_DEVELOPER_TOKEN,
            card_id,
            card_def,
            new_annotations=[new_annotation]
        )
        
        # Refresh to get the new annotation with its ID
        updated_card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
        annotations = get_domo_annotations(updated_card_def)
        
        # Find the newly created annotation
        for ann in sorted(annotations, key=lambda x: x.get("createdDate", 0), reverse=True):
            if ann.get("content") == content and ann.get("dataPoint", {}).get("point1") == entry_date:
                return ann
        
        return None
    except Exception as e:
        st.error(f"Error adding to Domo card {card_id}: {str(e)}")
        return None


def delete_annotation_from_domo(card_id: str, annotation_id: int) -> bool:
    """Delete annotation from a Domo card."""
    try:
        card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
        
        save_card_definition(
            DOMO_INSTANCE,
            DOMO_DEVELOPER_TOKEN,
            card_id,
            card_def,
            deleted_annotation_ids=[annotation_id]
        )
        return True
    except Exception as e:
        st.error(f"Error deleting from Domo card {card_id}: {str(e)}")
        return False


# ==========================
# SNOWFLAKE FUNCTIONS
# ==========================
def get_snowflake_connection():
    """Create a Snowflake connection using private key authentication."""
    private_key_pem = SNOWFLAKE_CONFIG["private_key"]
    
    if "\\n" in private_key_pem:
        private_key_pem = private_key_pem.replace("\\n", "\n")
    
    p_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )
    
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_CONFIG["account"],
        user=SNOWFLAKE_CONFIG["user"],
        private_key=pkb,
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        role=SNOWFLAKE_CONFIG["role"],
    )
    return conn


def get_snowflake_annotations(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    card_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get annotations from Snowflake with optional filters."""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        select_sql = f"""
            SELECT ID, CARD_ID, DOMO_USER_ID, DOMO_USER_NAME, COLOR, CONTENT, ENTRY_DATE, CREATED_DATE
            FROM {SNOWFLAKE_TABLE}
            WHERE 1=1
        """
        params = []
        
        if start_date:
            select_sql += " AND ENTRY_DATE >= %s"
            params.append(start_date)
        
        if end_date:
            select_sql += " AND ENTRY_DATE <= %s"
            params.append(end_date)
        
        if card_id:
            select_sql += " AND CARD_ID = %s"
            params.append(int(card_id))
        
        select_sql += " ORDER BY ENTRY_DATE DESC"
        
        cursor.execute(select_sql, params)
        
        rows = cursor.fetchall()
        columns = ["ID", "CARD_ID", "DOMO_USER_ID", "DOMO_USER_NAME", "COLOR", "CONTENT", "ENTRY_DATE", "CREATED_DATE"]
        
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        st.error(f"Snowflake query error: {str(e)}")
        return []


def insert_annotation_to_snowflake(
    content: str,
    entry_date: str,
    color: str,
    card_id: Optional[int] = None,
    annotation_id: Optional[int] = None,
    user_id: Optional[int] = None,
    user_name: Optional[str] = None
) -> bool:
    """Insert a new annotation record into Snowflake."""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        insert_sql = f"""
            INSERT INTO {SNOWFLAKE_TABLE} 
            (CARD_ID, ID, DOMO_USER_ID, DOMO_USER_NAME, COLOR, CONTENT, ENTRY_DATE, CREATED_DATE)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())
        """
        
        cursor.execute(insert_sql, (
            card_id,
            annotation_id,
            user_id,
            user_name,
            color,
            content,
            entry_date
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Snowflake insert error: {str(e)}")
        return False


def delete_annotation_from_snowflake(annotation_id: Optional[int] = None, card_id: Optional[int] = None, content: Optional[str] = None, entry_date: Optional[str] = None) -> bool:
    """Delete an annotation record from Snowflake."""
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        if annotation_id:
            delete_sql = f"DELETE FROM {SNOWFLAKE_TABLE} WHERE ID = %s"
            cursor.execute(delete_sql, (annotation_id,))
        elif content and entry_date:
            # For global annotations (no ID), delete by content and date
            delete_sql = f"DELETE FROM {SNOWFLAKE_TABLE} WHERE CONTENT = %s AND ENTRY_DATE = %s AND ID IS NULL"
            cursor.execute(delete_sql, (content, entry_date))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Snowflake delete error: {str(e)}")
        return False


def sync_card_annotations(card_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, int]:
    """
    Sync annotations from Domo to Snowflake for a specific card.
    Only adds missing annotations, never deletes.
    Also backfills CREATED_DATE from Domo.
    Optionally filter by annotation date range (ENTRY_DATE).
    """
    results = {"inserted": 0, "updated": 0, "skipped": 0}
    
    try:
        # Get Domo annotations
        card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
        domo_annotations = get_domo_annotations(card_def)
        
        # Filter by date range if provided
        if start_date or end_date:
            filtered_annotations = []
            for ann in domo_annotations:
                entry_date = ann.get("dataPoint", {}).get("point1", "")
                if entry_date:
                    if start_date and entry_date < start_date:
                        continue
                    if end_date and entry_date > end_date:
                        continue
                    filtered_annotations.append(ann)
            domo_annotations = filtered_annotations
        
        domo_by_id = {ann.get("id"): ann for ann in domo_annotations}
        
        # Get Snowflake annotations for this card (only those with ID)
        sf_annotations = get_snowflake_annotations(card_id=card_id)
        sf_with_id = [ann for ann in sf_annotations if ann.get("ID") is not None]
        sf_by_id = {ann["ID"]: ann for ann in sf_with_id}
        
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Domo → Snowflake: Add missing, update changed
        for ann_id, ann in domo_by_id.items():
            entry_date = ann.get("dataPoint", {}).get("point1", "")
            content = ann.get("content", "")
            color = ann.get("color", "")
            user_id = ann.get("userId", 0)
            user_name = ann.get("userName", "Unknown")
            
            # Convert Domo createdDate (milliseconds) to timestamp
            created_ts = ann.get("createdDate", 0)
            created_date = datetime.fromtimestamp(created_ts / 1000) if created_ts else None
            
            if ann_id in sf_by_id:
                # Check if update needed (content, color, or missing created_date)
                sf_ann = sf_by_id[ann_id]
                needs_update = (
                    sf_ann["CONTENT"] != content or 
                    sf_ann["COLOR"] != color or
                    sf_ann.get("CREATED_DATE") is None
                )
                
                if needs_update:
                    update_sql = f"""
                        UPDATE {SNOWFLAKE_TABLE}
                        SET CONTENT = %s, COLOR = %s, ENTRY_DATE = %s,
                            DOMO_USER_ID = %s, DOMO_USER_NAME = %s, CREATED_DATE = %s
                        WHERE ID = %s
                    """
                    cursor.execute(update_sql, (content, color, entry_date, user_id, user_name, created_date, ann_id))
                    results["updated"] += 1
                else:
                    results["skipped"] += 1
            else:
                # Insert to Snowflake
                insert_sql = f"""
                    INSERT INTO {SNOWFLAKE_TABLE} 
                    (CARD_ID, ID, DOMO_USER_ID, DOMO_USER_NAME, COLOR, CONTENT, ENTRY_DATE, CREATED_DATE)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (int(card_id), ann_id, user_id, user_name, color, content, entry_date, created_date))
                results["inserted"] += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return results
    except Exception as e:
        st.error(f"Sync error: {str(e)}")
        return results


def push_to_domo(card_id: str, start_date: str, end_date: str, colors: List[str]) -> Dict[str, int]:
    """
    Push annotations from Snowflake to a Domo card.
    Filters by date range and colors.
    """
    results = {"pushed": 0, "failed": 0}
    
    try:
        # Get Snowflake annotations with filters
        sf_annotations = get_snowflake_annotations(start_date=start_date, end_date=end_date)
        
        # Filter by colors
        if colors:
            sf_annotations = [ann for ann in sf_annotations if ann.get("COLOR") in colors]
        
        # Push each annotation to Domo
        for ann in sf_annotations:
            content = ann.get("CONTENT", "")
            entry_date = str(ann.get("ENTRY_DATE", ""))
            color = ann.get("COLOR", "#72B0D7")
            
            domo_ann = add_annotation_to_domo(card_id, content, entry_date, color)
            if domo_ann:
                results["pushed"] += 1
            else:
                results["failed"] += 1
        
        return results
    except Exception as e:
        st.error(f"Push to Domo error: {str(e)}")
        return results
# ==========================
# SESSION STATE INIT
# ==========================
if "card_ids" not in st.session_state:
    st.session_state.card_ids = []


# ==========================
# STREAMLIT APP
# ==========================

# Header
col_logo, col_title = st.columns([0.5, 4])
with col_logo:
    st.image("assets/logo.png", width=50)
with col_title:
    st.title("Annotations Manager")
st.markdown(
    "<div class='muted'>Create and manage annotations. Optionally add to Domo cards.</div>",
    unsafe_allow_html=True,
)

st.write("")

# Two column layout for Add and Delete
col_add, col_delete = st.columns(2, gap="medium")

# ==========================
# ADD ANNOTATION
# ==========================
with col_add:
    with st.container(border=True):
        st.markdown("""<div class='label'>Add Annotation 
            <span class="info-tooltip">ⓘ
                <span class="tooltiptext">כאן ניתן להוסיף הערה חדשה. מלאו את התוכן, בחרו תאריך וצבע. אם רוצים להוסיף לכרטיס דומו - הוסיפו מזהה כרטיס. בלי כרטיס - ההערה תישמר רק בסנופלייק.</span>
            </span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            "<div class='desc'>Create a new annotation. Optionally add to Domo cards.</div>",
            unsafe_allow_html=True,
        )
        
        annotation_text = st.text_area(
            "Content",
            placeholder="Enter annotation text...",
            height=80,
            key="add_content"
        )
        
        col_date, col_color = st.columns(2)
        with col_date:
            st.markdown("<div class='tiny'>Date</div>", unsafe_allow_html=True)
            annotation_date = st.date_input("Date", value=date.today(), label_visibility="collapsed", key="add_date")
        with col_color:
            st.markdown("<div class='tiny'>Color</div>", unsafe_allow_html=True)
            color_name = st.selectbox("Color", options=list(ANNOTATION_COLORS.keys()), label_visibility="collapsed", key="add_color")
        
        # Card IDs section
        st.markdown("<div class='tiny'>Card IDs (optional)</div>", unsafe_allow_html=True)
        
        # Preset cards dropdown
        preset_cards = get_preset_cards()
        preset_options = [""] + [f"{name} ({cid})" for cid, name in preset_cards.items()]
        
        col_preset, col_preset_btn = st.columns([3, 1])
        with col_preset:
            selected_preset = st.selectbox(
                "Common cards",
                options=preset_options,
                format_func=lambda x: "Select from common cards..." if x == "" else x,
                label_visibility="collapsed",
                key="add_preset_card"
            )
        with col_preset_btn:
            if st.button("+ Add", type="secondary", use_container_width=True, key="add_preset_btn"):
                if selected_preset:
                    # Extract card ID from "Name (ID)" format
                    card_id_from_preset = selected_preset.split("(")[-1].rstrip(")")
                    if card_id_from_preset not in st.session_state.card_ids:
                        st.session_state.card_ids.append(card_id_from_preset)
                        st.rerun()
        
        # Manual entry
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            new_card_id = st.text_input("Card ID", placeholder="Or enter card ID manually...", label_visibility="collapsed", key="new_card_id")
        with col_btn:
            if st.button("+ Add", type="secondary", use_container_width=True, key="add_manual_btn"):
                if new_card_id and new_card_id.strip():
                    card_id_clean = new_card_id.strip()
                    if card_id_clean not in st.session_state.card_ids:
                        st.session_state.card_ids.append(card_id_clean)
                        st.rerun()
        
        # Display selected card IDs using multiselect (allows removal by clicking X)
        if st.session_state.card_ids:
            selected = st.multiselect(
                "Selected cards",
                options=st.session_state.card_ids,
                default=st.session_state.card_ids,
                label_visibility="collapsed",
                key="card_ids_display"
            )
            # Update session state if user removed any
            if set(selected) != set(st.session_state.card_ids):
                st.session_state.card_ids = selected
                st.rerun()
        
        st.write("")
        
        if st.button("Add Annotation", type="primary", use_container_width=True):
            if not annotation_text:
                st.error("Please enter annotation text")
            else:
                with st.spinner("Adding annotation..."):
                    entry_date_str = annotation_date.strftime("%Y-%m-%d")
                    color_hex = ANNOTATION_COLORS[color_name]
                    
                    if st.session_state.card_ids:
                        # Add to Domo cards + Snowflake
                        success_cards = []
                        for cid in st.session_state.card_ids:
                            domo_ann = add_annotation_to_domo(cid, annotation_text, entry_date_str, color_hex)
                            if domo_ann:
                                # Insert to Snowflake with card ID and annotation ID
                                sf_success = insert_annotation_to_snowflake(
                                    content=annotation_text,
                                    entry_date=entry_date_str,
                                    color=color_hex,
                                    card_id=int(cid),
                                    annotation_id=domo_ann.get("id"),
                                    user_id=domo_ann.get("userId"),
                                    user_name=domo_ann.get("userName")
                                )
                                if sf_success:
                                    success_cards.append(cid)
                        
                        if success_cards:
                            st.success(f"Annotation added to cards: {', '.join(success_cards)}")
                            st.session_state.card_ids = []
                            st.rerun()
                    else:
                        # Snowflake only (global annotation)
                        sf_success = insert_annotation_to_snowflake(
                            content=annotation_text,
                            entry_date=entry_date_str,
                            color=color_hex
                        )
                        if sf_success:
                            st.success("Global annotation added to Snowflake!")
                            st.rerun()

# ==========================
# DELETE ANNOTATION
# ==========================
with col_delete:
    with st.container(border=True):
        st.markdown("""<div class='label'>Delete Annotation 
            <span class="info-tooltip">ⓘ
                <span class="tooltiptext">כאן ניתן למחוק הערה קיימת. בחרו טווח תאריכים ולחצו Load Annotations. בחרו הערה מהרשימה ולחצו Delete. ההערה תימחק מסנופלייק ומדומו.</span>
            </span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            "<div class='desc'>Filter by date range and select annotation to delete.</div>",
            unsafe_allow_html=True,
        )
        
        # Date range filter
        col_start, col_end = st.columns(2)
        with col_start:
            st.markdown("<div class='tiny'>From Date</div>", unsafe_allow_html=True)
            start_date = st.date_input("Start", value=date.today() - timedelta(days=30), label_visibility="collapsed", key="del_start")
        with col_end:
            st.markdown("<div class='tiny'>To Date</div>", unsafe_allow_html=True)
            end_date = st.date_input("End", value=date.today(), label_visibility="collapsed", key="del_end")
        
        # Load annotations button
        if st.button("Load Annotations", type="secondary", use_container_width=True):
            st.session_state.delete_annotations = get_snowflake_annotations(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
        
        # Show annotations dropdown
        if "delete_annotations" in st.session_state and st.session_state.delete_annotations:
            annotations = st.session_state.delete_annotations
            
            annotation_options = {}
            sorted_annotations = sorted(annotations, key=lambda x: str(x.get("ENTRY_DATE", "")), reverse=True)
            for ann in sorted_annotations:
                content_preview = str(ann['CONTENT'])[:30] + ('...' if len(str(ann['CONTENT'])) > 30 else '')
                date_str = str(ann.get('ENTRY_DATE', 'N/A'))
                card_str = f"Card {ann['CARD_ID']}" if ann.get('CARD_ID') else "Global"
                label = f"{content_preview} • {date_str} • {card_str}"
                annotation_options[label] = ann
            
            selected_label = st.selectbox(
                "Select annotation",
                options=list(annotation_options.keys()),
                label_visibility="collapsed"
            )
            
            st.write("")
            
            if st.button("Delete Selected", type="secondary", use_container_width=True):
                selected_ann = annotation_options[selected_label]
                with st.spinner("Deleting..."):
                    # Delete from Snowflake
                    if selected_ann.get("ID"):
                        sf_success = delete_annotation_from_snowflake(annotation_id=selected_ann["ID"])
                        
                        # If has card ID, also delete from Domo
                        if selected_ann.get("CARD_ID") and sf_success:
                            delete_annotation_from_domo(str(selected_ann["CARD_ID"]), selected_ann["ID"])
                    else:
                        # Global annotation - delete by content and date
                        sf_success = delete_annotation_from_snowflake(
                            content=selected_ann["CONTENT"],
                            entry_date=str(selected_ann["ENTRY_DATE"])
                        )
                    
                    if sf_success:
                        st.success("Annotation deleted!")
                        # Refresh the list
                        st.session_state.delete_annotations = get_snowflake_annotations(
                            start_date=start_date.strftime("%Y-%m-%d"),
                            end_date=end_date.strftime("%Y-%m-%d")
                        )
                        st.rerun()
        elif "delete_annotations" in st.session_state:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📝</div>
                    <p>No annotations in this date range</p>
                </div>
            """, unsafe_allow_html=True)

st.write("")

# ==========================
# SYNC SECTION
# ==========================
with st.container(border=True):
    st.markdown("""<div class='label'>Sync Card 
        <span class="info-tooltip">ⓘ
            <span class="tooltiptext">סנכרון מדומו לסנופלייק. הוסיפו מזהי כרטיסים, בחרו טווח תאריכים ולחצו Sync. הערות חדשות יתווספו, הערות שהשתנו יעודכנו. לא מתבצעת מחיקה.</span>
        </span>
    </div>""", unsafe_allow_html=True)
    st.markdown(
        "<div class='desc'>Sync annotations from Domo to Snowflake for specific cards.</div>",
        unsafe_allow_html=True,
    )
    
    # Card IDs section
    st.markdown("<div class='tiny'>Card IDs</div>", unsafe_allow_html=True)
    
    # Preset cards dropdown
    preset_cards = get_preset_cards()
    preset_options = [""] + [f"{name} ({cid})" for cid, name in preset_cards.items()]
    
    col_sync_preset, col_sync_preset_btn = st.columns([3, 1])
    with col_sync_preset:
        selected_sync_preset = st.selectbox(
            "Common cards",
            options=preset_options,
            format_func=lambda x: "Select from common cards..." if x == "" else x,
            label_visibility="collapsed",
            key="sync_preset_card"
        )
    with col_sync_preset_btn:
        if st.button("+ Add", type="secondary", use_container_width=True, key="add_sync_preset_btn"):
            if selected_sync_preset:
                card_id_from_preset = selected_sync_preset.split("(")[-1].rstrip(")")
                if "sync_card_ids" not in st.session_state:
                    st.session_state.sync_card_ids = []
                if card_id_from_preset not in st.session_state.sync_card_ids:
                    st.session_state.sync_card_ids.append(card_id_from_preset)
                    st.rerun()
    
    # Manual entry
    col_sync_input, col_sync_btn = st.columns([3, 1])
    with col_sync_input:
        new_sync_card_id = st.text_input("Card ID", placeholder="Or enter card ID manually...", label_visibility="collapsed", key="new_sync_card_id")
    with col_sync_btn:
        if st.button("+ Add", type="secondary", use_container_width=True, key="add_sync_card"):
            if new_sync_card_id and new_sync_card_id.strip():
                card_id_clean = new_sync_card_id.strip()
                if "sync_card_ids" not in st.session_state:
                    st.session_state.sync_card_ids = []
                if card_id_clean not in st.session_state.sync_card_ids:
                    st.session_state.sync_card_ids.append(card_id_clean)
                    st.rerun()
    
    # Display selected card IDs using multiselect (allows removal by clicking X)
    if "sync_card_ids" not in st.session_state:
        st.session_state.sync_card_ids = []
    
    if st.session_state.sync_card_ids:
        selected_sync_cards = st.multiselect(
            "Selected cards",
            options=st.session_state.sync_card_ids,
            default=st.session_state.sync_card_ids,
            label_visibility="collapsed",
            key="sync_card_ids_display"
        )
        # Update session state if user removed any
        if set(selected_sync_cards) != set(st.session_state.sync_card_ids):
            st.session_state.sync_card_ids = selected_sync_cards
            st.rerun()
    
    # Date range for sync
    col_sync_start, col_sync_end, col_sync_action = st.columns([2, 2, 1])
    with col_sync_start:
        st.markdown("<div class='tiny'>From Date</div>", unsafe_allow_html=True)
        sync_start_date = st.date_input("Sync From", value=date.today() - timedelta(days=365), label_visibility="collapsed", key="sync_start")
    with col_sync_end:
        st.markdown("<div class='tiny'>To Date</div>", unsafe_allow_html=True)
        sync_end_date = st.date_input("Sync To", value=date.today(), label_visibility="collapsed", key="sync_end")
    with col_sync_action:
        st.markdown("<div class='tiny'>&nbsp;</div>", unsafe_allow_html=True)
        if st.button("⇄ Sync", type="primary", use_container_width=True):
            if st.session_state.sync_card_ids:
                with st.spinner("Syncing..."):
                    total_inserted = 0
                    total_updated = 0
                    total_skipped = 0
                    
                    for card_id in st.session_state.sync_card_ids:
                        results = sync_card_annotations(
                            card_id,
                            start_date=sync_start_date.strftime("%Y-%m-%d"),
                            end_date=sync_end_date.strftime("%Y-%m-%d")
                        )
                        total_inserted += results["inserted"]
                        total_updated += results["updated"]
                        total_skipped += results["skipped"]
                    
                    st.success(
                        f"Sync complete! Inserted: {total_inserted}, "
                        f"Updated: {total_updated}, "
                        f"Skipped: {total_skipped}"
                    )
            else:
                st.error("Please add at least one card ID")

st.write("")

# ==========================
# PUSH TO DOMO SECTION
# ==========================
with st.container(border=True):
    st.markdown("""<div class='label'>Push to Domo 
        <span class="info-tooltip">ⓘ
            <span class="tooltiptext">דחיפת הערות מסנופלייק לדומו. הוסיפו מזהי כרטיסי יעד, בחרו טווח תאריכים וצבעים (ריק = הכל), ולחצו Push. ההערות יתווספו לכל הכרטיסים שנבחרו.</span>
        </span>
    </div>""", unsafe_allow_html=True)
    st.markdown(
        "<div class='desc'>Insert Snowflake annotations into Domo cards.</div>",
        unsafe_allow_html=True,
    )
    
    # Card IDs section
    st.markdown("<div class='tiny'>Target Card IDs</div>", unsafe_allow_html=True)
    
    # Preset cards dropdown
    preset_cards = get_preset_cards()
    preset_options = [""] + [f"{name} ({cid})" for cid, name in preset_cards.items()]
    
    col_push_preset, col_push_preset_btn = st.columns([3, 1])
    with col_push_preset:
        selected_push_preset = st.selectbox(
            "Common cards",
            options=preset_options,
            format_func=lambda x: "Select from common cards..." if x == "" else x,
            label_visibility="collapsed",
            key="push_preset_card"
        )
    with col_push_preset_btn:
        if st.button("+ Add", type="secondary", use_container_width=True, key="add_push_preset_btn"):
            if selected_push_preset:
                card_id_from_preset = selected_push_preset.split("(")[-1].rstrip(")")
                if "push_card_ids" not in st.session_state:
                    st.session_state.push_card_ids = []
                if card_id_from_preset not in st.session_state.push_card_ids:
                    st.session_state.push_card_ids.append(card_id_from_preset)
                    st.rerun()
    
    # Manual entry
    col_push_input, col_push_btn = st.columns([3, 1])
    with col_push_input:
        new_push_card_id = st.text_input("Card ID", placeholder="Or enter card ID manually...", label_visibility="collapsed", key="new_push_card_id")
    with col_push_btn:
        if st.button("+ Add", type="secondary", use_container_width=True, key="add_push_card"):
            if new_push_card_id and new_push_card_id.strip():
                card_id_clean = new_push_card_id.strip()
                if "push_card_ids" not in st.session_state:
                    st.session_state.push_card_ids = []
                if card_id_clean not in st.session_state.push_card_ids:
                    st.session_state.push_card_ids.append(card_id_clean)
                    st.rerun()
    
    # Display selected card IDs using multiselect (allows removal by clicking X)
    if "push_card_ids" not in st.session_state:
        st.session_state.push_card_ids = []
    
    if st.session_state.push_card_ids:
        selected_push_cards = st.multiselect(
            "Selected cards",
            options=st.session_state.push_card_ids,
            default=st.session_state.push_card_ids,
            label_visibility="collapsed",
            key="push_card_ids_display"
        )
        # Update session state if user removed any
        if set(selected_push_cards) != set(st.session_state.push_card_ids):
            st.session_state.push_card_ids = selected_push_cards
            st.rerun()
    
    # Date range for push
    col_push_start, col_push_end = st.columns(2)
    with col_push_start:
        st.markdown("<div class='tiny'>From Date</div>", unsafe_allow_html=True)
        push_start_date = st.date_input("Push From", value=date.today() - timedelta(days=365), label_visibility="collapsed", key="push_start")
    with col_push_end:
        st.markdown("<div class='tiny'>To Date</div>", unsafe_allow_html=True)
        push_end_date = st.date_input("Push To", value=date.today(), label_visibility="collapsed", key="push_end")
    
    # Color filter (multiselect)
    st.markdown("<div class='tiny'>Colors (leave empty for all)</div>", unsafe_allow_html=True)
    selected_colors = st.multiselect(
        "Colors",
        options=list(ANNOTATION_COLORS.keys()),
        default=[],
        label_visibility="collapsed",
        key="push_colors"
    )
    
    # Convert color names to hex values
    color_hex_values = [ANNOTATION_COLORS[c] for c in selected_colors]
    
    if st.button("→ Push to Domo", type="primary", use_container_width=True):
        if st.session_state.push_card_ids:
            with st.spinner("Pushing annotations to Domo..."):
                total_pushed = 0
                total_failed = 0
                success_cards = []
                
                for card_id in st.session_state.push_card_ids:
                    results = push_to_domo(
                        card_id,
                        start_date=push_start_date.strftime("%Y-%m-%d"),
                        end_date=push_end_date.strftime("%Y-%m-%d"),
                        colors=color_hex_values
                    )
                    total_pushed += results["pushed"]
                    total_failed += results["failed"]
                    if results["pushed"] > 0:
                        success_cards.append(card_id)
                
                if total_pushed > 0:
                    st.success(f"Pushed {total_pushed} annotations to cards: {', '.join(success_cards)}")
                if total_failed > 0:
                    st.warning(f"Failed to push {total_failed} annotations")
                if total_pushed == 0 and total_failed == 0:
                    st.info("No annotations found matching the filters")
        else:
            st.error("Please add at least one card ID")

st.write("")

# ==========================
# VIEW ALL ANNOTATIONS
# ==========================
with st.container(border=True):
    col_header, col_toggle, col_refresh = st.columns([3, 1.5, 1])
    with col_header:
        st.markdown("""<div class='label'>All Annotations 
            <span class="info-tooltip">ⓘ
                <span class="tooltiptext">צפייה בכל ההערות מסנופלייק. סננו לפי תאריכים ולחצו Apply. ניתן לעבור בין תצוגת טבלה לציר זמן, לייצא ל-CSV ולרענן.</span>
            </span>
        </div>""", unsafe_allow_html=True)
        st.markdown(
            "<div class='desc'>View all annotations from Snowflake.</div>",
            unsafe_allow_html=True,
        )
    with col_toggle:
        view_mode = st.toggle("Timeline View", value=False)
    with col_refresh:
        if st.button("↻ Refresh", type="secondary", use_container_width=True, key="refresh_all"):
            st.session_state.all_annotations = get_snowflake_annotations()
            st.rerun()
    
    # Date filter
    col_filter_start, col_filter_end, col_filter_btn = st.columns([2, 2, 1])
    with col_filter_start:
        st.markdown("<div class='tiny'>From Date</div>", unsafe_allow_html=True)
        filter_start = st.date_input("From", value=date.today() - timedelta(days=365), label_visibility="collapsed", key="filter_start")
    with col_filter_end:
        st.markdown("<div class='tiny'>To Date</div>", unsafe_allow_html=True)
        filter_end = st.date_input("To", value=date.today(), label_visibility="collapsed", key="filter_end")
    with col_filter_btn:
        st.markdown("<div class='tiny'>&nbsp;</div>", unsafe_allow_html=True)
        if st.button("Apply", type="secondary", use_container_width=True, key="apply_filter"):
            st.session_state.all_annotations = get_snowflake_annotations(
                start_date=filter_start.strftime("%Y-%m-%d"),
                end_date=filter_end.strftime("%Y-%m-%d")
            )
            st.rerun()
    
    # Load annotations if not loaded
    if "all_annotations" not in st.session_state:
        st.session_state.all_annotations = get_snowflake_annotations()
    
    annotations = st.session_state.all_annotations
    
    if annotations:
        if view_mode:
            # Timeline View
            import plotly.graph_objects as go
            
            timeline_data = []
            for ann in annotations:
                date_str = ann.get("ENTRY_DATE")
                if date_str:
                    timeline_data.append({
                        "Date": str(date_str),
                        "Content": ann.get("CONTENT", ""),
                        "Color": ann.get("COLOR", "#72B0D7"),
                        "Card": f"Card {ann['CARD_ID']}" if ann.get("CARD_ID") else "Global",
                    })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                df_timeline["Date"] = pd.to_datetime(df_timeline["Date"])
                df_timeline = df_timeline.sort_values("Date")
                
                fig = go.Figure()
                
                for idx, row in df_timeline.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row["Date"]],
                        y=[0],
                        mode="markers+text",
                        marker=dict(
                            size=16,
                            color=row["Color"],
                            line=dict(width=2, color="white")
                        ),
                        text=[row["Content"][:20] + "..." if len(row["Content"]) > 20 else row["Content"]],
                        textposition="top center",
                        hovertemplate=(
                            f"<b>{row['Content']}</b><br>"
                            f"Date: {row['Date'].strftime('%Y-%m-%d')}<br>"
                            f"{row['Card']}<extra></extra>"
                        ),
                        showlegend=False
                    ))
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis=dict(title="", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
                    yaxis=dict(visible=False, range=[-0.5, 1]),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter")
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            # Table View
            df_data = []
            for ann in annotations:
                created_date = ann.get("CREATED_DATE")
                created_str = created_date.strftime("%Y-%m-%d %H:%M") if created_date else "—"
                
                df_data.append({
                    "Content": ann.get("CONTENT"),
                    "Date": str(ann.get("ENTRY_DATE", "—")),
                    "Color": COLOR_NAME_MAP.get(ann.get("COLOR"), ann.get("COLOR", "—")),
                    "Card ID": ann.get("CARD_ID") if ann.get("CARD_ID") else "Global",
                    "Created By": ann.get("DOMO_USER_NAME", "—"),
                    "Created": created_str,
                    "ID": ann.get("ID") if ann.get("ID") else "—",
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values("Date", ascending=False)
            
            # Export CSV button
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="🡻 Export CSV",
                data=csv,
                file_name=f"annotations_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="secondary"
            )
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Content": st.column_config.TextColumn("Content", width="large"),
                    "Date": st.column_config.TextColumn("Date", width="small"),
                    "Color": st.column_config.TextColumn("Color", width="small"),
                    "Card ID": st.column_config.TextColumn("Card ID", width="small"),
                    "Created By": st.column_config.TextColumn("Created By", width="medium"),
                    "Created": st.column_config.TextColumn("Created", width="medium"),
                    "ID": st.column_config.TextColumn("ID", width="small"),
                }
            )
    else:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <p>No annotations found</p>
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
