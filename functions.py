"""Reusable custom functions for the NYC nonprofit capstone."""

import pandas as pd
import numpy as np

def assign_borough(zip_code):
    """Assign an NYC borough using the first three digits of a ZIP code."""
    digits = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]
    if len(digits) < 3:
        return "Unknown"

    prefix = digits[:3]
    mapping = {
        "100": "Manhattan", "101": "Manhattan", "102": "Manhattan",
        "103": "Staten Island",
        "104": "Bronx",
        "110": "Queens", "111": "Queens", "113": "Queens",
        "114": "Queens", "116": "Queens",
        "112": "Brooklyn",
    }
    return mapping.get(prefix, "Unknown")

def filter_by_ntee(dataframe, ntee_prefix):
    """Filter nonprofit records by the beginning of their NTEE code."""
    prefix = str(ntee_prefix).upper().strip()
    mask = dataframe["NTEE_CD"].fillna("").astype(str).str.upper().str.startswith(prefix)
    return dataframe.loc[mask].copy()

def calculate_nonprofit_density(nonprofit_count, population, per=10000):
    """Calculate nonprofits per 10,000 residents (or another chosen base)."""
    if pd.isna(population) or population == 0:
        return np.nan
    return nonprofit_count / population * per
