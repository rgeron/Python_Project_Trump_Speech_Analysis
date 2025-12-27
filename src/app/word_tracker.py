import streamlit as st
import pandas as pd
import plotly.express as px
import re

def render_word_tracker(df: pd.DataFrame, text_column: str):
    """
    Renders the Word Tracker tab content.
    
    Args:
        df: The filtered dataframe.
        text_column: The column containing text to analyze.
    """
    st.markdown("### Word Tracker")
    
    # 1. Inputs
    word_tracker_input = st.text_input("Enter words to track (comma separated)", value="")
    tracked_words = [w.strip() for w in word_tracker_input.split(',') if w.strip()]
    
    if not tracked_words:
        st.info("Enter words above to see their frequency over time.")
        return

    # 2. Global statistics for tracked words
    st.markdown("#### Global Statistics")
    stats_data = []
    
    # Pre-calculate counts to avoid re-calculating for stats and chart separately if possible,
    # but for simplicity we'll do it per word.
    
    for word in tracked_words:
        # Use simple regex for word boundary
        pattern = f"(?i)\\b{word}\\b"
        total_count = df[text_column].str.count(pattern).sum()
        speeches_with_word = df[df[text_column].str.contains(pattern,  regex=True)].shape[0]
        stats_data.append({
            "Word": word,
            "Total Occurrences": total_count,
            "Speeches Containing Word": speeches_with_word,
            "% of Speeches": f"{(speeches_with_word / len(df) * 100):.1f}%"
        })
        
    st.dataframe(pd.DataFrame(stats_data))

    # 3. Frequency Over Time Graph
    st.markdown("#### Frequency Over Time")
    
    # Prepare data for time series
    df_chart = df.copy()
    df_chart['year_month'] = df_chart['date'].dt.to_period('M').astype(str)
    
    chart_data = []
    for word in tracked_words:
        pattern = f"(?i)\\b{word}\\b"
        df_chart[f'count_{word}'] = df_chart[text_column].str.count(pattern)
        
        # Group by month
        monthly = df_chart.groupby('year_month')[f'count_{word}'].sum().reset_index()
        monthly.columns = ['year_month', 'count']
        monthly['word'] = word
        chart_data.append(monthly)
        
    if chart_data:
        final_chart_df = pd.concat(chart_data)
        fig = px.line(
            final_chart_df,
            x='year_month',
            y='count',
            color='word',
            title='Monthly Frequency of Tracked Words',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    # 4. Specific Word Inspection (Context)
    st.markdown("#### Word Inspection / Concordance")
    selected_word = st.selectbox("Select a word to inspect", tracked_words)
    
    if selected_word:
        # Filter speeches that contain the word
        pattern = f"(?i)\\b{selected_word}\\b"
        search_results = df[df[text_column].str.contains(pattern, regex=True)].copy()
        
        if search_results.empty:
            st.warning(f"No speeches found containing '{selected_word}'.")
        else:
            st.write(f"Found {len(search_results)} speeches containing **{selected_word}**.")
            
            # Allow user to pick a speech to see context
            speech_option = st.selectbox(
                "Select a speech to view mentions",
                search_results['label'].unique()
            )
            
            if speech_option:
                speech_row = search_results[search_results['label'] == speech_option].iloc[0]
                text = speech_row[text_column]
                
                # Highlight the word in the text (simple bolding)
                # Note: This simple replace might break case sensitivity visualization nicely, 
                # but good enough for MVP. 
                # Better approach: use regex sub with keeping case if desired, or just simple markdown.
                
                highlighted_text = re.sub(
                    f"({selected_word})", 
                    r"**\1**", 
                    text, 
                    flags=re.IGNORECASE
                )
                
                st.markdown(f"**Date:** {speech_row['date'].date()} | **Location:** {speech_row['location']}")
                # Show snippets or full text. Let's show a scrollable box.
                st.markdown("---")
                st.markdown(highlighted_text)
