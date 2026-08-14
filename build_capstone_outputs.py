"""Rebuild merged analysis outputs using the current Census CSV."""

from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from functions import calculate_nonprofit_density

DATA_DIR = Path("data")
DB_DIR = Path("database")
CHART_DIR = Path("charts")

DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)
CHART_DIR.mkdir(exist_ok=True)

# -------------------------
# Load cleaned nonprofit and Census data
# -------------------------
nonprofits = pd.read_csv(DATA_DIR / "nonprofits_cleaned.csv", low_memory=False)
census = pd.read_csv(DATA_DIR / "census_poverty_2022.csv")

# Standardize column names expected from the Census API pull
if "BELOW_POVERTY_EST" in census.columns and "BELOW_POVERTY" not in census.columns:
    census = census.rename(columns={"BELOW_POVERTY_EST": "BELOW_POVERTY"})

known = nonprofits[nonprofits["BOROUGH"] != "Unknown"].copy()
known["NTEE_MAJOR"] = known["NTEE_CD"].fillna("").astype(str).str.upper().str[:1]
known["IS_FAITH_BASED"] = known["NTEE_MAJOR"].eq("X").astype(int)

# -------------------------
# Borough summary / merge
# -------------------------
summary = (
    known.groupby("BOROUGH")
    .agg(
        NONPROFIT_COUNT=("EIN", "count"),
        FAITH_BASED_COUNT=("IS_FAITH_BASED", "sum"),
        HUMAN_SERVICES_COUNT=("NTEE_MAJOR", lambda s: (s == "P").sum()),
    )
    .reset_index()
)

merged = summary.merge(census, on="BOROUGH", how="left")

merged["NONPROFITS_PER_10K"] = merged.apply(
    lambda r: calculate_nonprofit_density(
        r["NONPROFIT_COUNT"], r["TOTAL_POPULATION"]
    ),
    axis=1,
)
merged["FAITH_BASED_PER_10K"] = merged.apply(
    lambda r: calculate_nonprofit_density(
        r["FAITH_BASED_COUNT"], r["TOTAL_POPULATION"]
    ),
    axis=1,
)
merged["HUMAN_SERVICES_PER_10K"] = merged.apply(
    lambda r: calculate_nonprofit_density(
        r["HUMAN_SERVICES_COUNT"], r["TOTAL_POPULATION"]
    ),
    axis=1,
)

merged = merged.sort_values("POVERTY_RATE", ascending=False)
merged.to_csv(DATA_DIR / "borough_summary_merged.csv", index=False)

# -------------------------
# Charts
# -------------------------
order = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
plot_df = merged.set_index("BOROUGH").reindex(order)

plt.figure(figsize=(9, 5))
plot_df["NONPROFIT_COUNT"].plot(kind="bar")
plt.title("NYC Nonprofits by Borough")
plt.xlabel("Borough")
plt.ylabel("Number of nonprofits")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(CHART_DIR / "01_nonprofits_by_borough.png", dpi=160)
plt.close()

