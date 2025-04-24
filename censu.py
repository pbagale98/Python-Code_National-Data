import sys
import requests
import pandas as pd
import numpy as np
import json

# ========= USER CONFIG ========= #
API_KEYS = {
    "census": "836fdc4da5b1160da432bcf77f7a179c9f6db662",
    "bls": "33981ff01bdc48e681013b2ba78c870f",
    "bea": "8369F6B2-6EA8-431B-84F8-428E58141C77"
}

# ========= CENSUS CONFIG ========= #
all_state_fips = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12",
    "13", "15", "16", "17", "18", "19", "20", "21", "22", "23",
    "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
    "34", "35", "36", "37", "38", "39", "40", "41", "42", "44",
    "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56"
]
years = list(range(2020, 2023))

# ========= BLS CONFIG ========= #
BLS_SERIES_IDS = {
    "unemployment_rate_us": ["LNS14000000"]
}

# ========= BEA CONFIG ========= #
BEA_DATASETS = {
    "gdp_by_state": {
        "url": "https://apps.bea.gov/api/data/",
        "params": {
            "method": "GetData",
            "datasetname": "Regional",
            "TableName": "SAGDP2",
            "LineCode": 1,
            "GeoFIPS": "STATE",
            "Year": "2022",
            "ResultFormat": "JSON"
        }
    }
}


def get_user_input(prompt, options=None):
    while True:
        user_input = input(prompt).strip().lower()
        if not options or user_input in options:
            return user_input
        print(f"Invalid input. Please choose from: {', '.join(options)}")


