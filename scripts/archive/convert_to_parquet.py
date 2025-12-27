import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from parquet.convert import convert_sqlite_to_parquet

if __name__ == "__main__":
    print("Converting SQLite database to Parquet...")
    convert_sqlite_to_parquet()
    print("Conversion complete. Parquet files saved in data/ directory.")
