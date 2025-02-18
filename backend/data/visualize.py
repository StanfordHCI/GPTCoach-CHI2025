# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

# This file defines functions for visualizing data sources

from typing import Literal

import pytz
from datetime import datetime
from async_lru import alru_cache

from data.fetch import fetch_aggregated_data
from data.data_sources import DATA_SOURCES
from data.granularity import Granularity
from data.utils import *

@alru_cache(maxsize=128)
async def generate_vizualization(user_id: str, 
                                 data_source_name: str, 
                                 date_str: str = "", 
                                 granularity: Literal["day", "week", "month"] = "day") -> tuple[str, dict]:
    """
    Generate json (for the frontend) and text (for GPT) for a visualization of the given series
    for the given user

    - user_id: the user's Firebase ID (str)
    - source: the name of the data source (str), e.g., "health.stepcount"
    - date_str: the date to visualize (str: "YYYY-MM-DDTHH:MM:SS" or "YYYY-MM-DD"). If no time is specified, today's date is used.
    - granularity: the granularity of the time buckets to aggregate the data into (str: "day", "week", "month")
    """
    if data_source_name not in DATA_SOURCES:
        raise ValueError(f"Data source '{data_source_name}' not found")
    # elif data_source_name == "health.workout":
    #     raise ValueError("Workouts are not supported for visualization")
    else:
        data_source = DATA_SOURCES[data_source_name]
    
    granularity = Granularity(granularity)
    if granularity < "day":
        raise ValueError(f"Granularity '{granularity}' is too fine: (should be 'day', 'week', or 'month')")

    # TODO: get the user's actual timezone
    date = pd.to_datetime(date_str) if date_str else datetime.now(tz=pytz.timezone("US/Pacific"))

    # Generate JSON description
    if data_source_name != "health.workout":
        viz_json = {
            "type": "visualization",

            "name": data_source_name,
            "data_type": data_source.type,
            "unit": data_source.units,

            "granularity": granularity.value,
            "date": date.date().isoformat(),
        }
    else:
        viz_json = None

    # Generate text
    start = round_datetime(date, granularity)
    end = advance_datetime(start, granularity)

    start_str = start.date().isoformat() #.rsplit("-", 1)[0]  # remove the timezone (e.g., "-07:00")
    end_str = end.date().isoformat() #.rsplit("-", 1)[0]  # remove the timezone (e.g., "-07:00")

    if start.date() == end.date():
        viz_text = f"{data_source.name} ({data_source.description}) on {start_str} is now being shown to the user."
    else:
        viz_text = f"{data_source.name} ({data_source.description}) from {start_str} to {end_str} is now being show to the user."

    # Add summary text
    print(f"Visualize: fetching data for {user_id} from {start_str} to {end_str} with granularity {granularity}")
    aggregated_data, description_string = await fetch_aggregated_data(user_id, data_source_name, start_str, end_str, granularity.value)
    viz_text += "\n" + description_string
    return viz_text, viz_json

