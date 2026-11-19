"""Turn raw OpenF1 laps + stints into a model-ready lap table."""
import pandas as pd

COMPOUNDS = {"SOFT", "MEDIUM", "HARD"}


def build_laps(laps: pd.DataFrame, stints: pd.DataFrame) -> pd.DataFrame:
    """Attach compound and tyre age to every lap by joining laps to stints."""
    stints = stints.copy()
    last_lap = int(laps["lap_number"].max())
    stints["lap_end"] = stints["lap_end"].fillna(last_lap)
    stints["is_last_stint"] = (
        stints["stint_number"] == stints.groupby("driver_number")["stint_number"].transform("max")
    )

    df = laps.merge(stints, on=["meeting_key", "session_key", "driver_number"], how="inner")
    df = df[(df["lap_number"] >= df["lap_start"]) & (df["lap_number"] <= df["lap_end"])].copy()

    # Tyre age = laps already on the set at stint start + laps into this stint.
    df["tyre_age"] = df["tyre_age_at_start"].fillna(0) + (df["lap_number"] - df["lap_start"])
    df["is_in_lap"] = (df["lap_number"] == df["lap_end"]) & ~df["is_last_stint"]
    df["laps_remaining"] = last_lap - df["lap_number"]   # fuel-load proxy
    df["compound"] = df["compound"].str.upper()
    return df


def filter_laps(df: pd.DataFrame) -> pd.DataFrame:
    """Drop laps that don't reflect clean tyre-limited pace."""
    df = df[df["lap_duration"].notna()]
    df = df[~df["is_pit_out_lap"].fillna(False)]
    df = df[~df["is_in_lap"]]
    df = df[df["lap_number"] > 1]
    df = df[df["compound"].isin(COMPOUNDS)]
    return df