// SPDX-FileCopyrightText: 2025 Stanford University
//
// SPDX-License-Identifier: MIT

import { useEffect, useState } from "react";
import { ActionIcon, Center, Group, Text, Paper, SegmentedControl, Skeleton, Space, Title, Tooltip, useMantineTheme } from "@mantine/core";

import { VisualizationParams } from "../../../models/VisualizationParams";
import { ParentSize } from "@visx/responsive";
import VisualizationRate from "./VisualizationRate";
import VisualizationCount from "./VisualizationCount";
import { IconChevronLeft, IconChevronRight } from "@tabler/icons-react";
import moment from "moment";
import { NumericDataPoint } from "../../../models/NumericDataPoint";
import { fetchFeaturizedData } from "../../../utils/dataFetching";

interface VisualizationWrapperProps {
    params: VisualizationParams
}

const DATA_SOURCE_NAMES: { [key: string]: string } = {
    "health.activeenergyburned": "Active Energy Burned",
    "health.appleexercisetime": "Exercise Time",
    "health.applestandtime": "Stand Time",
    "health.basalenergyburned": "Basal Energy Burned",
    "health.distancewalkingrunning": "Distance Walking/Running",
    "health.flightsclimbed": "Flights Climbed",
    "health.heartrate": "Heart Rate",
    "health.heartratevariabilitysdnn": "Heart Rate Variability",
    "health.oxygensaturation": "Oxygen Saturation",
    "health.respiratoryrate": "Respiratory Rate",
    "health.restingheartrate": "Resting Heart Rate",
    "health.stepcount": "Step Count",
    "health.walkingheartrateaverage": "Walking Heart Rate Average",
};

export default function VisualizationWrapper({ params }: VisualizationWrapperProps) {
    // Use mantine theme for colors
    const mantineTheme = useMantineTheme()

    // Currently selected date
    const [date, setDate] = useState<Date>(moment(params.date).toDate())
    const [granularity, setGranularity] = useState<"day" | "week" | "month">(params.granularity)

    const [loading, setLoading] = useState<boolean>(true);

    // Store actual data, as well as average and total (which will update when data changes)
    const [data, setData] = useState<NumericDataPoint[]>([]);
    const [average, setAverage] = useState<number | undefined>();
    const [total, setTotal] = useState<number | undefined>();

    useEffect(() => {
        // Fetch data from backend on load
        setLoading(true)

        fetchFeaturizedData(
            params.source_name, params.user_id, date, granularity
        )
            .then(data => {
                console.log("featurized data:", data)
                setData(data)
                setLoading(false)
            })
            .catch(error => console.error(error))

    }, [params, date, granularity]);

    // Compute average and total when data changes
    useEffect(() => {
        let sum = 0;
        data.forEach((element) => sum += element.value ?? 0);
        setTotal(sum);

        let numNonNullPoints = data.filter((element) => element.value != null).length
        setAverage(sum / numNonNullPoints);
    }, [data])

    const getTitle = (s: string) => {
        // map source name to title using DATA_SOURCE_NAMES
        return DATA_SOURCE_NAMES[s] ?? s
    }

    // Format a number nicely (keep integers as they are, round decimals)
    const formatNumber = (n: number | undefined) => {
        return n?.toLocaleString(undefined, {maximumFractionDigits: 2}) ?? "???"
    }

    return (

        <Paper
            p="xs"
            my="0.5rem"
            px="1rem"
            bg={"white"}
            withBorder={true}
            radius='lg'

            mr={0}
            ml={0}
        >
            {/*Title*/}
            <Group
                style={{ paddingBottom: "1em" }}
            >
                <Title>{getTitle(params.source_name)}</Title>

                <Space style={{ flexGrow: 1 }} />

                <SegmentedControl
                    data={[
                        { label: "Day", value: "day" },
                        { label: "Week", value: "week" },
                        { label: "Month", value: "month" }
                    ]}
                    value={granularity}
                    onChange={(newValue: string) => setGranularity(newValue as "day" | "week" | "month")}
                    mr="1em"
                />
            </Group>


            {/*Date Selector*/}
            <Group>
                <Tooltip withArrow label={`-1 ${granularity}`}>
                    <ActionIcon
                        onClick={() => setDate(moment(date).subtract(1, granularity).toDate())}
                        variant="light" 
                        color="gray"
                    >
                        <IconChevronLeft />
                    </ActionIcon>
                </Tooltip>

                <Center miw="12em">
                    <Title order={3}>
                        {granularity == "day" ?
                            moment(date).format("ddd, MMM Do")
                            : granularity == "week" ?
                                moment(date).startOf("week").format("MMM Do") + " - " + moment(date).endOf("week").format("MMM Do")
                                :
                                moment(date).format("MMMM YYYY")
                        }
                    </Title>
                </Center>

                <Tooltip withArrow label={`+1 ${granularity}`}>
                    <ActionIcon
                        onClick={() => setDate(moment(date).add(1, granularity).toDate())}
                        disabled={moment(date).endOf(granularity) > moment()}
                        variant="light" 
                        color="gray"
                    >
                        <IconChevronRight />
                    </ActionIcon>
                </Tooltip>

                <Space style={{ flexGrow: 1 }} />
                
                {/*Text showing total or average*/}
                {/* {!loading &&
                    <Title order={3} mr="1em">
                        {(params.data_type == "count" && granularity == "day" ) ? "Total: " : "Average: "}
                        <Text span color="teal">
                            {formatNumber((params.data_type == "count" && granularity == "day" ) ? total : average)}
                        </Text>
                        {" "}
                        {params.unit}
                    </Title>
                } */}
            </Group>

            {/*Actual Series (several divs to ensure correct scaling)*/}
            <Skeleton visible={loading}>
                <div style={{ position: "relative", height: 300, padding: 0 }}>
                    <ParentSize>
                        {(parent) => (
                            <div style={{ position: "absolute" }}>
                                {params.data_type == "rate" ?

                                    <VisualizationRate
                                        parentWidth={parent.width}
                                        parentHeight={parent.height}
                                        data={data}
                                        average={average}
                                        params={params}

                                        date={date}
                                        granularity={granularity}
                                    />
                                    :
                                    <VisualizationCount
                                        parentWidth={parent.width}
                                        parentHeight={parent.height}
                                        data={data}
                                        params={params}

                                        date={date}
                                        granularity={granularity}
                                    />
                                }
                            </div>
                        )
                        }
                    </ParentSize>
                </div>
            </Skeleton>
        </Paper>

    );
};
