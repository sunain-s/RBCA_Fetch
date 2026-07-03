# RBCA List Webscraping

#-----------------------------------------------------------------------------------------------------------
# Imports

import glob
import requests
import pandas as pd
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

#-----------------------------------------------------------------------------------------------------------
# Webscraping

URL = (
    "https://www.find-a-building-control-approver.service.gov.uk"
    "/api/GetRBCARegister?country=England"
)

headers = {
    "User-Agent": "RBCA Register Downloader/1.0 (Sunain.Syed@communities.gov.uk)" # replace with long standing email for contact from site admins
}

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
session.mount("https://", HTTPAdapter(max_retries=retries))
session.headers.update(headers)

response = session.get(URL, timeout=30)
response.raise_for_status()
data = response.json()

if "RBCAApplications" not in data:
    raise ValueError("Unexpected API response format.")

#-----------------------------------------------------------------------------------------------------------
# Extract Data

# Extract the company name, and registration number (RBCPxxxxxxxx)
records = []
for rbca in data.get("RBCAApplications", []):
    employer = rbca.get("Employer", {})
    records.append({
        "Company": employer.get("EmployerName", "UNKNOWN"),
        "Registration Number": rbca.get("Id", "UNKNOWN")
    })

df_raw = pd.DataFrame(records)
df_raw = df_raw[["Registration Number", "Company"]]
df_raw = df_raw.drop_duplicates(subset="Registration Number")
df = df_raw.sort_values(by="Company", key=lambda s: s.str.lower()) # df is used for snapshot output
df.reset_index(drop=True, inplace=True)
print(df)
print(f'Number of RBCAs = {len(df)}')

#-----------------------------------------------------------------------------------------------------------
# Save Data

today = datetime.today().strftime("%Y-%m-%d")
filename = f'RBCA_Register_{today}'

# All RBCAs as of timestamp
df.to_excel(filename + '.xlsx', index=False)
df.to_csv(filename + '.csv', index=False, encoding="utf-8-sig") # csv for simpler processing if needed

#-----------------------------------------------------------------------------------------------------------
# Diff Processing
# 
# USE df_raw for comparisons, NEVER use df for comparisons

# Get data from .xlsx (Excel) files
files = sorted(glob.glob("RBCA_Register_*.xlsx"))
today_file = f"RBCA_Register_{today}.xlsx"
files = [f for f in files if not f.endswith(today_file)] # Exclude curr_file from list
prev_file = files[-1] if files else None # Choose most recent snapshot (excluding current one)

if prev_file:
    prev_df = pd.read_excel(prev_file)
else:
    prev_df = pd.DataFrame(columns=["Registration Number", "Company"])
prev_df = prev_df[["Registration Number", "Company"]]
prev_df = prev_df.drop_duplicates(subset="Registration Number")

# Comparison sets
prev_set = set(prev_df["Registration Number"])
curr_set = set(df_raw["Registration Number"])

df_raw["Note"] = ""
df_raw.loc[df_raw["Registration Number"].isin(curr_set - prev_set), "Note"] = "[n]" # new additions in curr_set, not in prev_set

removed = prev_df[prev_df["Registration Number"].isin(prev_set - curr_set)].copy() # removals in prev_set, not in curr_set
removed["Note"] = "[r]"

# Build and organise diff output
diff_df = pd.concat([df_raw, removed], ignore_index=True)
cols = ["Registration Number", "Company", "Note"]
diff_df = diff_df.reindex(columns=cols, fill_value="")
diff_df = diff_df.sort_values(by="Company", key=lambda s: s.str.lower())
diff_df.reset_index(drop=True, inplace=True)

# Saving diff files
diff_filename = f"RBCA_Diff_{today}"
diff_df.to_excel(diff_filename + ".xlsx", index=False)
diff_df.to_csv(diff_filename + ".csv", index=False, encoding="utf-8-sig")