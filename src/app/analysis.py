
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS

def plot_top_ngrams(text_data: list, n: int = 1, top_k: int = 20, title: str = "Top Words", banned_words: list = None):
    """
    Plots top n-grams.
    
    Args:
        text_data: List of strings.
        n: N-gram size (1 for unigrams, 2 for bigrams, etc).
        top_k: Number of items to show.
        title: Chart title.
        banned_words: List of words to exclude.
    """
    try:
        stop_words = list(ENGLISH_STOP_WORDS)
        if banned_words:
            stop_words.extend(banned_words)

        if n == 1:
            vec = CountVectorizer(stop_words=stop_words, max_features=top_k)
        else:
            vec = CountVectorizer(ngram_range=(n, n), stop_words=stop_words, max_features=top_k)
            
        bow = vec.fit_transform(text_data)
        sum_words = bow.sum(axis=0)
        words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        df_ngram = pd.DataFrame(words_freq, columns=['term', 'count'])
        
        fig = px.bar(df_ngram, x='count', y='term', orientation='h', title=title)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    except ValueError:
        st.warning(f"Not enough text for {n}-gram analysis.")

def render_wordcloud(text_data: list, banned_words: list = None):
    """Renders a word cloud."""
    try:
        full_text = " ".join(text_data)
        if not full_text.strip():
            st.warning("No text to generate WordCloud.")
            return

        stopwords = set(STOPWORDS)
        if banned_words:
            stopwords.update(banned_words)

        wc = WordCloud(width=800, height=400, background_color='white', max_words=100, stopwords=stopwords).generate(full_text)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Could not generate word cloud: {e}")
