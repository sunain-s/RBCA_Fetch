# RBCA List Webscraping

#-----------------------------------------------------------------------------------------------------------
# Imports

import requests
import pandas as pd
import json

#-----------------------------------------------------------------------------------------------------------
# Webscraping

URL = (
    "https://www.find-a-building-control-approver.service.gov.uk"
    "/api/GetRBCARegister?country=England"
)

headers = {
    "User-Agent": "RBCA Register Downloader/1.0 (Sunain.Syed@communities.gov.uk)" # replace with long standing email for contact
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()
data = response.json()

if "RBCAApplications" not in data:
    raise ValueError("Unexpected API response format.")

# Extract the company name, and registration number (RBCPxxxxxxxx)
records = []
for rbca in data["RBCAApplications"]:
    records.append({
        "Company": rbca["Employer"]["EmployerName"],
        "Registration Number": rbca["Id"]
    })

df = pd.DataFrame(records)
df.sort_values("Company")
df.reset_index(drop=True, inplace=True)
print(df)

# This produces the file of all RBCAs at the time it was ran
df.to_csv("RBCA_Register.csv", index=False)
