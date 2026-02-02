import cudf

MONTH_ABBR = {
    1: "jan", 2: "feb", 3: "mar", 4: "apr",
    5: "may", 6: "jun", 7: "jul", 8: "aug",
    9: "sep", 10: "oct", 11: "nov", 12: "dec"
}

def get_month_bounds(year, month, root):
    """
    Return north, south, east, west bounds
    from AIS CSV for a given year/month.
    """
    file_path = (
        f"{root}/unipi_ais_dynamic_{year}/"
        f"unipi_ais_dynamic_{MONTH_ABBR[month]}{year}.csv"
    )

    df = cudf.read_csv(file_path, usecols=["lat", "lon"])

    return {
        "north": float(df["lat"].max()),
        "south": float(df["lat"].min()),
        "east":  float(df["lon"].max()),
        "west":  float(df["lon"].min()),
    }


bounds = get_month_bounds(
    year=2017,
    month=5,
    root=r"/mnt/c/Users/BBBS-AI-01/d/anomaly/dataset/piraeus"
)

print(bounds)
