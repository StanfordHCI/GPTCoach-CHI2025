# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

from typing import Literal
from async_lru import alru_cache
from datetime import datetime, timedelta
import time
from google.cloud.firestore_v1.base_query import FieldFilter
# from utils import *

from data.aggregate import aggregate
from data.data_point import DataPoint
from data.data_sources import get_user_data_sources
from data.granularity import adjust_date_and_granularity, Granularity
from data.utils import *

from firebase import FirebaseManager
firebase_manager = FirebaseManager()

@alru_cache(maxsize=128)
async def fetch_aggregated_data(user_id: str, 
                                data_source: str, 
                                start: str, 
                                end: str, 
                                granularity: Literal["15min", "hour", "day", "week", "month"],
                                include_empty_buckets: bool = False) -> tuple[list[DataPoint], str]:
    """
    Fetch aggregated data for a given user, data source, and time range
    - user_id: the user's Firebase ID (str)
    - data_source: the name of the data source (str), e.g., "health.stepcount"
    - start: the start of the time range in a YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format (str). If no time is specified, the function interprets the start date as the beginning of the day.
    - end: the start of the time range in a YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format (str). The end is exclusive, i.e., data is fetched up to but not including this date/datetime.
    - granularity: the granularity of the time buckets to aggregate the data into (str: "15min", "hour", "day", "week", "monthStart"). For example, if the granularity is 'hour', the function will return the data aggregated into hourly buckets. If the granularity is 'week', the function will return the data aggregated into weekly buckets. Note that a week is defined as starting on Sunday and ending on Saturday.

    Returns: a tuple containing the aggregated data (list of DataPoint objects) and a description string
    """
    print(f"Calling fetch_aggregated_data with args: user_id={user_id}, data_source={data_source}, start={start}, end={end}, granularity={granularity}")

    user_data_sources = get_user_data_sources(user_id)
    if data_source not in user_data_sources:
        raise ValueError(f"Data source '{data_source}' not found for user '{user_id}'")
    
    start, end, granularity = adjust_date_and_granularity(start, end, granularity)
    assert start < end, f"Invalid date range: {start} to {end}. Start date must be before end date."

    
    time1 = time.time()
    data = await fetch_raw_data(user_id, data_source, start, end)
    time2 = time.time()
    if len(data) == 0:
        raise ValueError(f"No data found for {data_source} for user {user_id} from {start} to {end}")
    df = data_to_df(data)
    time3 = time.time()
    aggregated_data = aggregate(df, data_source, start, end, granularity, include_empty_buckets)
    time4 = time.time()

    # fix times to only show seconds
    print("Time taken to fetch raw data:", time2 - time1)
    print("Time taken to convert data to df:", time3 - time2)
    print("Time taken to aggregate data:", time4 - time3)

    description_string = f"Here is a summary of the data for {data_source} from {start} to {end} at a granularity of {granularity}:\n"
    for data_point in aggregated_data:
        description_string += str(data_point) + "\n"

    return aggregated_data, description_string

