# RBCA List Webscraping

#-----------------------------------------------------------------------------------------------------------
# Imports

import os
import glob
import requests
import pandas as pd
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#-----------------------------------------------------------------------------------------------------------
# Setup

os.makedirs("snapshots", exist_ok=True)
os.makedirs("diffs", exist_ok=True)

URL = (
    "https://www.find-a-building-control-approver.service.gov.uk"
    "/api/GetRBCARegister?country=England"
)

headers = {
    "User-Agent": "RBCA Register Downloader/1.0 (Sunain.Syed@communities.gov.uk)" # replace with long standing email for contact from site admins
}

#-----------------------------------------------------------------------------------------------------------
# Fetch Data

def create_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update(headers)
    return session

def fetch_rbca_data(session, url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "RBCAApplications" not in data:
        raise ValueError("Unexpected API response format.")
    return data["RBCAApplications"]

#-----------------------------------------------------------------------------------------------------------
# Process Snapshot

def build_dataframe(applications):
    # Extract the company name, and registration number (RBCPxxxxxxxx)
    records = []
    for rbca in applications:
        employer = rbca.get("Employer", {})
        records.append({
            "Company": employer.get("EmployerName", "UNKNOWN"),
            "Registration Number": rbca.get("Id", "UNKNOWN")
        })
    df = pd.DataFrame(records)
    df = df[["Registration Number", "Company"]]
    df = df.drop_duplicates(subset="Registration Number")
    return df

def sort_dataframe(df):
    return df.sort_values(by="Company", key=lambda s: s.str.lower()).reset_index(drop=True)

#-----------------------------------------------------------------------------------------------------------
# Diff Processing
# 
# USE df_raw for diff comparisons, NEVER use df for diff comparisons

def load_previous_snapshot(today):
    files = sorted(glob.glob("snapshots/RBCA_Register_*.xlsx"))
    today_file = f"snapshots/RBCA_Register_{today}.xlsx"
    files = [f for f in files if not f.endswith(today_file)] # Exclude curr_file from list
    prev_file = files[-1] if files else None # Choose most recent snapshot (excluding current one)

    if prev_file:
        prev_df = pd.read_excel(prev_file)
        return prev_df[["Registration Number", "Company"]].drop_duplicates(subset="Registration Number")
    return pd.DataFrame(columns=["Registration Number", "Company"])

def compute_diff(df_raw, prev_df):
    prev_set = set(prev_df["Registration Number"])
    curr_set = set(df_raw["Registration Number"])

    df_raw["Note"] = ""
    df_raw.loc[df_raw["Registration Number"].isin(curr_set - prev_set), "Note"] = "[n]" # new additions in curr_set, not in prev_set

    removed = prev_df[prev_df["Registration Number"].isin(prev_set - curr_set)].copy() # removals in prev_set, not in curr_set
    removed["Note"] = "[r]"

    # Build and organise diff output
    diff_df = pd.concat([df_raw, removed], ignore_index=True)
    diff_df = diff_df[["Registration Number", "Company", "Note"]]
    diff_df = diff_df.sort_values(by="Company", key=lambda s: s.str.lower())
    diff_df.reset_index(drop=True, inplace=True)

    return diff_df

#-----------------------------------------------------------------------------------------------------------
# Save Data

def save_snapshot(df, today):
    filename = f'snapshots/RBCA_Register_{today}'
    # All RBCAs as of timestamp
    df.to_excel(filename + '.xlsx', index=False)
    df.to_csv(filename + '.csv', index=False, encoding="utf-8-sig") # csv for simpler processing if needed

def save_diff(diff_df, today):
    filename = f"diffs/RBCA_Diff_{today}"
    diff_df.to_excel(filename + ".xlsx", index=False)
    diff_df.to_csv(filename + ".csv", index=False, encoding="utf-8-sig")

#-----------------------------------------------------------------------------------------------------------
# Main

def main():
    today = datetime.today().strftime("%Y-%m-%d")
    session = create_session()
    applications = fetch_rbca_data(session, URL)
    df_raw = build_dataframe(applications)
    df = sort_dataframe(df_raw)

    print(df)
    print(f'Number of RBCAs = {len(df)}')

    save_snapshot(df, today)
    
    prev_df = load_previous_snapshot(today)
    diff_df = compute_diff(df_raw, prev_df) # USE df_raw for diff comparisons, NEVER use df for diff comparisons
    save_diff(diff_df, today)

if __name__ == "__main__":
    main()