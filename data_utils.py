import pandas as pd


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )
    return df


def read_table(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    except Exception:
        df = pd.read_csv(path, sep="\t", encoding="utf-8-sig")
    return clean_columns(df)


def load_project_data():
    projects = read_table("data/projects_master.csv")
    matrix = read_table("data/improvement_matrix_features.csv")

    # Rename columns in projects_master
    projects = projects.rename(columns={
        "SMART SCALE Round": "SMARTSCALE_Round",
        "Area Type": "AreaType",
        "Principal Improvement Type": "PrincipalImprovementType",
        "Total Expenditures as of July 2025": "TotalExpenditures",
        "Construction District": "District",
        "Construction Begin": "ConstructionBegin",
        "Construction End": "ConstructionEnd",
        "Road System": "RoadSystem",
        "Project Category": "ProjectCategory",
        "Innovative Intersection/Interchange Configuration": "InnovativeConfig",
        "No Data Flag Congestion": "NoDataFlagCongestion",
        "No Method Flag Congestion": "NoMethodFlagCongestion",
        "Peak Period for Congestion and Reliability Analysis": "PeakPeriod",
        "Before Year for Congestion and Reliability Measures": "BeforeYear",
        "After Year for Congestion and Reliability Measures": "AfterYear",
        "Average Delay % Change": "AvgDelayPctChange",
        "Average Delay Before (hours per 1000 veh)": "AvgDelayBefore",
        "Average Delay After (hours per 1000 veh)": "AvgDelayAfter",
        "Average Delay Change (hours per 1000 veh)": "AvgDelayChange",
        "Average Speed % Change": "AvgSpeedPctChange",
        "Average Speed Before (mph)": "AvgSpeedBefore",
        "Average Speed After (mph)": "AvgSpeedAfter",
        "Average Speed Change (mph)": "AvgSpeedChange",
        "PTI % Change": "PTIPctChange",
        "PTI Before": "PTIBefore",
        "PTI After": "PTIAfter",
        "PTI Change": "PTIChange",
        "BTI % Change": "BTIPctChange",
        "BTI Before": "BTIBefore",
        "BTI After": "BTIAfter",
        "BTI Change": "BTIChange",
        "TTI % Change": "TTIPctChange",
        "TTI Before": "TTIBefore",
        "TTI After": "TTIAfter",
        "TTI Change": "TTIChange",
        "LOTTR % Change": "LOTTRPctChange",
        "LOTTR Before": "LOTTRBefore",
        "LOTTR After": "LOTTRAfter",
        "LOTTR Change": "LOTTRChange",
        "Average VMT % Change": "VMTPctChange",
        "Average VMT Before": "VMTBefore",
        "Average VMT After": "VMTAfter",
        "Average VMT Change": "VMTChange",
        "Average VHT % Change": "VHTPctChange",
        "Average VHT Before": "VHTBefore",
        "Average VHT After": "VHTAfter",
        "Average VHT Change": "VHTChange",
    })

    # Basic checks
    if "AppID" not in projects.columns:
        raise ValueError(f"projects_master.csv missing AppID. Columns found: {projects.columns.tolist()}")
    if "AppID" not in matrix.columns:
        raise ValueError(f"improvement_matrix_features.csv missing AppID. Columns found: {matrix.columns.tolist()}")

    # Merge
    df = projects.merge(matrix, on="AppID", how="left", suffixes=("", "_matrix"))

    # Numeric conversion for commonly used fields
    numeric_cols = [
        "AvgDelayBefore", "AvgDelayAfter", "AvgDelayChange",
        "AvgSpeedBefore", "AvgSpeedAfter", "AvgSpeedChange",
        "PTIBefore", "PTIAfter", "PTIChange",
        "BTIBefore", "BTIAfter", "BTIChange",
        "TTIBefore", "TTIAfter", "TTIChange",
        "LOTTRBefore", "LOTTRAfter", "LOTTRChange",
        "VMTBefore", "VMTAfter", "VMTChange",
        "VHTBefore", "VHTAfter", "VHTChange",
        "AADT", "PeakHourVolume", "DirectionalVolume",
        "ImprovementTypeCount"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convenience fields
    if "ImprovementTypeCount" in df.columns and "SingleTreatmentProject" not in df.columns:
        df["SingleTreatmentProject"] = df["ImprovementTypeCount"].apply(
            lambda x: "Yes" if pd.notna(x) and x == 1 else ("No" if pd.notna(x) else "")
        )

    if "FacilityType" in df.columns and "DominantImprovementType" in df.columns:
        df["OMFGroup"] = (
            df["FacilityType"].fillna("").astype(str) + " | " +
            df["DominantImprovementType"].fillna("").astype(str)
        ).str.strip(" |")

    return df