@alru_cache(maxsize=128)
async def fetch_raw_data(user_id: str, 
                         data_source_name: str, 
                         start: datetime, 
                         end: datetime) -> list[dict]:
    """
    Fetch raw data from Firestore for a given user, data source, and time range
    - user_id: the user's Firebase ID (str)
    - data_source_name: the name of the data source (str), e.g., "health.stepcount"
    - start: the start of the time range (datetime)
    - end: the end of the time range (datetime). The end date is exclusive, i.e., data is fetched up to but not including this date/datetime.

    Returns: a list of dictionaries, where each dictionary represents a Firestore document
    """
    print(f"Calling fetch_raw_data with args: user_id={user_id}, data_source_name={data_source_name}, start={start}, end={end}")
    module, data_source = data_source_name.split(".")
    try:
        user_doc = firebase_manager.get_user_doc(user_id, async_ref=True)
        collection = user_doc.collection(module).document(data_source).collection("raw")
        # verify that collection exists
        snapshot = await collection.limit(1).get()
        if not snapshot:
            raise ValueError(f"Collection {module}.{data_source}.raw does not exist for user {user_id}")
    except Exception as e:
        print(f"Error fetching data source collection: {e}")
        return []
    
    end -= timedelta(microseconds=1) # end date is exclusive

    # TODO: expand query for sleep data

    if start.year != end.year:
        print("Case: different years")
        if is_start_of_year(start) and is_end_of_year(end):
            print("\tCase: single query")
            print(f"\twhere: yearRange contains {list(range(start.year, end.year+1))}")
            query = collection.where(filter=FieldFilter("yearRange", "array_contains_any", list(range(start.year, end.year+1))))
            return [doc.to_dict() async for doc in query.stream()]
        else:
            print("\tCase: split queries")
            set1 = await fetch_raw_data(user_id, data_source_name, start, datetime(start.year+1, 1, 1, 0, 0))
            if start.year + 1 != end.year:
                set2 = await fetch_raw_data(user_id, data_source_name, datetime(start.year+1, 1, 1, 0, 0), datetime(end.year, 1, 1, 0, 0))
            else:
                set2 = []
            set3 = await fetch_raw_data(user_id, data_source_name, datetime(end.year, 1, 1, 0, 0), end)
        
            return dedupe(set1 + set2 + set3)
        
    elif start.month != end.month:
        print("Case: different months")
        if is_start_of_month(start) and is_end_of_month(end):
            print("\tCase: single query")
            print(f"\twhere: yearStart == {start.year} AND monthRange contains {start.month}")
            query = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                              .where(filter=FieldFilter("monthRange", "array_contains_any", list(range(start.month, end.month+1))))
            return [doc.to_dict() async for doc in query.stream()]
        else:
            print("\tCase: split queries")
            set1 = await fetch_raw_data(user_id, data_source_name, start, datetime(start.year, start.month+1, 1, 0, 0))
            if start.month + 1 != end.month:
                set2 = await fetch_raw_data(user_id, data_source_name, datetime(start.year, start.month+1, 1, 0, 0), datetime(end.year, end.month, 1, 0, 0))
            else:
                set2 = []
            set3 = await fetch_raw_data(user_id, data_source_name, datetime(end.year, end.month, 1, 0, 0), end)
            return dedupe(set1 + set2 + set3)
        
    elif start.day != end.day:
        print("Case: different days", is_start_of_day(start), is_end_of_day(end))
        if is_start_of_day(start) and is_end_of_day(end):
            print("\tCase: single query")
            print(f"\twhere: yearStart == {start.year} AND monthStart == {start.month} AND dayRange contains {start.day} AND dayStart >= {start.day} AND dayStart < {end.day}")
            
            query1 = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                               .where(filter=FieldFilter("monthStart", "==", start.month)) \
                               .where(filter=FieldFilter("dayStart", ">=", start.day)) \
                               .where(filter=FieldFilter("dayStart", "<", end.day))
            query2 = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                               .where(filter=FieldFilter("monthStart", "==", start.month)) \
                               .where(filter=FieldFilter("dayRange", "array_contains", start.day))

            return [doc.to_dict() async for doc in query1.stream()] + [doc.to_dict() async for doc in query2.stream()]
        else:
            print("\tCase: split queries")
            day_after_start = datetime(start.year, start.month, start.day, 0, 0) + timedelta(days=1)
            set1 = await fetch_raw_data(user_id, data_source_name, start, day_after_start)
            if start.day + 1 != end.day:
                set2 = await fetch_raw_data(user_id, data_source_name, day_after_start, datetime(end.year, end.month, end.day, 0, 0))
            else:
                set2 = []
            set3 = await fetch_raw_data(user_id, data_source_name, datetime(end.year, end.month, end.day, 0, 0), end)
            return dedupe(set1 + set2 + set3)
        
    else:
        print("Case: same day")
        if is_start_of_day(start) and is_end_of_day(end):
            print("\tCase: whole day")
            print(f"\twhere: yearStart == {start.year} AND monthStart == {start.month} AND dayStart == {start.day}")
            query = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                              .where(filter=FieldFilter("monthStart", "==", start.month)) \
                              .where(filter=FieldFilter("dayStart", "==", start.day)) 
            return [doc.to_dict() async for doc in query.stream()]

        print("\tCase: intraday")
        start_15min_bucket = (start.hour * 60 + start.minute) // 15
        end_15min_bucket = (end.hour * 60 + end.minute) // 15
        if start_15min_bucket != end_15min_bucket:
            print("\t\tCase: multiple 15min buckets")
            print(f"\t\twhere: yearStart == {start.year} AND monthStart == {start.month} AND dayStart == {start.day} AND fifteenMinBucketStart >= {start_15min_bucket} AND fifteenMinBucketStart < {end_15min_bucket} AND fifteenMinBucketRange contains {start_15min_bucket}")
            query1 = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                              .where(filter=FieldFilter("monthStart", "==", start.month)) \
                              .where(filter=FieldFilter("dayStart", "==", start.day)) \
                              .where(filter=FieldFilter("fifteenMinBucketStart", ">=", start_15min_bucket)) \
                              .where(filter=FieldFilter("fifteenMinBucketStart", "<", end_15min_bucket))
            
            query2 = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                               .where(filter=FieldFilter("monthStart", "==", start.month)) \
                               .where(filter=FieldFilter("dayStart", "==", start.day)) \
                               .where(filter=FieldFilter("fifteenMinBucketRange", "array_contains", start_15min_bucket))
            return [doc.to_dict() async for doc in query1.stream()] + [doc.to_dict() async for doc in query2.stream()]
        else:
            print("\t\tCase: single 15min bucket")
            print(f"\t\twhere: yearStart == {start.year} AND monthStart == {start.month} AND dayStart == {start.day} AND fifteenMinBucket == {start_15min_bucket}")
            query = collection.where(filter=FieldFilter("yearStart", "==", start.year)) \
                              .where(filter=FieldFilter("monthStart", "==", start.month)) \
                              .where(filter=FieldFilter("dayStart", "==", start.day)) \
                              .where(filter=FieldFilter("fifteenMinBucket", "==", start_15min_bucket))
            return [doc.to_dict() async for doc in query.stream()]