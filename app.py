
import streamlit as st
from src.app.data import load_data, ANALYSIS_COLUMNS
from src.app.filters import render_filters
import src.app.visualizations as viz
import src.app.analysis as nlp
import src.app.map_viz as map_viz
import src.app.word_tracker as word_tracker

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Trump Speech Analyzer")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Filters ---
df_filtered, text_column, banned_words = render_filters(df, ANALYSIS_COLUMNS)

if df_filtered.empty:
    st.warning("No speeches found with the current filters. Please adjust your selection.")
    st.stop()

# --- Main Dashboard ---
st.title("Donald Trump Speech Analysis")

tab1, tab2, tab5, tab3, tab4 = st.tabs(["Overview & Evolution", "N-Gram & Analysis", "Word Tracker", "Speech Inspector", "Map"])

# --- Tab 1: Overview & Evolution ---
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Speeches", len(df_filtered))
    
    # Calculate approx lexical richness or just total words
    total_words = df_filtered[text_column].apply(lambda x: len(str(x).split())).sum()
    col2.metric("Total Words (Approx)", f"{total_words:,}")
    
    col3.metric("Date Range", f"{df_filtered['date'].min().date()} to {df_filtered['date'].max().date()}")

    st.markdown("### Temporal Evolution")
    viz.plot_time_series(df_filtered)
    # viz.plot_word_frequency(df_filtered, text_column, tracked_words) # Moved to separate tab
    
    col_geo, col_len = st.columns(2)
    with col_geo:
        st.markdown("### Top Locations")
        viz.plot_top_locations(df_filtered)
        
    with col_len:
        st.markdown("### Speech Length vs Date")
        viz.plot_speech_length(df_filtered, text_column)

# --- Tab 2: NLP Analysis ---
with tab2:
    st.markdown(f"### Analysis based on: **{text_column}**")
    
    text_data = df_filtered[text_column].dropna().astype(str).tolist()
    
    if not text_data:
        st.warning("No text data available for analysis.")
    else:
        col_ngram1, col_ngram2 = st.columns(2)
        with col_ngram1:
            nlp.plot_top_ngrams(text_data, n=1, title="Top 20 Unigrams", banned_words=banned_words)
        with col_ngram2:
            nlp.plot_top_ngrams(text_data, n=2, title="Top 20 Bigrams", banned_words=banned_words) # or use n=3 or allow user to toggle
        
        st.markdown("#### Word Cloud")
        nlp.render_wordcloud(text_data, banned_words=banned_words)

# --- Tab 5: Word Tracker ---
with tab5:
    word_tracker.render_word_tracker(df_filtered, text_column)

# --- Tab 3: Speech Inspector ---
with tab3:
    st.markdown("### Inspect Individual Speeches")
    
    selected_label = st.selectbox("Choose a speech", df_filtered['label'].unique())
    
    if selected_label:
        speech_row = df_filtered[df_filtered['label'] == selected_label].iloc[0]
        
        st.markdown("#### Metadata")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.info(f"**Date:** {speech_row['date'].date()}")
        m_col2.info(f"**Location:** {speech_row['location']}")
        m_col3.info(f"**Category:** {speech_row['categories']}")
        
        st.markdown(f"#### Full Text ({text_column})")
        st.text_area("Content", speech_row[text_column], height=400)

# --- Tab 4: Map ---
with tab4:
    st.markdown("### Geographic Distribution")
    map_viz.render_map(df_filtered)
