import sys,os
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))
from rollcall.url_soupper import url_soupper
from rollcall.speech_decomposer import (get_title, get_date, get_cleaned_categories, get_nbr_sentences_nbr_words_nbr_seconds, get_candidate_transcriptions)
from rollcall.speeches_db import add_speech_to_parquet
import sqlite3
import json
import argparse

def process_speeches():
    parser = argparse.ArgumentParser(description='Process speeches for a candidate.')
    parser.add_argument('--candidate', type=str, default='trump', choices=['trump', 'harris', 'biden'], help='Candidate to process (trump, harris, or biden)')
    args = parser.parse_args()

    candidate = args.candidate.lower()
    
    if candidate == 'trump':
        db_path = "data/speeches.db"
        parquet_prefix = ""
        candidate_last_name = "Trump"
        candidate_full_name = "Donald Trump"
        person_name = "Donald Trump"
    elif candidate == 'harris':
        db_path = "data/other_candidate.db"
        parquet_prefix = "other_"
        candidate_last_name = "Harris"
        candidate_full_name = "Kamala Harris"
        person_name = "Kamala Harris"
    elif candidate == 'biden':
        db_path = "data/other_candidate.db"
        parquet_prefix = "other_"
        candidate_last_name = "Biden"
        candidate_full_name = "Joe Biden"
        person_name = "Joe Biden"
    else:
        print(f"Unknown candidate: {candidate}")
        return

    print(f"Processing speeches for {candidate} from {db_path}")

    conn=sqlite3.connect(db_path)
    cur=conn.cursor()
    # Filter by candidate name in URL to avoid mixing candidates in shared DB
    rows=cur.execute("Select id, url from Speeches where title is NULL AND url LIKE ?", (f'%/{candidate}/%',)).fetchall()
    for id, url in rows:
        print(url)
        soup=url_soupper(url)
        title=get_title(soup)
        date=get_date(soup)
        nbr_sentences, nbr_words, nbr_seconds = get_nbr_sentences_nbr_words_nbr_seconds(soup, candidate_last_name)
        categories=get_cleaned_categories(soup)
        categories_str = json.dumps(categories, ensure_ascii=False)
        candidate_transcript=get_candidate_transcriptions(soup, candidate_full_name)

        cur.execute(""" Update Speeches Set title=?, date=?, nbr_sentences=?, nbr_words=?, nbr_seconds=?,categories=?, person_name=? where id=?""", (title, date, nbr_sentences, nbr_words, nbr_seconds, categories_str, person_name, id))
        
        transcription_data_list = []
        for transcription in candidate_transcript:
            cur.execute("""
            INSERT INTO Transcriptions (speech_id, timestamp, text)
            VALUES (?, ?, ?);
        """, (id, transcription[0], transcription[1]))
            transcription_id = cur.lastrowid
            
            transcription_data_list.append({
                "id": transcription_id,
                "speech_id": id,
                "timestamp": transcription[0],
                "text": transcription[1],
                "duration": None, 
                "person_name": person_name
            })
        conn.commit()
        
        # Add to Parquet
        speech_data = {
            "id": id,
            "url": url,
            "title": title,
            "date": date,
            "nbr_sentences": nbr_sentences,
            "nbr_words": nbr_words,
            "nbr_seconds": nbr_seconds,
            "categories": categories_str,
            "person_name": person_name
        }
            
        add_speech_to_parquet(speech_data, transcription_data_list, file_prefix=parquet_prefix)
        
    conn.close()

if __name__=='__main__':
    process_speeches()