// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

// Class to represent visualization info from GPT to the user
export class VisualizationParams {
    role = "assistant";

    // Name and type of the data source
    user_id: string;
    source_name: string;
    data_type: "count" | "rate" | "ordinal";
    unit: string;

    // Date is a string in YYYY-MM-DD format
    date: string;
    granularity: "day" | "week" | "month";

    constructor(
        user_id: string,
        source_name: string,
        data_type: "count" | "rate" | "ordinal",
        unit: string,
        granularity: "day" | "week" | "month",
        date: string
    ) {
        this.user_id = user_id;
        this.source_name = source_name;
        this.data_type = data_type;
        this.unit = unit;
        this.granularity = granularity;
        this.date = date;
    }
}
