# marine_backend/routes/predict_trajectory.py
from fastapi import APIRouter, Query

from marine_backend.core.readers import read_time_window

router = APIRouter()


from pathlib import Path
import pandas as pd
from autogluon.timeseries import TimeSeriesPredictor, TimeSeriesDataFrame


def load_predictors(model_dir: Path):
    """
    Load pretrained Chronos-2 predictors.
    """
    return (
        TimeSeriesPredictor.load(model_dir / "lat"),
        TimeSeriesPredictor.load(model_dir / "lon"),
    )


def load_jan_2018(csv_dir: Path) -> TimeSeriesDataFrame:
    """
    Load January 2018 AIS data into TimeSeriesDataFrame.
    """
    files = sorted(csv_dir.glob("*jan2018*.csv"))
    df = pd.concat(pd.read_csv(f) for f in files)

    df = df.sort_values(["vessel_id", "timestamp"])

    return TimeSeriesDataFrame.from_data_frame(
        df[["vessel_id", "timestamp", "lat", "lon"]],
        id_column="vessel_id",
        timestamp_column="timestamp",
    )


def predict(ts_df, lat_model, lon_model) -> pd.DataFrame:
    """
    Predict latitude and longitude.
    """
    lat = lat_model.predict(ts_df)["mean"]
    lon = lon_model.predict(ts_df)["mean"]

    out = lat.to_frame("lat")
    out["lon"] = lon
    return out


t = {"actual" : None,"predicted" : None}
@router.get("/predict_trajectory")
def predict_trajectory(file: str, start_ts: int = Query(-10**18), end_ts: int = Query(10**18), vessel_id: str = Query(...)):
    """
    End-to-end evaluation.
    """
    MODEL_DIR = Path("../models")

    lat_model, lon_model = load_predictors(MODEL_DIR)
    df = read_time_window(file, start_ts, end_ts)

    pred = predict(df, lat_model, lon_model)
    
    if vessel_id is None:
        vessel_id = df.index.get_level_values(0)[0]

    t["actual"] = df.loc[vessel_id][["lat", "lon"]]
    t["predicted"] = pred.loc[vessel_id]

    return (t["actual"], t["predicted"], vessel_id)
