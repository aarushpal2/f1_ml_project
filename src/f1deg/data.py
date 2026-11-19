"""Download race data from OpenF1 and cache it to data/raw/ as parquet."""
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://api.openf1.org/v1"
RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
SLEEP = 2.5  # seconds between calls, stays under 30 requests/min
ENDPOINTS = ["laps", "stints", "pit", "race_control", "drivers"]


def _get(endpoint: str, **params) -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(f"{BASE}/{endpoint}", params=params, timeout=60)
        if r.status_code == 429:               # rate limited: back off and retry
            time.sleep(10 * (attempt + 1))
            continue
        if r.status_code == 404:               # no results
            return pd.DataFrame()
        r.raise_for_status()
        time.sleep(SLEEP)
        data = r.json()
        return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()
    raise RuntimeError(f"Rate limited too many times on {endpoint} {params}")


def fetch_year(year: int, limit: int | None = None) -> None:
    """Download every race of a season (or the first `limit` races) to data/raw/<year>/."""
    sessions = _get("sessions", year=year, session_name="Race")
    out_root = RAW / str(year)
    out_root.mkdir(parents=True, exist_ok=True)
    sessions.to_parquet(out_root / "sessions.parquet")
    if limit:
        sessions = sessions.head(limit)

    for _, s in sessions.iterrows():
        key = int(s["session_key"])
        out = out_root / str(key)
        if out.exists() and all((out / f"{e}.parquet").exists() for e in ENDPOINTS):
            continue                              # already downloaded, so resume safely
        out.mkdir(exist_ok=True)
        print(f"{year} {s['country_name']} (session {key})")
        for e in ENDPOINTS:
            df = _get(e, session_key=key)
            df = df.drop(columns=[c for c in df.columns if c.startswith("segments")])
            df.to_parquet(out / f"{e}.parquet")


def load_session(year: int, session_key: int) -> dict[str, pd.DataFrame]:
    folder = RAW / str(year) / str(session_key)
    return {e: pd.read_parquet(folder / f"{e}.parquet") for e in ENDPOINTS}