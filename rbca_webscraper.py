# RBCA List Webscraping

#-----------------------------------------------------------------------------------------------------------
# Imports

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

df = pd.DataFrame(records)
df = df[["Registration Number", "Company"]]
df = df.drop_duplicates(subset="Registration Number")
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
