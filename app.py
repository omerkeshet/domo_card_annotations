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
# CONFIGURATION FROM SECRETS
# ==========================
# These values come from Streamlit Cloud secrets
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
    
    # Extract dataSourceId from the columns metadata (it's called "sourceId" in columns)
    data_source_id = None
    columns = fetched.get("columns", [])
    if columns and len(columns) > 0:
        data_source_id = columns[0].get("sourceId")
    
    # Add dataSourceId to each subscription (required for save)
    if data_source_id:
        subscriptions = fetched.get("definition", {}).get("subscriptions", {})
        for sub_name, sub_def in subscriptions.items():
            if "dataSourceId" not in sub_def:
                sub_def["dataSourceId"] = data_source_id
    
    # Store the dataSourceId for later use
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
    
    # Get the dataSourceId
    data_source_id = card_def.get("_dataSourceId")
    if not data_source_id:
        columns = card_def.get("columns", [])
        if columns and len(columns) > 0:
            data_source_id = columns[0].get("sourceId")
    
    # Get the definition
    definition = card_def.get("definition", {})
    
    # Get title from definition
    title = definition.get("title", "")
    
    # Convert 'title' to 'dynamicTitle' format if needed
    if "dynamicTitle" not in definition:
        definition["dynamicTitle"] = {
            "text": [{"text": title, "type": "TEXT"}] if title else []
        }
    
    # Add dynamicDescription if missing
    if "dynamicDescription" not in definition:
        definition["dynamicDescription"] = {
            "text": [],
            "displayOnCardDetails": True
        }
    
    # Add description if missing
    if "description" not in definition:
        definition["description"] = ""
    
    # Add controls if missing
    if "controls" not in definition:
        definition["controls"] = []
    
    # Set up annotations
    if new_annotations is None:
        new_annotations = []
    if deleted_annotation_ids is None:
        deleted_annotation_ids = []
    
    # Format new annotations
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
    
    # Convert formulas to save format
    definition["formulas"] = {
        "dsUpdated": [],
        "dsDeleted": [],
        "card": []
    }
    
    # Convert conditionalFormats to save format
    definition["conditionalFormats"] = {
        "card": [],
        "datasource": []
    }
    
    # Convert segments to save format
    if "segments" in definition:
        segments = definition["segments"]
        if isinstance(segments, dict) and "active" in segments and "definitions" in segments:
            definition["segments"] = {
                "active": segments.get("active", []),
                "create": [],
                "update": [],
                "delete": []
            }
    
    # Build the payload
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
    return card_def.get("definition", {}).get("title", "Unknown")


