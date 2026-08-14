from pathlib import Path
"""Pull 2022 ACS 5-Year Subject Table S1701 poverty data for NYC counties."""

import os
import pandas as pd
import requests

API_URL = "https://api.census.gov/data/2022/acs/acs5/subject"

NYC_COUNTIES = {
    "005": "Bronx",
    "047": "Brooklyn",
    "061": "Manhattan",
    "081": "Queens",
    "085": "Staten Island",
}


def get_census_poverty_data(save_path="data/census_poverty_2022.csv"):
    params = {
        "get": "NAME,S1701_C01_001E,S1701_C02_001E,S1701_C03_001E",
        "for": "county:*",
        "in": "state:36",
    }

    api_key = os.environ.get("CENSUS_API_KEY")
    if api_key:
        params["key"] = api_key

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    try:
        rows = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        preview = response.text[:500]
        raise RuntimeError(
            "The Census API returned a non-JSON response. "
            f"HTTP status: {response.status_code}. "
            f"Response preview: {preview!r}"
        ) from exc

    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df[df["county"].isin(NYC_COUNTIES)].copy()

    df["BOROUGH"] = df["county"].map(NYC_COUNTIES)
    df = df.rename(columns={
        "NAME": "COUNTY",
        "S1701_C01_001E": "TOTAL_POPULATION",
        "S1701_C02_001E": "BELOW_POVERTY",
        "S1701_C03_001E": "POVERTY_RATE",
        "county": "COUNTY_FIPS",
    })

    for col in ["TOTAL_POPULATION", "BELOW_POVERTY", "POVERTY_RATE"]:
        df[col] = pd.to_numeric(df[col])

    df["YEAR"] = 2022
    df["SOURCE_TABLE"] = "ACS 5-Year Subject Table S1701"

    df = df[[
        "BOROUGH",
        "COUNTY",
        "COUNTY_FIPS",
        "TOTAL_POPULATION",
        "BELOW_POVERTY",
        "POVERTY_RATE",
        "YEAR",
        "SOURCE_TABLE",
    ]].sort_values("BOROUGH")

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)
    return df


if __name__ == "__main__":
    print(get_census_poverty_data())
