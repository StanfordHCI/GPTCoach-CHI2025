// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { useMantineTheme } from "@mantine/core";
import {
    Axis,
    Grid,
    GlyphSeries,
    LineSeries,
    AreaSeries,
    Tooltip,
    XYChart,
    buildChartTheme
} from "@visx/xychart";

import { curveMonotoneX } from "@visx/curve";

import { VisualizationParams } from "../../../models/VisualizationParams";
import { NumericDataPoint } from "../../../models/NumericDataPoint";
import moment from "moment";
import { useEffect, useState } from "react";


interface VisualizationRateProps {
    parentWidth: number,
    parentHeight: number,

    data: NumericDataPoint[]
    average: number | undefined
    params: VisualizationParams

    date: Date
    granularity: "day" | "week" | "month"
}

export default function VisualizationRate({ parentWidth, parentHeight, data, average, params, date, granularity }: VisualizationRateProps) {
    // Use mantine theme for colors
    const mantineTheme = useMantineTheme()

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
            margin={{ top: 20, bottom: 20, left: 30, right: 20 }}
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
                    let datum = tooltipData?.datumByKey["dataLines"].datum

                    return datum && datum.value && (
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
                numTicks={4}
                hideAxisLine
            />

            <Grid rows={true} columns={false} numTicks={4} />

            <GlyphSeries
                dataKey="dataGlyphs"
                data={data}

                xAccessor={(d: NumericDataPoint) => d.date}
                yAccessor={(d: NumericDataPoint) => d.value}
            />

            <LineSeries
                dataKey="dataLines"
                data={data}

                curve={curveMonotoneX}

                xAccessor={(d: NumericDataPoint) => d.date}
                yAccessor={(d: NumericDataPoint) => d.value}
            />

            <AreaSeries
                dataKey="minMaxArea"
                data={data}

                curve={curveMonotoneX}
                opacity={0.2}

                lineProps={{
                    strokeWidth: 0
                }}

                xAccessor={(d: NumericDataPoint) => d.date}
                yAccessor={(d: NumericDataPoint) => d.maximum}
                y0Accessor={(d: NumericDataPoint) => d.minimum}
            />

            {/* Average */}
            {average && data && data.length > 0 &&
                <LineSeries
                    dataKey="average"
                    data={[
                        { date: data[0].date, value: average, maximum: undefined, minimum: undefined },
                        { date: data[data.length - 1].date, value: average, maximum: undefined, minimum: undefined }
                    ]}

                    strokeDasharray={8}
                    strokeWidth={2}

                    xAccessor={(d: NumericDataPoint) => d.date}
                    yAccessor={(d: NumericDataPoint) => d.value}
                />
            }

        </XYChart>

    );
};
