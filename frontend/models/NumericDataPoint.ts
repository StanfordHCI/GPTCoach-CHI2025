// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// Store a data point to pass to visualizations etc

export interface NumericDataPoint {
    // Date (moment in time) and value
    date: Date
    value: number | null

    // Optional max/min values for values over a time range
    maximum: number | undefined
    minimum: number | undefined
}