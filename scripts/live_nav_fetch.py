import os
import time
import requests
import pandas as pd

API_BASE = "https://api.mfapi.in/mf/"
OUTPUT_DIR = os.path.join("data", "raw", "live_nav")

ANCHOR_SCHEME = {"code": 125497, "label": "ANCHOR_HDFC_Top100"}

SCHEMES = [
    {"code": 119551, "label": "SBI_Bluechip"},
    {"code": 120503, "label": "ICICI_Bluechip"},
    {"code": 118632, "label": "Nippon_LargeCap"},
    {"code": 119092, "label": "Axis_Bluechip"},
    {"code": 120841, "label": "Kotak_Bluechip"},
]

def fetch_scheme_nav(scheme_code):
    url = f"{API_BASE}{scheme_code}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

def save_as_csv(payload, scheme_code, label):
    meta = payload.get("meta", {})
    records = payload.get("data", [])

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"No NAV data returned for scheme {scheme_code}")

    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df["nav"] = df["nav"].astype(float)
    df = df.sort_values("date")

    df.insert(0, "amfi_code", scheme_code)
    df.insert(1, "scheme_name", meta.get("scheme_name"))
    df.insert(2, "fund_house", meta.get("fund_house"))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"nav_{scheme_code}_{label}.csv")
    df.to_csv(out_path, index=False)
    return out_path

def main():
    print("=" * 70)
    print("LIVE NAV FETCH - mfapi.in")
    print("=" * 70)

    targets = [ANCHOR_SCHEME] + SCHEMES
    results = []

    for target in targets:
        code, label = target["code"], target["label"]
        try:
            payload = fetch_scheme_nav(code)
            real_name = payload.get("meta", {}).get("scheme_name", "Unknown")
            path = save_as_csv(payload, code, label)
            n_rows = len(payload.get("data", []))
            print(f"[OK] code={code} ({label}) -> real scheme: '{real_name}' | {n_rows} rows -> {path}")
            results.append((code, label, real_name, n_rows, "OK"))
        except Exception as exc:
            print(f"[FAIL] code={code} ({label}) -> {exc}")
            results.append((code, label, None, 0, f"FAILED: {exc}"))
        time.sleep(0.5)

    print("=" * 70)
    summary = pd.DataFrame(results, columns=["amfi_code", "label", "real_scheme_name", "rows", "status"])
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
