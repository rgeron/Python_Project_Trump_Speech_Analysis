
import sqlite3

def store_urls(urls, db_path="data/speeches.db"):
    conn = sqlite3.connect(db_path)
    for url in urls:
        conn.execute("INSERT OR IGNORE INTO Speeches (url) VALUES (?)", (url,))

    conn.commit()
    conn.close()
