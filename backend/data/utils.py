# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta

from data.granularity import Granularity

def is_start_of_day(dt: datetime) -> bool:
    return dt.hour == 0 and dt.minute == 0 and dt.second == 0
def is_start_of_month(dt: datetime) -> bool:
    return dt.day == 1 and is_start_of_day(dt)
def is_start_of_year(dt: datetime) -> bool:
    return dt.month == 1 and is_start_of_month(dt)
def is_end_of_day(dt: datetime) -> bool:
    return dt.hour == 23 and dt.minute == 59 and dt.second == 59
def is_end_of_month(dt: datetime) -> bool:
    if not is_end_of_day(dt):
        return False
    next_day = dt + timedelta(days=1)
    return next_day.month != dt.month
def is_end_of_year(dt: datetime) -> bool:
    return dt.month == 12 and is_end_of_month(dt)

def dedupe(entries: list[dict]) -> list[dict]:
    """
    Deduplicate a list of entries by identifier
    """
    ids = set()
    deduped = []
    for entry in entries:
        if entry["id"] not in ids:
            deduped.append(entry)
            ids.add(entry["id"])
    return deduped

def reformat_entry(entry_dict: dict) -> dict:
    """
    Filters out unnecessary keys 
    """
    keys_to_keep = ["datetimeStart", "datetimeEnd", "device"]
    output_dict = {}
    for k, v in entry_dict.items():
        if k in keys_to_keep:
            output_dict[k] = v
        elif k == "valueQuantity":
            output_dict["value"] = v["value"]
        elif k == "valueCodeableConcept":
            output_dict["value"] = v["coding"][0]["code"]
    return output_dict

def data_to_df(data: list[dict]) -> pd.DataFrame:
    formatted_data = [reformat_entry(entry) for entry in data]
    df = pd.DataFrame(formatted_data, columns=["datetimeStart", "datetimeEnd", "device", "value"])
    df['datetimeStart'] = pd.to_datetime(df['datetimeStart'])
    df['datetimeEnd'] = pd.to_datetime(df['datetimeEnd'])
    return df

def filter_by_device(data: pd.DataFrame):
    if len(data) == 0:
        return data, "unknown"

    devices = data['device'].unique()
    devices = [s.lower() for s in devices]

    # if "watch" in any string, filter out all non-watch data
    if any("watch" in s for s in devices):
        data = data[data['device'].str.lower().str.contains("watch")]
        device = "Apple Watch"
    elif any("iphone" in s for s in devices):
        data = data[data['device'].str.lower().str.contains("iphone")]
        device = 'iPhone'
    else:
        # choose the most common device
        device = data['device'].mode()[0]
        data = data[data['device'] == device]
    return data, device

def round_datetime(dt: datetime, granularity: Granularity) -> datetime:
    # Round a datetime to the specified granularity (15min, day, week, month)

    if granularity == "15min":
        return dt.replace(minute=dt.minute - (dt.minute % 15), second=0, microsecond=0)
    elif granularity == "hour":
        return dt.replace(minute=0, second=0, microsecond=0)
    elif granularity == "day":
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    elif granularity == "week":
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        dt = dt - timedelta(days=dt.weekday() + 1)
        print(f"Rounded to week: {dt} (weekday: {dt.weekday()}")
        return dt
    elif granularity == "month":
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError(f"Invalid granularity {granularity}!")


def advance_datetime(dt: datetime, granularity: Granularity) -> datetime:
    # Advance the given datetime by granularity
    TIMEDELTAS = {
        "fifteenMinBucket": timedelta(minutes=15),
        "hour": timedelta(hours=1),
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": relativedelta(months=1)
    }
    
    return dt + TIMEDELTAS[str(granularity)]