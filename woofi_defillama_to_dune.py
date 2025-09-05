import os
import requests
import pandas as pd
from datetime import datetime

# 读取 Dune API Key
DUNE_API_KEY = os.environ.get("DUNE_API_KEY")

if not DUNE_API_KEY:
    raise ValueError("DUNE_API_KEY is not set in environment variables.")

BASE_URL = "https://api.llama.fi"

def get_protocol_data(slug):
    url = f"{BASE_URL}/protocol/{slug}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Error fetching {slug}: {resp.status_code}")
        return None
    return resp.json()

def get_woofi_metrics():
    # 定义 WOOFi 产品
    protocols = [
        {"slug": "woofi", "type": "main"},
        {"slug": "woofi-earn", "type": "earn"},
        {"slug": "woofi-swap", "type": "swap"},
        {"slug": "woofi-pro-perps", "type": "pro-perps"}
    ]

    data = []

    for p in protocols:
        info = get_protocol_data(p["slug"])
        if info is None:
            continue

        # 对于 Pro Perps，没有 TVL/volume，只存基本信息
        if p["type"] == "pro-perps":
            data.append({
                "protocol": info.get("name"),
                "type": p["type"],
                "tvl": None,
                "volume_24h": None,
                "fees_24h": None,
                "users_24h": None,
                "parentProtocol": info.get("parentProtocolSlug"),
                "chains": ",".join(info.get("chains", [])),
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            data.append({
                "protocol": info.get("name"),
                "type": p["type"],
                "tvl": info.get("tvl"),
                "volume_24h": info.get("volume_24h"),
                "fees_24h": info.get("fees_24h"),
                "users_24h": info.get("users_24h"),
                "parentProtocol": info.get("parentProtocolSlug"),
                "chains": ",".join(info.get("chains", [])),
                "timestamp": datetime.utcnow().isoformat()
            })

    return pd.DataFrame(data)

def upload_to_dune(df):
    # 上传到 Dune（示例，需确认 endpoint 是否正确）
    headers = {"X-Dune-API-Key": DUNE_API_KEY}
    url = "https://api.dune.com/api/v1/dataset/upload"
    payload = df.to_dict(orient="records")
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
