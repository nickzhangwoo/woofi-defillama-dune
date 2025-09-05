import os
import requests
import pandas as pd
from datetime import datetime

# 读取 Dune API Key
DUNE_API_KEY = os.environ.get("DUNE_API_KEY")
if not DUNE_API_KEY:
    raise ValueError("DUNE_API_KEY is not set in environment variables.")

# DefiLlama API 基础 URL
BASE_URL = "https://api.llama.fi"

# WOOFi 各产品的协议 slug
protocols = ["woofi", "woofi-earn", "woofi-swap", "woofi-pro-perps"]

def get_woofi_metrics():
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
    # CSV 数据
    csv_data = df.to_csv(index=False)

    # 自动生成表名：nickzhang_前缀 + 日期
    table_name = f"nickzhang_woofi_metrics_{datetime.utcnow().strftime('%Y%m%d')}"

    payload = {
        "data": csv_data,
        "description": "WOOFi metrics daily data",
        "table_name": table_name,
        "is_private": False
    }

    headers = {
        "Content-Type": "application/json",
        "X-DUNE-API-KEY": DUNE_API_KEY
    }

    # 上传 API URL（企业版 Dune 支持）
    url = "https://api.dune.com/api/v1/table/upload/csv"
    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code == 200:
        print(f"Data uploaded successfully as {table_name}.")
    else:
        print(f"Upload failed ❌: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    df = get_woofi_metrics()
    print(f"Fetched {len(df)} rows of WOOFi data:")
    print(df)
    upload_to_dune(df)
