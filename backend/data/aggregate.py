# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

import pandas as pd
from datetime import datetime

from data.data_point import DataPoint, WorkoutData
from data.data_sources import DATA_SOURCES
from data.utils import filter_by_device
    
def aggregate(df, data_source, start, end, granularity, include_empty_buckets=False) -> list[DataPoint]:
    print(f"Aggregating data for {data_source} from {start} to {end} with granularity {granularity}")
    # get all time buckets for the given granularity
    if granularity == "15min":
        freq = "15min"
    elif granularity == "hour":
        freq = "H"
    elif granularity == "day":
        freq = "D"
    elif granularity == "week":
        freq = "W-SUN"
    elif granularity == "month":
        freq = "M"
    else:
        raise ValueError(f"Unsupported granularity: {granularity}")

    # Create time buckets
    time_buckets = pd.date_range(start=start, end=end, freq=freq)
    if granularity == "month":
        time_buckets = time_buckets + pd.Timedelta(days=1)
    if time_buckets[0] != start:  # Ensure the first bucket starts at the start time
        time_buckets = time_buckets.union([start])
    if time_buckets[-1] != end:  # Ensure the last bucket goes up to the end time
        time_buckets = time_buckets.union([end])
    
    aggregated_data = []
    for start_bucket, end_bucket in zip(time_buckets[:-1], time_buckets[1:]):
        data_bucket = df[(df['datetimeStart'] < end_bucket) & (df['datetimeEnd'] >= start_bucket)]
        if len(data_bucket) == 0:
            if include_empty_buckets:
                aggregated_data.append(
                    DataPoint(
                        start=start_bucket,
                        end=end_bucket - pd.Timedelta(seconds=1),
                        data_source=data_source,
                        data=[],
                        units=DATA_SOURCES[data_source].units,
                        device="unknown",
                        type=DATA_SOURCES[data_source].type
                    )
                )
            else:
                continue

        data_bucket, device_name = filter_by_device(data_bucket)

        if DATA_SOURCES[data_source].type == "count":
            if granularity >= "day":
                daily_averages = [list(g) for _, g in data_bucket.groupby(data_bucket['datetimeStart'].dt.date)['value']]
                aggregated_data.append(
                    DataPoint(
                        start=start_bucket,
                        end=end_bucket - pd.Timedelta(seconds=1),
                        data_source=data_source,
                        data=daily_averages,
                        units=DATA_SOURCES[data_source].units,
                        device=device_name,
                        type="count"
                    )
                )
            else:
                aggregated_data.append(
                    DataPoint(
                        start=start_bucket,
                        end=end_bucket - pd.Timedelta(seconds=1),
                        data_source=data_source,
                        data=list(data_bucket['value']),
                        units=DATA_SOURCES[data_source].units,
                        device=device_name,
                        type="count"
                    )
                )
        elif DATA_SOURCES[data_source].type == "rate":
            aggregated_data.append(
                DataPoint(
                    start=start_bucket,
                    end=end_bucket - pd.Timedelta(seconds=1),
                    data_source=data_source,
                    data=list(data_bucket['value']),
                    units=DATA_SOURCES[data_source].units,
                    device=device_name,
                    type="rate"
                )
            )
        elif DATA_SOURCES[data_source].type == "workout":
            # tuples of (start, end, duration, type)
            workout_data = [WorkoutData(
                start=row['datetimeStart'],
                end=row['datetimeEnd'],
                duration=(row['datetimeEnd'] - row['datetimeStart']).total_seconds(),
                type=row['value']
            ) for _, row in data_bucket.iterrows()]

            aggregated_data.append(
                DataPoint(
                    start=start_bucket,
                    end=end_bucket - pd.Timedelta(seconds=1),
                    data_source=data_source,
                    data=workout_data,
                    units=DATA_SOURCES[data_source].units,
                    device=device_name,
                    type="workout"
                )
            )
        else:
            raise ValueError(f"Unsupported data type: {DATA_SOURCES[data_source].type}")
        
    return aggregated_data