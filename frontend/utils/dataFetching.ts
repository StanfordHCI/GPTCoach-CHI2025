// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// This file defines helper functions for fetching featurized data from the backend
// It verifies user authentication with JWT tokens and fetches data from the backend

import axios from "axios";
import { NumericDataPoint } from "../models/NumericDataPoint";
import { BACKEND_URL } from "./config";

export async function fetchFeaturizedData(
    series: string,
    userID: string,
    date: Date,
    granularity: "day" | "week" | "month"
): Promise<NumericDataPoint[]> {

    // Retrieve the stored token
    const token = localStorage.getItem('token');
    if (!token) {
        console.error("JWT token is not available. Please login.");
        return [];
    }

    console.log(`Fetching featurized data for ${series} series, user ${userID}, date ${date.toISOString()}, granularity ${granularity}`);

    // Use backend endpoint to fetch user data for a specified time interval
    try {
        const response = await axios.get(`${BACKEND_URL}/data/`, {
            // headers: {
            //     // Include the JWT token in the Authorization header
            //     'Authorization': `Bearer ${token}`,
            // },
            params: {
                series: series,
                user_id: userID,
                date: date.toISOString(), // Ensure the date is in a proper format
                granularity: granularity,
            },
        });

        console.log("Fetched data:", response.data)

        // Convert and return the data in the required format
        return response.data.map((dataPoint: any) => ({
            date: new Date(dataPoint.start),
            value: dataPoint.value,
            maximum: dataPoint.maximum,
            minimum: dataPoint.minimum,
        } as NumericDataPoint));
    } catch (error) {
        console.error("Failed to fetch featurized data:", error);
        return [];
    }
}
