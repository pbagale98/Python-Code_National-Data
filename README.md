
```markdown
# U.S. Socioeconomic Data Aggregator

This project is a Python-based data aggregation tool that fetches and compiles datasets from three major U.S. government sources:

- **Census Bureau API**
- **Bureau of Labor Statistics (BLS) API**
- **Bureau of Economic Analysis (BEA) API**

It allows you to pull multi-year demographic, income, labor force, housing, and GDP data across all U.S. states and cities with populations over 50,000.

## Features

- Pull Census ACS 5-Year data (2010–2022) by state or all U.S. cities
- Clean, standardize, and filter city-level data based on population
- Calculate unemployment rate on the fly
- Retrieve national unemployment data from BLS
- Retrieve state-level GDP data from BEA
- Save all results to `.csv` files for further analysis

## Requirements

- Python 3.6+
- `requests`
- `pandas`
- `numpy`

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

## Setup

Update your API keys inside the script:

```python
API_KEYS = {
    "census": "YOUR_CENSUS_API_KEY",
    "bls": "YOUR_BLS_API_KEY",
    "bea": "YOUR_BEA_API_KEY"
}
```

## Usage

Run the script in a Python environment. The script currently does not have a CLI or GUI but is built to run individual functions:

### Pull Census Data for a Specific State

```python
pull_census_state("06")  # California
```

### Pull Census Data for All Cities in All States (Population ≥ 50,000)

```python
pull_census_all_states()
```

### Pull BLS National Unemployment Data

```python
pull_bls_data()
```

### Pull BEA GDP by State

```python
pull_bea_data()
```

Each function saves a `.csv` file to the working directory with appropriately formatted and labeled data.

## Output Files

- `census_state_XX.csv`: Census data for a specific state (XX = FIPS code)
- `census_all_states_cities.csv`: Cleaned and filtered data from all major U.S. cities
- `bls_unemployment_data.csv`: Monthly national unemployment data from BLS
- `bea_gdp_by_state.csv`: State-level GDP data from BEA

## Data Sources

- [U.S. Census Bureau](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [Bureau of Labor Statistics (BLS)](https://www.bls.gov/developers/)
- [Bureau of Economic Analysis (BEA)](https://apps.bea.gov/API/signup/index.cfm)

## License

MIT License — feel free to use and modify this project for any purpose.
``'
