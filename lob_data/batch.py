# =============================================================
# ingest/batch.py
# =============================================================
"""
Loads the raw BitMEX XBTUSD file 
and transforms its format into 
a long Feather format using ingestion (ingestion.py).
"""

from pathlib import Path
import subprocess

# Set up directories
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/replay")

# Create directories if they do not exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Process each raw file
for file in RAW_DIR.glob("XBTUSD_*.csv"):

    # Extract date from filename and construct output filename
    date_str = file.stem.split("_")[1].replace("-", "")
    out_file = OUT_DIR / f"{date_str}.feather"

    # Skip if output file already exists
    if out_file.exists():
        print(f"{out_file.name} already exist, skip.")
        continue

    # Run ingestion script using subprocess
    print(f"Processing: {file.name}: {out_file.name}")
    subprocess.run([
        "python", "lob_data/ingestion.py",
        "--input", str(file),
        "--output", str(out_file)
    ])