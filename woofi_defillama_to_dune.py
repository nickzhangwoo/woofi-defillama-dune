import os
import requests
import pandas as pd
from datetime import datetime

# Dune 公司 API key（从 GitHub Secrets 里读取）
DUNE_API_KEY = os.environ.get("DUNE_API_KEY")

if not DUNE_API_KEY:
    raise ValueError("DUNE_API_KEY is not set in environment variables.")

# DefiLlama API endpoints
BASE_URL = "https://api.llama.fi"

# 上传到 Dune 的表信息
DUNE_TABLE_NAMESPACE = "woofianalytics"  # 公司 namespace
DUNE_TABLE_NAME = "nickzhang_woofi_metrics"  # 表名
DUNE_TABLE_FULL_NAME = f"dune.{DUNE_TABLE_NAMESPACE}.{DUNE_TABLE_NAME}"

def get_woofi_metrics():
    protocols = ["woofi-pro-perps", "woofi-swap", "woofi-earn"]
    data = []

    for protocol in protocols:
        url = f"{BASE_URL}/protocol/{protocol}"
        resp = requests.get(url)
        if resp.status_code == 200:
            info = resp.json()
            data.append({
                "protocol": info.get("name"),
                "tvl": info.get("tvl"),
                "volume_24h": info.get("volume_24h"),
                "fees_24h": info.get("fees_24h"),
                "users_24h": info.get("users_24h"),
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            print(f"Error fetching {protocol}: {resp.status_code}")

    return pd.DataFrame(data)

def upload_to_dune(df):
    url = "https://api.dune.com/api/v1/insert"
    headers = {"X-Dune-API-Key": DUNE_API_KEY}
    payload = {
        "table_name": DUNE_TABLE_NAME,
        "namespace": DUNE_TABLE_NAMESPACE,
        "data": df.to_dict(orient="records")
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        print("Upload successful ✅")
    else:
        print(f"Upload failed ❌: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    df = get_woofi_metrics()
    print(f"Fetched {len(df)} rows of WOOFi data:")
    print(df)
    upload_to_dune(df)
