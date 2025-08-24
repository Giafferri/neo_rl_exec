# =============================================================
# orderbook/orderbook_files.py
#
# These files are used to manage the order book data on several files
# =============================================================

import pandas as pd

def load_orderbook_data(paths):
    """
    Load order book data from a list of file paths.

    Args:
        paths (list[str]): List of paths to the order book data files.

    Returns:
        pd.DataFrame: Concatenated DataFrame containing the order book data 
                      from all provided files.
    """
    dataframes = []
    for path in paths:
        try:
            df = pd.read_feather(path)
            dataframes.append(df)
        except Exception as e:
            print(f"Error loading order book data from {path}: {e}")
    
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return None