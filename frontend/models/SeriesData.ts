// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// THIS FILE IS DEPRECATED


// Model for a singular data point
export interface DataPoint {
    // Date of the reading (as a timetsamp so it can be easily send as JSON)
    date: string

    // Numerical value of this data point
    value: number

    // The units for the series ("steps", "beats/minute", etc)
    unit: string
}

// Type storing a time series of data
export type DataSeries = DataPoint[]

// Type storing data for all series on a given day
export type DayData = Map<string, DataPoint[]>

// Type storing data for all series over a range of dates 
// (uses date strings as keys, so to avoid multiple instances of the same date not matching)
export type DateRangeData = Map<string, DayData>
