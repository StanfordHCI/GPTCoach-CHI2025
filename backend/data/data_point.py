# SPDX-FileCopyrightText: 2025 Stanford University
#
# SPDX-License-Identifier: MIT

# Model for a data point, representing a reading from a data series over a time interval
# Represents values of the "rate" or "count" types

from datetime import datetime
from typing import Literal, Optional, Union
import numpy as np
from pydantic import BaseModel, computed_field

class WorkoutData(BaseModel):
    start: datetime
    end: datetime
    duration: float # in seconds
    type: str

class DataPoint(BaseModel):
    # The start and end of the reading
    # (may be identical if this represents a single point in time)
    start: datetime
    end: datetime

    # The data source that this reading comes from
    data_source: str

    # The numeric value of the data (int/float) or the type of workout activity (str)
    data: list[Union[float, int, WorkoutData]] | list[list[Union[float, int]]] | None

    # The units of the data
    units: str
    # The device that recorded the data
    device: str
    # The aggregation type of the data
    type: Literal["count", "rate", "workout"]

    # Property to find duration in hours
    @computed_field
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600
    
    @computed_field
    def value(self) -> Optional[float]:
        if self.is_daily_count:
            return np.mean([np.sum(d) for d in self.data])
        elif (self.type == "rate" and len(self.data) > 1):
            return np.mean(self.data)
        elif (self.type == "count") or (self.type == "rate" and len(self.data) == 1):
            return np.sum(self.data)
        elif len(self.data) == 0:
            return None
        else:
            raise ValueError(f"Invalid data type {self.type} and data {self.data}")
        
    @computed_field
    def maximum(self) -> Optional[float]:
        if self.type == "rate" and len(self.data) > 1:
            return np.max(self.data)
        elif self.is_daily_count:
            return np.max([np.sum(d) for d in self.data])
        else:
            return self.value
    
    @computed_field
    def minimum(self) -> Optional[float]:
        if self.type == "rate" and len(self.data) > 1:
            return np.min(self.data)
        elif self.is_daily_count:
            return np.min([np.sum(d) for d in self.data])
        else:
            return self.value
        
    @computed_field
    def is_daily_count(self) -> bool:
        if len(self.data) == 0:
            return False
        return self.type == "count" and type(self.data[0]) == list
        
    def __len__(self):
        if self.is_daily_count:
            return sum([len(d) for d in self.data])
        else:
            return len(self.data)
      
    def __str__(self):
        time_str = f"{self.start.strftime('%a, %Y-%m-%d:%H:%M:%S')} to {self.end.strftime('%a, %Y-%m-%d:%H:%M:%S')}: "
        if len(self) == 0:
            return time_str + f"No data from {self.device}"
        elif (self.type == "rate" and len(self.data) > 1):
            mean = np.mean(self.data)
            std = np.std(self.data)
            max, min = np.max(self.data), np.min(self.data)
            n = len(self)
            return time_str + f"{mean:.2f}±{std:.2f} ({min:.2f}-{max:.2f}) {self.units} from {self.device} ({n} entries)"
        elif self.is_daily_count:
            n = len(self)
            std = np.std([np.sum(d) for d in self.data])
            max, min = self.maximum, self.minimum
            return time_str + f"{self.value:.2f}±{std:.2f} ({min:.2f}-{max:.2f}) {self.units} from {self.device} ({n} entries)"
        elif (self.type == "count") or (self.type == "rate" and len(self.data) == 1):
            n = len(self)
            return time_str + f"{sum(self.data):.2f} {self.units} from {self.device} ({n} entries)"
        elif self.type == "workout":
            n = len(self)
            base_str = time_str + f"{n} workouts from {self.device}"
            workout_groups = {}
            for workout in self.data:
                if workout.type not in workout_groups:
                    workout_groups[workout.type] = []
                workout_groups[workout.type].append(workout.duration)

            # add summary of workout types
            for workout_type, durations in workout_groups.items():
                mean_duration_mins = np.mean(durations) / 60
                total_duration_mins = np.sum(durations) / 60
                total_duration_hours = np.sum(durations) / 3600
                duration_hour_str = f" ({int(total_duration_hours)}h{int(total_duration_mins % 60)}m) " if total_duration_hours >= 1 else f""

                base_str += f"\n - {workout_type}: {len(durations)} workouts, {mean_duration_mins:.2f} mins/workout, {total_duration_mins:.2f} mins {duration_hour_str} total"

            return base_str
        else:
            raise ValueError(f"Could not aggregate data for type {self.type} and data {self.data}")
        
    def __repr__(self):
        return self.__str__()
