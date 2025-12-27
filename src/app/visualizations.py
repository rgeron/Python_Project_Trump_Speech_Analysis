
import streamlit as st
import plotly.express as px
import pandas as pd

def plot_time_series(df: pd.DataFrame):
    """Plots speeches per month."""
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    speeches_per_month = df.groupby('year_month').size().reset_index(name='count')
    
    fig = px.line(
        speeches_per_month, 
        x='year_month', 
        y='count', 
        title='Number of Speeches over Time',
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_word_frequency(df: pd.DataFrame, text_column: str, tracked_words: list):
    """Plots frequency of tracked words over time."""
    if not tracked_words:
        return

    st.markdown(f"### Frequency of: {', '.join(tracked_words)}")
    
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    tracker_data = []
    
    for word in tracked_words:
        pattern = f"(?i)\\b{word}\\b"
        df[f'count_{word}'] = df[text_column].str.count(pattern)
        daily_counts = df.groupby('year_month')[f'count_{word}'].sum().reset_index()
        daily_counts['word'] = word
        # Rename for concatenation
        daily_counts = daily_counts.rename(columns={f'count_{word}': 'count'})
        tracker_data.append(daily_counts)
        
    if tracker_data:
        df_tracker = pd.concat(tracker_data)
        fig = px.line(
            df_tracker,
            x='year_month',
            y='count',
            color='word',
            title='Word Frequency over Time',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

def plot_top_locations(df: pd.DataFrame):
    """Plots top 15 locations."""
    top_locs = df['location'].value_counts().head(15).reset_index()
    top_locs.columns = ['location', 'count']
    fig = px.bar(top_locs, x='count', y='location', orientation='h', title='Top 15 Locations')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

def plot_speech_length(df: pd.DataFrame, text_column: str):
    """Plots speech length vs date."""
    df['word_count'] = df[text_column].apply(lambda x: len(str(x).split()))
    # Convert categories to string for plotting (lists are unhashable)
    df_plot = df.copy()
    df_plot['categories_str'] = df_plot['categories'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    
    fig = px.scatter(
        df_plot, 
        x='date', 
        y='word_count', 
        color='categories_str',
        title='Speech Length (Word Count) Distribution',
        hover_data=['title', 'location']
    )
    st.plotly_chart(fig, use_container_width=True)
