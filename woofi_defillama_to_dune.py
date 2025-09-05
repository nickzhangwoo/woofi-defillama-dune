import os
import requests
import pandas as pd
from datetime import datetime

# -------------------------------
# 公司 Enterprise Dune API 配置
# -------------------------------
DUNE_API_KEY = "Vg96yb9PuDnP5LG4NhRPSKyZNFL69Z3k"  # 公司 API token
NAMESPACE = "woofianalytics"
TABLE_NAME = "nickzhang_woofi_metrics"

# -------------------------------
# DefiLlama API 配置
# -------------------------------
BASE_URL = "https://api.llama.fi"
PROTOCOLS = ["woofi-pro-perps", "woofi-swap", "woofi-earn"]

# -------------------------------
# 获取 WOOFi 数据
# -------------------------------
def get_woofi_metrics():
    data = []
    for protocol in PROTOCOLS:
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

# -------------------------------
# 上传数据到 Dune Enterprise 表
# -------------------------------
def upload_to_dune(df):
    url = f"https://api.dune.com/api/v1/table/insert"
    headers = {
        "X-DUNE-API-KEY": DUNE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "namespace": NAMESPACE,
        "table_name": TABLE_NAME,
        "rows": df.to_dict(orient="records")
    }

    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        print("✅ Upload successful")
    else:
        print(f"❌ Upload failed: {resp.status_code} {resp.text}")

# -------------------------------
# 主程序
# -------------------------------
if __name__ == "__main__":
    df = get_woofi_metrics()
    print(f"Fetched {len(df)} rows of WOOFi data:")
    print(df)
    upload_to_dune(df)
