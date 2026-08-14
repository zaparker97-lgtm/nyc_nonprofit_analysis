# Nonprofit Presence and Community Need in New York City

## Project Overview

This project examines how nonprofit organizations are distributed across New York City's five boroughs and compares that distribution with borough-level poverty. It began with an IRS nonprofit dataset and adds U.S. Census Bureau poverty data to ask whether nonprofit presence appears to line up with where community need is highest.

The analysis focuses on:

- overall nonprofit counts by borough
- faith-based / religion-related nonprofits
- child welfare, adoption, foster care, and youth-related nonprofits
- nonprofit density per 10,000 residents
- Human Services nonprofit density
- borough poverty rates
- relational database analysis using SQLite and SQL

## Research Questions

1. Which boroughs have the most nonprofits?
2. How are faith-based nonprofits distributed across the five boroughs?
3. How many nonprofits focus on child welfare, adoption, foster care, or youth services?
4. Do boroughs with higher poverty rates have more nonprofits or Human Services nonprofits per resident?
5. Is there a visible gap between nonprofit concentration and community need?

## Data Sources

### Dataset 1: IRS Exempt Organizations Business Master File Extract

Source: Internal Revenue Service

https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf

The NYC extract contains 48,066 nonprofit records. The analysis uses organization name, ZIP code, NTEE classification code, subsection, ruling date, assets, income, and revenue, then adds a borough field based on ZIP code.

### Dataset 2: U.S. Census Bureau — 2022 ACS 5-Year Subject Table S1701

Source: U.S. Census Bureau

https://api.census.gov/data/2022/acs/acs5/subject

The project uses:

- total population for whom poverty status is determined
- number below the poverty level
- percent below the poverty level

The five NYC counties are mapped to their borough equivalents:

- Bronx County → Bronx
- Kings County → Brooklyn
- New York County → Manhattan
- Queens County → Queens
- Richmond County → Staten Island

The Census data can be reproduced with `pull_census_data.py`.

## Technologies Used

- Python 3
- pandas
- NumPy
- Matplotlib
- requests
- SQLite / sqlite3
- Jupyter Notebook
- Git and GitHub

## Project Structure

```text
analysis.ipynb
eo1_nyc (1).csv
functions.py
pull_census_data.py
build_capstone_outputs.py
requirements.txt
README.md
data/
    census_poverty_2022.csv
    nonprofits_cleaned.csv
    borough_summary_merged.csv
database/
    nyc_nonprofit.db
    queries.sql
    erd.png
charts/
    01_nonprofits_by_borough.png
    02_faith_based_by_borough.png
    03_poverty_vs_nonprofit_density.png
    04_ntee_category_breakdown_pie.png
```

## Setup and Running the Project

Clone or download the repository, then open a terminal in the project folder.

### macOS / Linux

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start Jupyter:

```bash
python3 -m jupyter notebook
```

Open `analysis.ipynb` and run the notebook from top to bottom.

Deactivate the environment when finished:

```bash
deactivate
```

### Windows PowerShell

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Start Jupyter:

```powershell
py -m jupyter notebook
```

Open `analysis.ipynb` and run the notebook from top to bottom.

Deactivate the environment when finished:

```powershell
deactivate
```

## Reproducing the Census Data

The repository includes the Census CSV used in the analysis. To pull a fresh copy from the Census API, set a Census API key in your environment and run:

```bash
python3 pull_census_data.py
```

The script saves the results to:

```text
data/census_poverty_2022.csv
```

## Data Cleaning and Preparation

The project:

- reduces the original IRS extract to the fields needed for analysis
- checks missing values, duplicates, and data types
- flags negative financial values and converts those values to missing for analysis
- assigns boroughs using ZIP codes
- preserves records with missing NTEE codes for overall counts while excluding them from category-specific analysis
- creates NTEE major-category and faith-based indicators
- merges borough-level Census measures with nonprofit records
- calculates nonprofits per 10,000 residents

## Custom Python Functions

The project includes three reusable functions in `functions.py`:

1. `assign_borough()` — assigns an NYC borough from a ZIP code
2. `filter_by_ntee()` — filters nonprofits by an NTEE code prefix
3. `calculate_nonprofit_density()` — calculates nonprofits per 10,000 residents

## Database and SQL

The SQLite database contains two related tables:

- `borough_poverty` — one record per NYC borough
- `nonprofits` — many nonprofit records linked to a borough

The relationship is one borough to many nonprofits. The Entity Relationship Diagram is stored in `database/erd.png`.

The notebook includes SQL queries using:

- joins
- grouping and aggregation
- filtering
- calculated density measures
- a subquery

Saved SQL examples are also available in `database/queries.sql`.

## Visualizations

The notebook includes multiple chart types:

- bar chart — nonprofits by borough
- bar chart — faith-based nonprofits by borough
- bar chart — child welfare, adoption, and youth nonprofits by borough
- scatter plot — poverty rate vs. nonprofit density
- pie chart — major NTEE category breakdown

## Key Findings

- Manhattan has the most nonprofits overall, with 20,872 records assigned to the borough.
- Brooklyn has the most faith-based / religion-related nonprofits under the NTEE X definition, with 4,699.
- The child welfare, adoption, foster care, and youth-related filter identifies 1,112 organizations.
- The Bronx has the highest borough poverty rate in the Census data at 26.9%.
- Manhattan has the highest nonprofit density per 10,000 residents by a large margin.
- Nonprofit concentration and poverty do not move together in a simple way at the borough level.

## Limitations

- Borough-level Census data hide neighborhood-level differences.
- About 10,000 IRS records are missing NTEE codes.
- A nonprofit's registered address does not necessarily represent the communities it serves.
- The child welfare/adoption/youth classification is based on a practical NTEE and keyword filter rather than a perfect service-area classification.
- The poverty-vs.-density scatter plot contains only five borough observations, so it is descriptive rather than causal.

## AI Acknowledgment

Generative AI was used as a support tool for code debugging, organization, documentation, and explanations of technical concepts. The analysis approach, project decisions, review of outputs, and final submission remain the responsibility of the project owner.