# ==========================
# STREAMLIT APP
# ==========================
st.set_page_config(
    page_title="Domo Annotations Manager",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Domo Card Annotations Manager")
st.markdown("Add and delete annotations on Domo cards")

# Main content
st.header("🔍 Load Card")

card_id = st.text_input("Card ID", placeholder="e.g., 19344562")

if st.button("Load Card", type="primary"):
    if not card_id:
        st.error("Please enter a Card ID")
    else:
        with st.spinner("Loading card..."):
            try:
                card_def = fetch_kpi_definition(DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id)
                st.session_state.card_def = card_def
                st.session_state.card_id = card_id
                st.success(f"✅ Loaded card: **{get_card_title(card_def)}**")
            except Exception as e:
                st.error(f"❌ Error loading card: {str(e)}")

# Show card content if loaded
if "card_def" in st.session_state and "card_id" in st.session_state:
    card_def = st.session_state.card_def
    card_id = st.session_state.card_id
    
    st.divider()
    
    # Create two columns for Add and Delete
    col1, col2 = st.columns(2)
    
    # ==========================
    # ADD ANNOTATION
    # ==========================
    with col1:
        st.header("➕ Add Annotation")
        
        with st.form("add_annotation_form"):
            annotation_text = st.text_area(
                "Annotation Text",
                placeholder="Enter your annotation text here...",
                height=100
            )
            
            annotation_date = st.date_input(
                "Annotation Date",
                value=date.today()
            )
            
            color_name = st.selectbox(
                "Color",
                options=list(ANNOTATION_COLORS.keys()),
                index=0
            )
            
            submit_add = st.form_submit_button("Add Annotation", type="primary")
            
            if submit_add:
                if not annotation_text:
                    st.error("Please enter annotation text")
                else:
                    with st.spinner("Adding annotation..."):
                        try:
                            new_annotation = {
                                "content": annotation_text,
                                "dataPoint": {"point1": annotation_date.strftime("%Y-%m-%d")},
                                "color": ANNOTATION_COLORS[color_name],
                            }
                            
                            result = save_card_definition(
                                DOMO_INSTANCE, 
                                DOMO_DEVELOPER_TOKEN, 
                                card_id, 
                                card_def,
                                new_annotations=[new_annotation]
                            )
                            
                            st.success(f"✅ Annotation added: '{annotation_text}' on {annotation_date}")
                            
                            # Reload card to refresh annotations
                            st.session_state.card_def = fetch_kpi_definition(
                                DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id
                            )
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error adding annotation: {str(e)}")
    
    # ==========================
    # DELETE ANNOTATION
    # ==========================
    with col2:
        st.header("🗑️ Delete Annotation")
        
        annotations = get_annotations(card_def)
        
        if annotations:
            # Create a selection box with annotation info
            annotation_options = {
                f"{ann['id']} - {ann['content'][:50]}{'...' if len(ann['content']) > 50 else ''} ({ann['dataPoint'].get('point1', 'N/A')})": ann['id']
                for ann in annotations
            }
            
            selected_annotation = st.selectbox(
                "Select Annotation to Delete",
                options=list(annotation_options.keys())
            )
            
            if st.button("Delete Annotation", type="secondary"):
                annotation_id = annotation_options[selected_annotation]
                
                with st.spinner("Deleting annotation..."):
                    try:
                        result = save_card_definition(
                            DOMO_INSTANCE, 
                            DOMO_DEVELOPER_TOKEN, 
                            card_id, 
                            card_def,
                            deleted_annotation_ids=[annotation_id]
                        )
                        
                        st.success(f"✅ Deleted annotation ID: {annotation_id}")
                        
                        # Reload card to refresh annotations
                        st.session_state.card_def = fetch_kpi_definition(
                            DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id
                        )
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error deleting annotation: {str(e)}")
        else:
            st.info("No annotations on this card")
    
    # ==========================
    # CURRENT ANNOTATIONS TABLE
    # ==========================
    st.divider()
    st.header("📋 Current Annotations")
    
    if st.button("🔄 Refresh"):
        with st.spinner("Refreshing..."):
            st.session_state.card_def = fetch_kpi_definition(
                DOMO_INSTANCE, DOMO_DEVELOPER_TOKEN, card_id
            )
            st.rerun()
    
    annotations = get_annotations(st.session_state.card_def)
    
    if annotations:
        # Create a clean dataframe for display
        df_data = []
        for ann in annotations:
            df_data.append({
                "ID": ann.get("id"),
                "Content": ann.get("content"),
                "Date": ann.get("dataPoint", {}).get("point1", "N/A"),
                "Color": ann.get("color"),
                "Created By": ann.get("userName", "Unknown"),
                "Created At": datetime.fromtimestamp(
                    ann.get("createdDate", 0) / 1000
                ).strftime("%Y-%m-%d %H:%M") if ann.get("createdDate") else "N/A"
            })
        
        df = pd.DataFrame(df_data)
        
        # Display with color indicators
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", format="%d"),
                "Content": st.column_config.TextColumn("Content", width="large"),
                "Date": st.column_config.TextColumn("Date"),
                "Color": st.column_config.TextColumn("Color"),
                "Created By": st.column_config.TextColumn("Created By"),
                "Created At": st.column_config.TextColumn("Created At"),
            }
        )
        
        st.caption(f"Total: {len(annotations)} annotations")
    else:
        st.info("No annotations found on this card")

# Footer
st.divider()
st.caption("Domo Annotations Manager | Built with Streamlit")
