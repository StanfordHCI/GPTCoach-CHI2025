// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { useMantineTheme } from "@mantine/core";
import {
    Axis,
    Grid,
    BarSeries,
    AreaSeries,
    XYChart,
    Tooltip,
    buildChartTheme
} from "@visx/xychart";

import { curveStep, curveStepAfter } from "@visx/curve"
import { scaleTime } from "@visx/scale"


import { VisualizationParams } from "../../../models/VisualizationParams";
import { NumericDataPoint } from "../../../models/NumericDataPoint";
import moment from "moment";


interface VisualizationCountProps {
    parentWidth: number,
    parentHeight: number,

    data: any[]
    params: VisualizationParams

    date: Date
    granularity: "day" | "week" | "month"
}

export default function VisualizationCount({ parentWidth, parentHeight, data, params, date, granularity }: VisualizationCountProps) {
    // Use mantine theme for colors
    const mantineTheme = useMantineTheme()

    // Compute average and min/max x and y values
    let sum = 0;
    data.forEach((element) => sum += element.value);
    let average = sum / data.length;

    // Helper for formatting dates in tooltips and axis
    const formatTimestamp = (date: Date) => {
        switch (granularity) {
            case "day":
                return moment(date).format("h:mm a")
            case "week":
                return moment(date).format("ddd M/D")
            case "month":
                return moment(date).format("MMM Do")
        }
    }

    // Chart theme for styling
    let theme = buildChartTheme({
        colors: [mantineTheme.colors.teal[6]],

        // Required properties (don't actually do anything as these elements aren't rendered)
        backgroundColor: "white",
        gridColor: mantineTheme.colors.gray[4],
        gridColorDark: "white",
        tickLength: 0
    })

    return (
        <XYChart
            margin={{ top: 20, bottom: 20, left: 100, right: 60 }}
            width={parentWidth}
            height={parentHeight}
            theme={theme}

            xScale={{ type: "time" }}
            yScale={{ type: "linear" }}
        >
            <Tooltip<NumericDataPoint>
                snapTooltipToDatumX
                showVerticalCrosshair


                renderTooltip={({ tooltipData, colorScale }) => {
                    let datum = tooltipData?.nearestDatum?.datum

                    return datum && (
                        <div>
                            <div style={{ color: "black" }}>
                                {formatTimestamp(datum.date)}
                            </div>


                            <span style={{ color: mantineTheme.colors.teal[6] }}>
                                {datum.value?.toLocaleString(undefined, { maximumFractionDigits: 2 }) ?? "No Data"}
                            </span>
                            {datum.value &&
                                <span style={{ fontWeight: "normal", color: "black" }}>
                                    {' ' + params.unit}
                                </span>
                            }

                        </div>
                    )
                }}
            />
            <Axis
                orientation="bottom"
                numTicks={7}
                tickLength={3}
                tickFormat={formatTimestamp}
            />
            <Axis
                orientation="left"
                tickLength={50}
                numTicks={4}
                hideAxisLine
            />

            <Grid rows={true} columns={false} numTicks={4} />

            {/* <AreaSeries
                dataKey="data"
                data={data}

                curve={curveStep}
                opacity={0.8}

                xAccessor={d => d.date}
                yAccessor={d => d.value}
            /> */}

            <BarSeries
                dataKey="data"
                data={data}

                radius={5}
                radiusTop

                xAccessor={d => d.date}
                yAccessor={d => d.value}
            />

        </XYChart>

    );
};
