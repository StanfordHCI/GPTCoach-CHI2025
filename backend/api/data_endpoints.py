# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

# This file contains functionality for getting actual data from firebase
from fastapi import APIRouter
from datetime import datetime

from typing import Literal

from data.utils import round_datetime, advance_datetime
from data.data_point import DataPoint
from data.fetch import fetch_aggregated_data

router = APIRouter(prefix="/data")

# API endpoint functions -----------------------------------------------------------------------
@router.get("/")
async def get_featurized_data(series: str, 
                              user_id: str, 
                              date: str, 
                              granularity: str
                              ) -> list[DataPoint]:
    # API endpoint to expose `data_fetch_utils.fetch_featurized_data`

    print(f"Calling get_featurized_data with args: series={series}, user_id={user_id}, date={date}, granularity={granularity}")
    date = datetime.fromisoformat(date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    start = round_datetime(date, granularity)
    end = advance_datetime(start, granularity)

    start_str = start.date().isoformat()
    end_str = end.date().isoformat()

    if granularity == "day":
        agg_granularity = "15min"
    elif granularity == "week":
        agg_granularity = "day"
    elif granularity == "month":
        agg_granularity = "day"

    print(f"Data endpoint: fetching data for {user_id} from {start_str} to {end_str} with granularity {granularity} at aggregation level {agg_granularity}")
    aggregated_data, description_string = await fetch_aggregated_data(user_id, series, start_str, end_str, agg_granularity, include_empty_buckets=True)
    return aggregated_data