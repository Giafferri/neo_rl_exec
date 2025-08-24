# =============================================================
# ingest/ingestion.py
# =============================================================
"""
Loads the raw BitMEX XBTUSD file and converts its format to long Feather :

    timestamp_ns | side | level | midpoint_USD | distance_to_mid | notional_USD | size_BTC |
    cancel_notional_USD | limit_notional_USD | market_notional_USD

We now persist only the midpoint and the relative distance per level (no `price_USD` stored).
Prices can still be reconstructed on the fly if needed as:

    price_USD = midpoint_USD * (1 + distance_to_mid)

The data in cancel_notional_USD, limit_notional_USD, and market_notional_USD columns cannot be utilized to rebuild the order book,
because they are not cumulative and do not represent the total notional at each level. They should be used as features in a RL model.
"""

from __future__ import annotations
import click
import pandas as pd
from pathlib import Path

def normalise_lob(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise the raw LOB data into a long format.
    Args:
        df_raw (pd.DataFrame): Raw LOB data with columns like 'timestamp_ns', 'bids_distance_0', 'asks_distance_0', etc.
    Returns:
        pd.DataFrame: Normalised LOB data in long format with columns:
            'timestamp_ns', 'side', 'level', 'midpoint_USD', 'distance_to_mid', 'notional_USD', 'size_BTC',
            'cancel_notional_USD', 'limit_notional_USD', 'market_notional_USD'
    """
    df = df_raw.copy()

    # Define timestamp as nanoseconds since epoch
    df["timestamp_ns"] = (
        pd.to_datetime(df["timestamp_ns"], utc=True, format="ISO8601").astype("int64")
    )

    # Sort by timestamp and remove duplicates
    df = df.sort_values("timestamp_ns").drop_duplicates("timestamp_ns")

    # passage en format vertical long  (20 × 2 = 40 lignes / snapshot)
    records: list[dict] = []
    for _, row in df.iterrows():
        ts = int(row["timestamp_ns"])
        for side in ("bids", "asks"):
            for lvl in range(20):
                # Distance from midpoint and midpoint value
                dist = float(row[f"{side}_distance_{lvl}"])
                mid = float(row["midpoint"])

                # Price at this level reconstructed from (midpoint × (1 + distance))
                price = mid * (1.0 + dist)
                
                # Notional USD at this level
                notional_usd = float(row[f"{side}_notional_{lvl}"])

                # Size in BTC at this level (notional / price)
                size_btc = notional_usd / price

                # Cancel notional USD at this level
                cancel_notional_usd = float(row[f"{side}_cancel_notional_{lvl}"])

                # Limit notional USD at this level
                limit_notional_usd = float(row[f"{side}_limit_notional_{lvl}"])

                # Market notional USD at this level
                market_notional_usd = float(row[f"{side}_market_notional_{lvl}"])

                # Records data for this level
                records.append(
                    dict(
                        timestamp_ns=ts,
                        side="BID" if side == "bids" else "ASK",
                        level=lvl,
                        midpoint_USD=mid,
                        distance_to_mid=dist,
                        notional_USD=notional_usd,
                        size_BTC=size_btc,
                        cancel_notional_USD=cancel_notional_usd,
                        limit_notional_USD=limit_notional_usd,
                        market_notional_USD=market_notional_usd,
                    )
                )

    # Create the new DataFrame from records
    df_long = pd.DataFrame.from_records(records)

    # Reorder columns to the desired schema
    df_long = df_long[
        [
            "timestamp_ns",
            "side",
            "level",
            "midpoint_USD",
            "distance_to_mid",
            "notional_USD",
            "size_BTC",
            "cancel_notional_USD",
            "limit_notional_USD",
            "market_notional_USD",
        ]
    ]

    # Ensure that size is not NaN
    assert df_long["size_BTC"].notna().all()

    # Ensure that notional is not NaN
    assert df_long["notional_USD"].notna().all()

    # Ensure that notional is not NaN
    assert df_long["cancel_notional_USD"].notna().all()

    # Ensure that notional is not NaN
    assert df_long["limit_notional_USD"].notna().all()

    # Ensure that notional is not NaN
    assert df_long["market_notional_USD"].notna().all()

    # Ensure that midpoint and distance are not NaN
    assert df_long["midpoint_USD"].notna().all()
    assert df_long["distance_to_mid"].notna().all()

    # Ensure that timestamp is monotonic increasing
    assert df_long["timestamp_ns"].is_monotonic_increasing

    return df_long

# =============================================================
# Main function to read raw data and save it in long format
# =============================================================
@click.command()
@click.option("--input",  "-i", type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=click.Path(), required=True)
def main(input: str, output: str):
    print(f"Reading {input}")
    df_raw = pd.read_csv(input)

    # Ensure first column is named 'timestamp_ns'
    if df_raw.columns[0].startswith("Unnamed") or df_raw.columns[0].startswith("system_time"):
        df_raw = df_raw.rename(columns={df_raw.columns[0]: "timestamp_ns"})

    # Transform raw data into long format
    print("Transforming LOB data into long format...")
    df_long = normalise_lob(df_raw)

    # Save transformed DataFrame to Feather format
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_long.to_feather(out_path)
    print(f"Feather here : {out_path}")

# =============================================================
# Entry point for the script
# =============================================================
if __name__ == "__main__":
    main()