def pull_census_state(state_fips):
    all_data = []
    for year in years:
        url = f"https://api.census.gov/data/{year}/acs/acs5"
        params = {
            "get": "NAME,B01003_001E,B06011_001E",
            "for": "county:*",
            "in": f"state:{state_fips}",
            "key": API_KEYS["census"]
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            df["year"] = year
            all_data.append(df)
        else:
            print(f"Failed to fetch data for {year}: {response.status_code}")

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(f"census_state_{state_fips}.csv", index=False)
    print(f"Saved census data for state {state_fips} as 'census_state_{state_fips}.csv'")


def pull_census_all_states():
    all_data = []

    for state_fips in all_state_fips:
        for year in years:
            url = f"https://api.census.gov/data/{year}/acs/acs5"
            params = {
                "get": "NAME,B01003_001E,B06011_001E,B25105_001E,B25058_001E,B25070_007E,B25064_001E,"
                       "B17001_002E,B10058_001E,B08303_001E,B23001_001E,B23001_007E,B19013_001E,"
                       "B09001_001E,C24010_004E,C24010_005E,C24010_006E,C24010_007E,B15001_017E,"
                       "B15001_050E,B07009_005E,B07009_013E",
                "for": "place:*",
                "in": f"state:{state_fips}",
                "key": API_KEYS["census"]
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if len(data) < 2:
                    print(f"No data returned for state {state_fips} in year {year}")
                    continue

                df = pd.DataFrame(data[1:], columns=data[0])
                df["year"] = year
                all_data.append(df)

            except requests.exceptions.RequestException as e:
                print(f"Request failed for state {state_fips} in year {year}: {e}")
            except Exception as e:
                print(f"General error for state {state_fips} in year {year}: {e}")

    if not all_data:
        print("No Census data pulled. Exiting.")
        return

    final_df = pd.concat(all_data, ignore_index=True)

    rename_map = {
        "NAME": "City",
        "B01003_001E": "Total_Population",
        "B06011_001E": "Median_Income",
        "B25105_001E": "Median_Monthly_Housing_Costs",
        "B25058_001E": "Median_Contract_Rent",
        "B25070_007E": "Rent_30_34_Percent",
        "B25064_001E": "Median_Gross_Rent",
        "B17001_002E": "Poverty_Rate",
        "B10058_001E": "Gross_Rent_Percentage",
        "B08303_001E": "Total_Commute",
        "B23001_001E": "Total_Labor_Force",
        "B23001_007E": "Unemployed_Population",
        "B19013_001E": "Median_Household_Income",
        "B09001_001E": "Children_Under_6",
        "C24010_004E": "Construction_Workers",
        "C24010_005E": "Extraction_Workers",
        "C24010_006E": "Installation_Maintenance_Repair_Workers",
        "C24010_007E": "Production_Workers",
        "B15001_017E": "Males_25_34_Bachelors",
        "B15001_050E": "Females_25_34_Bachelors",
        "B07009_005E": "Native_Bachelors",
        "B07009_013E": "Foreign_Bachelors"
    }
    final_df.rename(columns=rename_map, inplace=True)

    numeric_cols = list(rename_map.values())
    numeric_cols.remove("City")

    for col in numeric_cols:
        final_df[col] = pd.to_numeric(final_df[col], errors="coerce")

    final_df["Unemployment_Rate"] = (final_df["Unemployed_Population"] / final_df["Total_Labor_Force"]) * 100
    final_df.replace(-666666666, np.nan, inplace=True)

    # Filter based on 2010 population
    cities_2010 = final_df[(final_df["year"] == 2010) & (final_df["Total_Population"] >= 50000)]["City"]
    filtered_df = final_df[final_df["City"].isin(cities_2010)].copy()

    filtered_df[["City_Name", "State"]] = filtered_df["City"].str.split(", ", expand=True)
    filtered_df["City_Name"] = filtered_df["City_Name"].str.replace(" city (balance)", "", regex=False)
    filtered_df["City_Name"] = filtered_df["City_Name"].str.replace(r" city| town| village", "", regex=True)

    column_order = ['year', 'City_Name', 'State', 'Total_Population', 'Median_Income',
                    'Median_Monthly_Housing_Costs', 'Median_Contract_Rent', 'Rent_30_34_Percent',
                    'Median_Gross_Rent', 'Poverty_Rate', 'Gross_Rent_Percentage', 'Total_Commute',
                    'Total_Labor_Force', 'Unemployed_Population', 'Unemployment_Rate',
                    'Median_Household_Income', 'Children_Under_6', 'Construction_Workers',
                    'Extraction_Workers', 'Installation_Maintenance_Repair_Workers',
                    'Production_Workers', 'Males_25_34_Bachelors', 'Females_25_34_Bachelors',
                    'Native_Bachelors', 'Foreign_Bachelors']

    filtered_df = filtered_df[column_order]
    filtered_df.to_csv("census_all_states_cities.csv", index=False)
    print("✅ Census data saved as 'census_all_states_cities.csv'")



def pull_bls_data():
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": BLS_SERIES_IDS["unemployment_rate_us"],
        "registrationkey": API_KEYS["bls"]
    })

    response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=data, headers=headers)
    if response.status_code == 200:
        series = response.json().get("Results", {}).get("series", [])
        df_list = []
        for item in series:
            sid = item.get("seriesID")
            data_points = item.get("data", [])
            for point in data_points:
                point["seriesID"] = sid
            df_list.extend(data_points)
        df = pd.DataFrame(df_list)
        df.to_csv("bls_unemployment_data.csv", index=False)
        print("BLS data saved as 'bls_unemployment_data.csv'")
    else:
        print("BLS API call failed:", response.text[:300])


def pull_bea_data():
    dataset = BEA_DATASETS["gdp_by_state"]
    response = requests.get(dataset["url"], params={**dataset["params"], "UserID": API_KEYS["bea"]})
    if response.status_code == 200:
        data = response.json().get("BEAAPI", {}).get("Results", {}).get("Data", [])
        df = pd.DataFrame(data)
        df.to_csv("bea_gdp_by_state.csv", index=False)
        print("BEA data saved as 'bea_gdp_by_state.csv'")
    else:
        print("BEA API call failed:", response.text[:300])


def main():
    print("Which dataset would you like to pull?")
    print("1. Census - All States & Cities")
    print("2. Census - Single State (by FIPS)")
    print("3. BLS - National Unemployment")
    print("4. BEA - GDP by State")

    choice = get_user_input("Enter choice (1-4): ", options=["1", "2", "3", "4"])

    if choice == "1":
        pull_census_all_states()
    elif choice == "2":
        state_fips = get_user_input("Enter 2-digit state FIPS code (e.g., 06 for CA): ")
        pull_census_state(state_fips)
    elif choice == "3":
        pull_bls_data()
    elif choice == "4":
        pull_bea_data()
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
