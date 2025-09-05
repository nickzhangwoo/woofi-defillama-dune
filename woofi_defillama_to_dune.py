import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# 配置区
# -----------------------------
DUNE_API_KEY = "Vg96yb9PuDnP5LG4NhRPSKyZNFL69Z3k"  # 企业版 API token
DUNE_NAMESPACE = "woofianalytics"                   # 企业 namespace
# -----------------------------

BASE_URL = "https://api.llama.fi"

def get_woofi_metrics():
    protocols = ["woofi-pro-perps", "woofi-swap", "woofi-earn"]
    data = []

    for protocol in protocols:
        url = f"{BASE_URL}/protocol/{protocol}"
        resp = requests.get(url)
        if resp.status_code == 200:
            info = resp.json()
            data.append({
                "protocol": info.get("name", protocol),
                "tvl": info.get("tvl"),
                "volume_24h": info.get("volume_24h"),
                "fees_24h": info.get("fees_24h"),
                "users_24h": info.get("users_24h"),
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            print(f"Error fetching {protocol}: {resp.status_code}")

    df = pd.DataFrame(data)
    print(f"Fetched {len(df)} rows of WOOFi data:\n{df}\n")
    return df

def upload_to_dune(df):
    today_str = datetime.utcnow().strftime("%Y%m%d")
    table_name = f"nickzhang_woofi_metrics_{today_str}"
    url = "https://api.dune.com/api/v1/table/insert"

    payload = {
        "namespace": DUNE_NAMESPACE,
        "table_name": table_name,
        "rows": df.to_dict(orient="records")
    }

    headers = {
        "X-Dune-API-Key": DUNE_API_KEY,
        "Content-Type": "application/json"
    }

    print(f"Uploading to table: {DUNE_NAMESPACE}.{table_name}")
    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code == 200:
        print(f"Data uploaded successfully as {table_name}.")
    else:
        print(f"Upload failed ❌: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    df = get_woofi_metrics()
    upload_to_dune(df)