plt.figure(figsize=(9, 5))
plot_df["FAITH_BASED_COUNT"].plot(kind="bar")
plt.title("Faith-Based Nonprofits by Borough")
plt.xlabel("Borough")
plt.ylabel("Number of religion-related nonprofits (NTEE X)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(CHART_DIR / "02_faith_based_by_borough.png", dpi=160)
plt.close()

plt.figure(figsize=(8, 6))
plt.scatter(merged["POVERTY_RATE"], merged["NONPROFITS_PER_10K"], s=90)
for _, row in merged.iterrows():
    plt.annotate(
        row["BOROUGH"],
        (row["POVERTY_RATE"], row["NONPROFITS_PER_10K"]),
        xytext=(5, 5),
        textcoords="offset points",
    )
plt.title("Poverty Rate vs. Nonprofit Density")
plt.xlabel("Population below poverty level (%)")
plt.ylabel("Nonprofits per 10,000 residents")
plt.tight_layout()
plt.savefig(CHART_DIR / "03_poverty_vs_nonprofit_density.png", dpi=160)
plt.close()

major_labels = {
    "A": "Arts/Culture",
    "B": "Education",
    "C": "Environment",
    "D": "Animal-related",
    "E": "Health",
    "F": "Mental Health",
    "G": "Diseases/Disorders",
    "H": "Medical Research",
    "I": "Crime/Legal",
    "J": "Employment",
    "K": "Food/Agriculture",
    "L": "Housing",
    "M": "Public Safety",
    "N": "Recreation/Sports",
    "O": "Youth Development",
    "P": "Human Services",
    "Q": "International",
    "R": "Civil Rights",
    "S": "Community Improvement",
    "T": "Philanthropy",
    "U": "Science/Technology",
    "V": "Social Science",
    "W": "Public Benefit",
    "X": "Religion-related",
    "Y": "Mutual Benefit",
    "Z": "Unknown/Unclassified",
}

major_counts = (
    known.loc[known["NTEE_MAJOR"] != "", "NTEE_MAJOR"]
    .value_counts()
    .head(10)
)
labels = [major_labels.get(code, code) for code in major_counts.index]

plt.figure(figsize=(9, 7))
plt.pie(major_counts.values, labels=labels, autopct="%1.1f%%", startangle=90)
plt.title("Top 10 NTEE Major Categories in NYC")
plt.tight_layout()
plt.savefig(CHART_DIR / "04_ntee_category_breakdown_pie.png", dpi=160)
plt.close()


# -------------------------
# ERD
# -------------------------
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis("off")

ax.text(
    0.05, 0.88, "borough_poverty", fontsize=16, weight="bold",
    bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black")
)
ax.text(
    0.05, 0.77,
    "PK  borough\n"
    "    county\n"
    "    county_fips\n"
    "    total_population\n"
    "    below_poverty\n"
    "    poverty_rate\n"
    "    year",
    fontsize=12, va="top",
    bbox=dict(boxstyle="round,pad=0.6", fc="white", ec="black"),
)

ax.text(
    0.60, 0.88, "nonprofits", fontsize=16, weight="bold",
    bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black")
)
ax.text(
    0.60, 0.77,
    "    ein\n"
    "    name\n"
    "    city\n"
    "    state\n"
    "    zip\n"
    "FK  borough\n"
    "    subsection\n"
    "    ruling\n"
    "    asset_amt\n"
    "    income_amt\n"
    "    revenue_amt\n"
    "    ntee_cd\n"
    "    ntee_major\n"
    "    is_faith_based",
    fontsize=12, va="top",
    bbox=dict(boxstyle="round,pad=0.6", fc="white", ec="black"),
)

ax.annotate(
    "", xy=(0.60, 0.55), xytext=(0.38, 0.55),
    arrowprops=dict(arrowstyle="<->", lw=2)
)
ax.text(0.42, 0.59, "1 : many", fontsize=12)
ax.set_title("NYC Nonprofit Analysis — Entity Relationship Diagram", fontsize=18)
plt.tight_layout()
plt.savefig(DB_DIR / "erd.png", dpi=180, bbox_inches="tight")
plt.close()

# -------------------------
# SQLite database
# -------------------------
db_path = DB_DIR / "nyc_nonprofit.db"
if db_path.exists():
    db_path.unlink()

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON;")

conn.execute(
    """
    CREATE TABLE borough_poverty (
        borough TEXT PRIMARY KEY,
        county TEXT NOT NULL,
        county_fips TEXT NOT NULL,
        total_population INTEGER NOT NULL,
        below_poverty INTEGER,
        poverty_rate REAL NOT NULL,
        year INTEGER NOT NULL
    )
    """
)

conn.execute(
    """
    CREATE TABLE nonprofits (
        ein INTEGER,
        name TEXT NOT NULL,
        city TEXT,
        state TEXT,
        zip TEXT,
        borough TEXT NOT NULL,
        subsection REAL,
        ruling REAL,
        asset_amt REAL,
        income_amt REAL,
        revenue_amt REAL,
        ntee_cd TEXT,
        ntee_major TEXT,
        is_faith_based INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (borough) REFERENCES borough_poverty(borough)
    )
    """
)

census_db = census[
    [
        "BOROUGH",
        "COUNTY",
        "COUNTY_FIPS",
        "TOTAL_POPULATION",
        "BELOW_POVERTY",
        "POVERTY_RATE",
        "YEAR",
    ]
].copy()
census_db.columns = [c.lower() for c in census_db.columns]
census_db.to_sql("borough_poverty", conn, if_exists="append", index=False)

nonprofit_db = known[
    [
        "EIN",
        "NAME",
        "CITY",
        "STATE",
        "ZIP",
        "BOROUGH",
        "SUBSECTION",
        "RULING",
        "ASSET_AMT",
        "INCOME_AMT",
        "REVENUE_AMT",
        "NTEE_CD",
        "NTEE_MAJOR",
        "IS_FAITH_BASED",
    ]
].copy()
nonprofit_db.columns = [c.lower() for c in nonprofit_db.columns]
nonprofit_db.to_sql("nonprofits", conn, if_exists="append", index=False)

conn.execute(
    "CREATE INDEX IF NOT EXISTS idx_nonprofits_borough ON nonprofits(borough)"
)
conn.execute(
    "CREATE INDEX IF NOT EXISTS idx_nonprofits_ntee ON nonprofits(ntee_major)"
)
conn.commit()
conn.close()

print("Rebuilt outputs using the current Census API data.")
print()
print(
    merged[
        [
            "BOROUGH",
            "NONPROFIT_COUNT",
            "FAITH_BASED_COUNT",
            "POVERTY_RATE",
            "NONPROFITS_PER_10K",
        ]
    ].to_string(index=False)
)
