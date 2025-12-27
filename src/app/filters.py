
import streamlit as st
import pandas as pd
from typing import Tuple, List, Optional
import datetime

# --- Constants ---
WEST_COAST = ["CA", "OR", "WA"]
EAST_COAST = ["ME", "NH", "MA", "RI", "CT", "NY", "NJ", "DE", "MD", "VA", "NC", "SC", "GA", "FL"]
NON_CONTIGUOUS = ["AK", "HI"]

BLUE_STATES = [
    "CA", "OR", "WA", "NV", "AZ", "NM", "CO",
    "MN", "IL", "MI", "WI",
    "NY", "VT", "ME", "MA", "RI", "CT",
    "NJ", "DE", "MD", "DC", "HI", "VA"
]

RED_STATES = [
    "ID", "MT", "WY", "UT",
    "ND", "SD", "NE", "KS", "OK",
    "TX", "MO", "AR", "LA",
    "IN", "KY", "TN", "MS", "AL",
    "WV", "SC", "AK"
]

SWING_STATES = ["PA", "GA", "NC", "FL", "OH", "IA"]

# Comprehensive list of US State Codes for validation
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
}

def render_filters(df: pd.DataFrame, available_text_columns: List[str]) -> Tuple[pd.DataFrame, str]:
    """
    Renders the sidebar filters and returns the filtered dataframe and selected text column.
    
    Args:
        df: The initial dataframe.
        available_text_columns: List of columns available for text analysis.
        
    Returns:
        tuple: (filtered_df, selected_text_column, banned_words)
    """
    st.sidebar.title("Filters")

    # --- 1. Text Version Selector ---
    allowed_columns = ['text', 'text_basic', 'text_no_stopwords', 'text_lemmatized']
    available_options = [col for col in allowed_columns if col in df.columns]
    
    # Fallback if none of the preferred columns are found (shouldn't happen with correct data)
    if not available_options:
        available_options = [col for col in available_text_columns if col in df.columns]

    text_column = st.sidebar.radio(
        "Analysis Text",
        options=available_options,
        index=available_options.index('clean_v1') if 'clean_v1' in available_options else 0
    )
    
    # --- 1.5 Banned Words ---
    banned_words_input = st.sidebar.text_area("Words to Ban (comma separated)", placeholder="e.g. applause, cheers")
    banned_words = [word.strip() for word in banned_words_input.split(',')] if banned_words_input else []

    # --- 2. Date Filters (Pills) ---
    st.sidebar.subheader("Date Range")
    
    date_options = ["All Time", "Last 3 Years", "After 2013"]
    selected_date_preset = st.sidebar.pills("Select Period", date_options, default="All Time")
    
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    start_date = min_date
    end_date = max_date
    
    if selected_date_preset == "Last 3 Years":
        start_date = max_date - datetime.timedelta(days=365*3)
    elif selected_date_preset == "After 2013":
        start_date = datetime.date(2014, 1, 1)
    
    # Filter by date immediately to influence downstream counts if needed
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    
    # --- 3. Category Filter ---
    st.sidebar.subheader("Categories")
    
    # Import category groups
    from src.app.category_mapping import CATEGORY_GROUPS
    
    # --- Category Groups ---
    group_options = sorted(list(CATEGORY_GROUPS.keys()))
    selected_groups = st.sidebar.multiselect(
        "Select Category Groups",
        options=group_options,
        default=[],
        placeholder="All Groups"
    )

    # Resolve categories from selected groups
    categories_from_groups = set()
    for group in selected_groups:
        categories_from_groups.update(CATEGORY_GROUPS.get(group, []))

    # --- Individual Categories ---
    all_categories = sorted(list(set([item for sublist in df['categories'] for item in sublist])))
    
    selected_categories = st.sidebar.multiselect(
        "Select Specific Categories",
        options=all_categories,
        default=[],
        placeholder="All Categories"
    )

    # Combine categories from groups and individually selected categories
    # If BOTH are empty, we show everything (no filter).
    # If EITHER is selected, we filter for the union of them.
    
    final_selected_categories = categories_from_groups.union(set(selected_categories))
    
    if final_selected_categories:
        mask = mask & df['categories'].apply(lambda x: any(cat in final_selected_categories for cat in x))


    # --- 4. Location Filters (Pills) ---
    st.sidebar.subheader("Location")
    
    location_options = [
        "All", "West Coast", "East Coast", "Middle State", "Non Contiguous", 
        "Blue State", "Red State", "Swing State", "Abroad"
    ]
    selected_location_preset = st.sidebar.pills("Select Region", location_options, default="All")

    if selected_location_preset != "All":
        # Logic to filter based on preset
        def filter_location(loc_str):
            if not isinstance(loc_str, str): return False
            loc_str = loc_str.strip()
            
            # --- Logic to identify State ---
            state = None
            
            # Case 1: "City, STATE" format
            parts = loc_str.split(",")
            if len(parts) > 1:
                possible_state = parts[-1].strip().upper()
                if possible_state in US_STATES:
                    state = possible_state
            
            # Case 2: Just "STATE" code (e.g. "WA", "FL")
            elif loc_str.upper() in US_STATES:
                state = loc_str.upper()
            
            # --- Preset Logic ---
            
            if selected_location_preset == "Abroad":
                # Identified as Abroad if it is NOT a US state location and NOT 'Unknown'
                if state: return False
                if loc_str == "Unknown": return False 
                return True

            # For US-based regions, we need a valid US state
            if not state: return False
            
            if selected_location_preset == "West Coast":
                return state in WEST_COAST
            elif selected_location_preset == "East Coast":
                return state in EAST_COAST
            elif selected_location_preset == "Non Contiguous":
                return state in NON_CONTIGUOUS
            elif selected_location_preset == "Middle State":
                return (state not in WEST_COAST) and \
                       (state not in EAST_COAST) and \
                       (state not in NON_CONTIGUOUS)
            elif selected_location_preset == "Blue State":
                return state in BLUE_STATES
            elif selected_location_preset == "Red State":
                return state in RED_STATES
            elif selected_location_preset == "Swing State":
                return state in SWING_STATES
            
            return True

        mask = mask & df['location'].apply(filter_location)

    df_filtered = df[mask].copy()
    
    return df_filtered, text_column, banned_words
