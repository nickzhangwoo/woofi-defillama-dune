import os
import requests
import pandas as pd
from datetime import datetime

# 读取 Dune API Key
DUNE_API_KEY = os.environ.get("DUNE_API_KEY")

if not DUNE_API_KEY:
    raise ValueError("DUNE_API_KEY is not set in environment variables.")

# DefiLlama API endpoints
BASE_URL = "https://api.llama.fi"

def get_woofi_metrics():
    # 获取 WOOFi 各个产品数据
    protocols = ["woofi-pro", "woofi-swap", "woofi-earn"]
    data = []

    for protocol in protocols:
        url = f"{BASE_URL}/protocol/{protocol}"
        resp = requests.get(url)
        if resp.status_code == 200:
            info = resp.json()
            # 收集部分你需要的数据示例
            data.append({
                "protocol": protocol,
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
    # 这里是上传到 Dune 的示例
    # 你可以改成真实的 Dune API 上传逻辑
    headers = {"X-Dune-API-Key": DUNE_API_KEY}
    url = "https://api.dune.com/api/v1/dataset/upload"
    payload = df.to_dict(orient="records")
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        print("Upload successful")
    else:
        print(f"Upload failed: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    df = get_woofi_metrics()
    print(df)
    upload_to_dune(df)
