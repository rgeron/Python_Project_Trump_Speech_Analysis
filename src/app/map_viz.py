
import streamlit as st
import plotly.express as px
import pandas as pd

def render_map(df: pd.DataFrame):
    """
    Renders a US choropleth map showing the number of speeches per state.
    
    Args:
        df (pd.DataFrame): The filtered dataframe containing 'location' column.
    """
    if df.empty:
        st.warning("No data available for map.")
        return

    # Extract State Code from 'location' (Format: "Town, STATE")
    # We assume standard "XX" format at the end of the string.
    # Note: "Abroad" and "Unknown" will not match this and be excluded from US map.
    def get_state(loc):
        if not isinstance(loc, str): return None
        if ',' in loc:
            parts = loc.split(',')
            candidate = parts[-1].strip()
            if len(candidate) == 2 and candidate.isupper():
                return candidate
        # Fallback: maybe the location IS the state code?
        if len(loc) == 2 and loc.isupper():
            return loc
        return None

    df_map = df.copy()
    df_map['state'] = df_map['location'].apply(get_state)
    
    # Filter out null states (Foreign, Unknown)
    df_us = df_map[df_map['state'].notna()]
    
    if df_us.empty:
        st.info("No US locations found in the current selection.")
        return

    # Aggregate count
    state_counts = df_us['state'].value_counts().reset_index()
    state_counts.columns = ['state', 'count']

    # Create Choropleth
    fig = px.choropleth(
        state_counts,
        locations='state',
        locationmode="USA-states",
        color='count',
        scope="usa",
        color_continuous_scale="Reds",
        title=f"Speeches by State ({df_us.shape[0]} total)",
        labels={'count': 'Number of Speeches'}
    )
    
    fig.update_layout(
        geo_scope='usa',
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)
